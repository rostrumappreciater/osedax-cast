"""Convert audio files to Opus format."""
import subprocess
import os
from pathlib import Path

class OpusConverter:
    def __init__(self, output_dir: str, bitrate: str = "32k"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.bitrate = bitrate

    def convert_to_opus(self, input_path: str, episode_id: str) -> str:
        """Convert input file to Opus and return path to output file."""
        output_path = self.output_dir / f"{episode_id}.opus"
        if output_path.exists():
            return str(output_path)

        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-c:a", "libopus",
            "-b:a", self.bitrate,
            "-vbr", "on",
            "-compression_level", "10",
            "-application", "audio",
            "-frame_duration", "60",
            "-vn",  # No video
            "-y",   # Overwrite
            str(output_path)
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return str(output_path)
