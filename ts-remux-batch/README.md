# README Review & Improved Version

Below is a more production-grade, GitHub-optimized README structure with clearer positioning, badges, architecture explanation, and operational guidance.

---

# TS Remux & Batch Converter

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![FFmpeg](https://img.shields.io/badge/ffmpeg-required-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

Reliable utilities for converting MPEG-TS (.ts) files into seek-friendly containers such as MP4 or MKV.

Designed for:

* Media servers (Jellyfin / Plex / Kodi users)
* IPTV recordings
* Broadcast captures
* Large media libraries requiring batch processing

---

## Problem Statement

Transport Stream (.ts) files are optimized for streaming and broadcast delivery. Many players exhibit:

* Poor random access seeking
* Timeline inaccuracies
* Audio desynchronization
* Metadata inconsistencies

This project solves the issue by:

1. Attempting a **lossless remux (stream copy)**.
2. Falling back to **controlled re-encoding** when necessary.
3. Providing batch processing with resume capability.

---

## Architecture Overview

The project is intentionally modular:

* `ts_converter.py`

  * Core conversion engine
  * Remux-first strategy
  * Re-encode fallback
  * Reusable as module or CLI tool

* `batch_convert.py`

  * Recursive scanner
  * Parallel execution
  * Resume support via progress.json
  * Optional dry-run mode

Dependency Model:

* Python standard library
* External dependency: ffmpeg

---

## Features

✔ Fast lossless remux (when possible)
✔ Automatic AAC bitstream correction for MP4
✔ Safe fallback re-encoding (H.264 + AAC)
✔ Recursive folder scanning
✔ Parallel processing
✔ Resume support
✔ Dry-run mode
✔ Structure-preserving output directory

---

## Requirements

* Python 3.8+
* ffmpeg installed and available in PATH

### Install FFmpeg

Linux (Debian/Ubuntu):

```
sudo apt install ffmpeg
```

macOS (Homebrew):

```
brew install ffmpeg
```

Windows:
Download from [https://ffmpeg.org](https://ffmpeg.org) and add to PATH.

Verify installation:

```
ffmpeg -version
```

---

## Installation

```
git clone https://github.com/<username>/ts-remux-batch.git
cd ts-remux-batch
```

No pip installation required.

---

## Usage

### Single File Conversion

```
python ts_converter.py input.ts -o output.mp4
```

Options:

* `--format` Target container (mp4, mkv, mov)
* `--overwrite` Replace existing output
* `--no-reencode` Disable fallback re-encode
* `--debug` Verbose logging

---

### Batch Conversion

Basic:

```
python batch_convert.py /media/library
```

With output directory + parallel workers:

```
python batch_convert.py /media/library -o /converted --workers 4
```

Dry run:

```
python batch_convert.py /media/library --dry-run
```

Resume supported automatically via `progress.json`.

---

## Performance Notes

* Remux operations are near-instant.
* Re-encoding is CPU-bound.
* Increasing `--workers` improves throughput but may saturate disk I/O.
* SSD recommended for large libraries.

---

## Safe Usage Recommendations

* Always test on a small subset first.
* Use `--dry-run` before large operations.
* Consider keeping originals until verification.

---

## Common Use Cases

* Fix IPTV recordings that won’t seek in VLC
* Normalize large TV show collections
* Prepare files for Plex / Jellyfin ingestion
* Convert broadcast captures into archive format

---

## Future Improvements

* ffprobe-based intelligent decision engine
* Hardware acceleration support (NVENC / VAAPI)
* Config file support (YAML/JSON)
* Web-based dashboard
* Automatic media server refresh hooks
* Checksum validation
* Watch-folder daemon mode

---

## Limitations

* No GUI (CLI only)
* No automatic subtitle extraction
* No container-level metadata rewriting

---

## License

MIT License

---

## Contributing

Pull requests welcome.

---

## Final Evaluation

Is the original README functional? Yes.

Is it production-polished for GitHub visibility and collaboration? Not fully.

This version improves:

* Positioning clarity
* Professional structure
* Technical transparency
* Scannability
* Contributor-readiness

If you want, I can now:

* Create a "developer-focused" README variant
* Create a "media-server user" simplified README
* Or generate a GitHub release description
