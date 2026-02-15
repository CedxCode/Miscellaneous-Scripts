# Miscellaneous Scripts

A personal collection of practical scripts used or modified to automate recurring tasks.

This repository is not a framework or a polished product suite. It is a working toolbox: scripts that solve real problems, refined over time as needs evolve.

---

## Purpose

This repository exists to:

* Centralize useful automation scripts
* Avoid rewriting the same utilities repeatedly
* Keep improved versions of modified scripts
* Provide quick reuse across systems or projects

Most scripts are task-driven rather than generic libraries.

---

## Philosophy

* Practical over perfect
* Minimal dependencies
* Clear CLI usage
* Easy to copy and adapt
* Modular folder structure

If a script works reliably and solves the problem, it belongs here.

---

## Current Contents

### 📁 ts-remux-batch

Utilities for converting MPEG-TS (`.ts`) files into more seek-friendly containers such as `.mp4` or `.mkv`.

Typical use case:

* Fix playback/seek issues in recorded or downloaded `.ts` files
* Batch normalize media files for media servers
* Preserve quality via remux when possible

Features:

* Fast lossless remux (stream copy)
* Re-encode fallback when necessary
* Recursive folder scanning
* Resume support
* Parallel processing

See detailed usage in:

```
ts-remux-batch/README.md
```

---

## Repository Structure

```
Miscellaneous-Scripts/
│
├── ts-remux-batch/
│   ├── ts_converter.py
│   ├── batch_convert.py
│   └── README.md
│
└── (other automation scripts...)
```

Each folder is self-contained and includes its own documentation.

---

## Requirements

Most scripts rely on:

* Python 3.8+

Some may require external tools (e.g., `ffmpeg`). Requirements are documented inside each folder.

---

## How to Use

Clone the repository and navigate to the relevant script folder:

```
git clone https://github.com/<username>/Miscellaneous-Scripts.git
cd Miscellaneous-Scripts/<script-folder>
```

Read that folder's README for usage details.

---

## Notes

* Scripts may evolve over time.
* Interfaces may change if improvements are made.
* This repository is primarily maintained for personal automation needs.

---

## Suggested GitHub Repository Description

Short version:

"Personal collection of practical Python automation scripts and utilities."

Alternative:

"Utility scripts used for task automation, media processing, and system workflows."
