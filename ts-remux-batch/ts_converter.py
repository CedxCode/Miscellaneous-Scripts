#!/usr/bin/env python3
"""
ts_converter.py

Single-file converter utilities for .ts -> other container (default: mp4).
Tries to remux with stream copy first (fast). If that fails, falls back to re-encoding.

Usage (as module):
    from ts_converter import convert_ts, ConversionError
    convert_ts("input.ts", "output.mp4")

Usage (CLI):
    python ts_converter.py input.ts -o output.mp4
"""

from pathlib import Path
import shutil
import subprocess
import argparse
import sys
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")


class ConversionError(RuntimeError):
    pass


def _ffmpeg_exists() -> bool:
    return shutil.which("ffmpeg") is not None


def _run_cmd(cmd, capture_output=False):
    logging.debug("Running command: %s", " ".join(cmd))
    try:
        if capture_output:
            completed = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return completed.returncode, completed.stdout, completed.stderr
        else:
            completed = subprocess.run(cmd)
            return completed.returncode, None, None
    except FileNotFoundError as e:
        raise ConversionError("ffmpeg not found on PATH") from e


def convert_ts(
    input_path: str,
    output_path: str,
    container: str = "mp4",
    reencode_on_fail: bool = True,
    overwrite: bool = False,
    timeout: Optional[int] = None,
) -> None:
    """
    Convert a single .ts file into another container.

    - Tries remux (stream copy) first: very fast, no quality loss.
    - If remux fails and reencode_on_fail is True, performs a re-encode.

    Parameters:
        input_path: path to .ts file
        output_path: path to resulting file (should include extension matching container)
        container: output container extension (mp4, mkv, mov, etc.)
        reencode_on_fail: whether to re-encode if remux fails
        overwrite: if True, overwrite existing output
        timeout: optional seconds to allow ffmpeg to run (applies to subprocess.run)
    Raises:
        ConversionError on failure
    """
    if not _ffmpeg_exists():
        raise ConversionError("ffmpeg is required but not found in PATH. Install ffmpeg and retry.")

    src = Path(input_path)
    if not src.exists():
        raise ConversionError(f"Input file does not exist: {input_path}")

    out = Path(output_path)
    if out.exists() and not overwrite:
        raise ConversionError(f"Output file already exists (use overwrite=True to replace): {output_path}")

    out.parent.mkdir(parents=True, exist_ok=True)

    # Try fast remux (stream copy).
    # For MP4 containers we often need to convert ADTS AAC to mp4 format using a bitstream filter.
    remux_cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y" if overwrite else "-n",
        "-i",
        str(src),
        "-c",
        "copy",
    ]

    # If target is mp4, add AAC ADTS to ASC bitstream filter which is commonly needed
    if container.lower() in {"mp4", "mov"}:
        remux_cmd += ["-bsf:a", "aac_adtstoasc"]

    remux_cmd.append(str(out))

    logging.info("Attempting fast remux (stream copy): %s -> %s", src, out)
    rc, _, stderr = _run_cmd(remux_cmd, capture_output=True)
    if rc == 0:
        logging.info("Remux succeeded: %s", out)
        return

    logging.warning("Remux failed (ffmpeg returned %d). stderr:\n%s", rc, stderr.strip() if stderr else "(no stderr)")

    if not reencode_on_fail:
        raise ConversionError("Remux failed and reencode_on_fail is False. See ffmpeg stderr above.")

    # Fallback: re-encode video/audio to known codecs. This is slower and lossy
    logging.info("Falling back to re-encode. This may take longer and change file size/quality.")
    # Use reasonable defaults: H.264 for video, AAC for audio
    reencode_cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y" if overwrite else "-n",
        "-i",
        str(src),
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "20",  # quality: lower=better (range ~18-23 is typical)
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        str(out),
    ]

    rc2, _, stderr2 = _run_cmd(reencode_cmd, capture_output=True)
    if rc2 != 0:
        logging.error("Re-encode failed. stderr:\n%s", stderr2.strip() if stderr2 else "(no stderr)")
        raise ConversionError(f"Both remux and re-encode failed for {input_path}")

    logging.info("Re-encode succeeded: %s", out)


# --- CLI support ---
def _parse_args():
    p = argparse.ArgumentParser(description="Convert .ts file to another container (remux first, re-encode fallback).")
    p.add_argument("input", help="Input .ts file")
    p.add_argument("-o", "--output", help="Output file path. If omitted, same name with new extension is used.")
    p.add_argument("-f", "--format", default="mp4", help="Target container/extension (mp4, mkv). Default: mp4")
    p.add_argument("--no-reencode", action="store_true", help="Do not attempt re-encoding if remux fails.")
    p.add_argument("--overwrite", action="store_true", help="Overwrite existing output file.")
    p.add_argument("--debug", action="store_true", help="Enable debug logging.")
    return p.parse_args()


def _cli_main():
    args = _parse_args()
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    inp = Path(args.input)
    if not inp.exists():
        logging.error("Input not found: %s", inp)
        sys.exit(2)

    if args.output:
        out = Path(args.output)
    else:
        out = inp.with_suffix("." + args.format.lstrip("."))

    try:
        convert_ts(
            str(inp),
            str(out),
            container=args.format,
            reencode_on_fail=not args.no_reencode,
            overwrite=args.overwrite,
        )
    except ConversionError as e:
        logging.error("Conversion failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    _cli_main()
