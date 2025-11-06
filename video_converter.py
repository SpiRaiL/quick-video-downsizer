import os
import subprocess
from datetime import datetime
import json

# Check if ffmpeg is available
try:
    subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
except (subprocess.CalledProcessError, FileNotFoundError):
    print("FFmpeg is not installed or not in PATH. Please download FFmpeg from https://ffmpeg.org/download.html, extract it, and add the bin folder to your PATH environment variable.")
    exit(1)

# Define video extensions
video_exts = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm']

# Get current directory
current_dir = '/mnt/d/media/google drive space cleanup/'

# Function to format file size
def format_size(size_bytes):
    return f"{size_bytes / (1024**2):.2f} MB"

# List to collect report data
report = []

for file in os.listdir(current_dir):
    if os.path.isfile(os.path.join(current_dir, file)):
        _, ext = os.path.splitext(file)
        if ext.lower() in video_exts:
            input_file = os.path.join(current_dir, file)
            input_size = os.path.getsize(input_file)
            input_mtime = os.path.getmtime(input_file)
            # Get filming timestamp from video metadata
            try:
                result = subprocess.run(['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', input_file], capture_output=True, text=True, check=True)
                metadata = json.loads(result.stdout)
                creation_time_str = metadata.get('format', {}).get('tags', {}).get('creation_time')
                if creation_time_str:
                    dt = datetime.fromisoformat(creation_time_str.replace('Z', '+00:00'))
                    timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    timestamp = datetime.fromtimestamp(input_mtime).strftime('%Y-%m-%d %H:%M:%S')
            except:
                timestamp = datetime.fromtimestamp(input_mtime).strftime('%Y-%m-%d %H:%M:%S')

            # Check for existing output in HD or 2K
            hd_output = os.path.join(current_dir, 'HD', file)
            k2_output = os.path.join(current_dir, '2K', file)
            if os.path.exists(hd_output):
                output_file = hd_output
                output_size = os.path.getsize(output_file)
                status = 'exists'
                print(f"Skipping {file}, output already exists in HD.")
                report.append({'file': file, 'input_size': input_size, 'output_size': output_size, 'status': status, 'timestamp': timestamp})
                continue
            elif os.path.exists(k2_output):
                output_file = k2_output
                output_size = os.path.getsize(output_file)
                status = 'exists'
                print(f"Skipping {file}, output already exists in 2K.")
                report.append({'file': file, 'input_size': input_size, 'output_size': output_size, 'status': status, 'timestamp': timestamp})
                continue
            else:
                # Ask for resolution
                print(f"Processing {file} ({format_size(input_size)})")
                choice = input("Choose resolution: HD (1080p), 2K (1440p), or SKIP? ").strip().upper()
                if choice == 'HD':
                    resolution = 'HD'
                    scale = '1920:1080'
                elif choice == '2K':
                    resolution = '2K'
                    scale = '2560:1440'
                elif choice == 'SKIP':
                    status = 'skipped'
                    print(f"Skipping {file}.")
                    report.append({'file': file, 'input_size': input_size, 'output_size': 0, 'status': status, 'timestamp': timestamp})
                    continue
                else:
                    print(f"Invalid choice for {file}, skipping.")
                    status = 'skipped'
                    report.append({'file': file, 'input_size': input_size, 'output_size': 0, 'status': status, 'timestamp': timestamp})
                    continue

                output_folder = os.path.join(current_dir, resolution)
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                output_file = os.path.join(output_folder, file)

                # ffmpeg command
                cmd = [
                    'ffmpeg',
                    '-i', input_file,
                    '-map_metadata', '0',
                    '-vf', f'scale={scale}:force_original_aspect_ratio=decrease,pad={scale}:(ow-iw)/2:(oh-ih)/2',
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    output_file
                ]
                try:
                    subprocess.run(cmd, check=True)
                    # Preserve file modification time
                    os.utime(output_file, (os.path.getatime(output_file), input_mtime))
                    output_size = os.path.getsize(output_file)
                    status = 'converted'
                    print(f"Converted {file} to {output_file}")
                    report.append({'file': file, 'input_size': input_size, 'output_size': output_size, 'status': status, 'timestamp': timestamp})
                except subprocess.CalledProcessError as e:
                    print(f"Error converting {file}: {e}")
                    # For errors, add with status error or something
                    report.append({'file': file, 'input_size': input_size, 'output_size': 0, 'status': 'error', 'timestamp': timestamp})

# Print the report
print("\nConversion Report:")
print(f"{'Timestamp':<20} {'Input Size':<15} {'Output Size':<15} {'Status':<10} {'File'}")
print("-" * 110)
for item in report:
    print(f"{item['timestamp']:<20} {format_size(item['input_size']):<15} {format_size(item['output_size']):<15} {item['status']:<10} {item['file']}")

# Write report to TSV file
project_dir = os.path.dirname(os.path.abspath(__file__))
report_file = os.path.join(project_dir, 'conversion_report.tsv')
with open(report_file, 'w') as f:
    f.write("Timestamp\tInput Size\tOutput Size\tStatus\tFile\n")
    for item in report:
        f.write(f"{item['timestamp']}\t{format_size(item['input_size'])}\t{format_size(item['output_size'])}\t{item['status']}\t{item['file']}\n")
print(f"\nReport saved to {report_file}")