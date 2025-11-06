# Video Converter

A Python script to convert videos to HD (1080p) or 2K (1440p) using FFmpeg in WSL2.

## Design for WSL2

This script is tailored for WSL2 environments to process video files stored on Windows drives. It accesses Windows files via mounted paths like `/mnt/d/`, allowing seamless conversion of large video libraries without moving files.

The source directory is hardcoded as `/mnt/d/media/google drive space cleanup/` - update this path in the script to match your Windows video folder.

## Code Vibe

The script is a straightforward, interactive tool that prioritizes user control and metadata preservation. It extracts filming timestamps from video metadata for accurate reporting, handles existing files gracefully, and provides per-file decision-making.

It's intentionally simple and hackable - feel free to fork, modify, or build your own version to suit your needs. The code encourages experimentation with FFmpeg parameters, resolution options, or additional metadata handling.

## Requirements
- Python 3
- FFmpeg

## Usage
1. Update `current_dir` in the script to your video folder.
2. Run `python3 video_converter.py`
3. Choose HD, 2K, or SKIP for each new file.

## Output
- Videos in HD/ or 2K/ subdirs.
- Report saved as `conversion_report.tsv`.