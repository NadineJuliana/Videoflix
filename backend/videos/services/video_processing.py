"""
Services for video processing.
"""

import subprocess
from pathlib import Path

HLS_RESOLUTIONS = (480, 720, 1080)


def convert_to_hls(source_path, output_dir, height):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    command = [
        "ffmpeg",
        "-i", str(source_path),
        "-vf", f"scale=-2:{height}",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-hls_time", "10",
        "-hls_playlist_type", "vod",
        "-hls_segment_filename", str(output_path / "%03d.ts"),
        "-f", "hls",
        str(output_path / "index.m3u8"),
    ]

    subprocess.run(command, check=True)


def process_video(source_path, hls_dir, thumbnail_path):
    generate_thumbnail(source_path, thumbnail_path)

    for height in HLS_RESOLUTIONS:
        resolution_dir = Path(hls_dir) / f"{height}p"
        convert_to_hls(source_path, resolution_dir, height)


def generate_thumbnail(source_path, output_path):
    thumbnail_path = Path(output_path)
    thumbnail_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "ffmpeg",
        "-i", str(source_path),
        "-ss", "00:00:01",
        "-frames:v", "1",
        "-update", "1",
        "-y",
        str(thumbnail_path),
    ]

    subprocess.run(command, check=True)
