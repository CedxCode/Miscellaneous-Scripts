#!/usr/bin/env python3
"""
batch_convert.py

Recursively scan folder(s) for .ts files and convert them using ts_converter.convert_ts.

Features:
 - recursive scan
 - preserve directory structure in output directory (if provided)
 - dry-run mode
 - resume support (progress.json)
 - optional parallelism (threads)
"""

from pathlib import Path
import argparse
import logging
import json
import concurrent.futures
import sys
import time

from ts_converter import convert_ts, ConversionError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")


def find_ts_files(root_paths, recursive=True):
    files = []
    for root in root_paths:
        p = Path(root)
        if p.is_file() and p.suffix.lower() == ".ts":
            files.append(p)
        elif p.exists() and p.is_dir():
            if recursive:
                for f in p.rglob("*.ts"):
                    files.append(f)
            else:
                for f in p.glob("*.ts"):
                    files.append(f)
        else:
            logging.warning("Path not found or not accessible: %s", p)
    return sorted(files)


def compute_output_path(input_path: Path, src_root: Path, dst_root: Path, target_ext: str):
    """
    Map input file to an output path preserving subdirectory structure relative to src_root.
    If src_root is None or not provided, use input's parent as base.
    """
    if src_root and src_root.exists():
        try:
            rel = input_path.relative_to(src_root)
        except Exception:
            # fallback: use input name only
            rel = input_path.name
    else:
        rel = input_path.name

    out_name = Path(rel).with_suffix("." + target_ext.lstrip("."))
    return dst_root.joinpath(out_name)


def load_progress(progress_file: Path):
    if progress_file.exists():
        try:
            with open(progress_file, "r", encoding="utf-8") as fh:
                return set(json.load(fh))
        except Exception:
            logging.warning("Could not read progress file; starting fresh.")
            return set()
    return set()


def save_progress(progress_file: Path, done_set):
    tmp = progress_file.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(sorted(list(done_set)), fh, indent=2)
    tmp.replace(progress_file)


def worker_convert(task):
    inp, out, opts = task
    try:
        convert_ts(str(inp), str(out), container=opts["format"], reencode_on_fail=opts["reencode"], overwrite=opts["overwrite"])
        return (str(inp), True, None)
    except ConversionError as e:
        return (str(inp), False, str(e))
    except Exception as e:
        return (str(inp), False, f"Unexpected error: {e}")


def main():
    p = argparse.ArgumentParser(description="Batch convert .ts files to another container.")
    p.add_argument("paths", nargs="+", help="File(s) and/or directory(ies) to scan for .ts files.")
    p.add_argument("-o", "--outdir", default=None, help="Output directory. If omitted, converted files are placed next to originals.")
    p.add_argument("-f", "--format", default="mp4", help="Target container extension (default: mp4).")
    p.add_argument("--no-reencode", action="store_true", help="Do not re-encode on remux failure.")
    p.add_argument("--overwrite", action="store_true", help="Overwrite existing outputs.")
    p.add_argument("--dry-run", action="store_true", help="Show what would be done, do not run conversions.")
    p.add_argument("--workers", type=int, default=1, help="Number of parallel workers (default 1).")
    p.add_argument("--resume-file", default="progress.json", help="JSON file to store completed files for resume support.")
    p.add_argument("--recursive/--no-recursive", dest="recursive", default=True, help="Scan directories recursively (default: True).")
    p.add_argument("--debug", action="store_true", help="Enable debug logging.")
    args = p.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    targets = find_ts_files(args.paths, recursive=args.recursive)
    if not targets:
        logging.info("No .ts files found in given paths.")
        sys.exit(0)

    logging.info("Found %d .ts files", len(targets))

    outdir = Path(args.outdir) if args.outdir else None
    progress_file = Path(args.resume_file)
    done = load_progress(progress_file) if args.resume_file else set()

    tasks = []
    for t in targets:
        tpath = Path(t)
        if str(tpath) in done:
            logging.debug("Skipping already processed (resume): %s", tpath)
            continue

        if outdir:
            # preserve folder structure: find the first base path that contains the file
            # If multiple roots were provided, choose the one that is a parent of file
            src_root = None
            for root_candidate in args.paths:
                rc = Path(root_candidate)
                try:
                    if tpath.is_relative_to(rc):
                        src_root = rc
                        break
                except Exception:
                    # Path.is_relative_to available in Py 3.9+, fallback with try/except above
                    try:
                        tpath.relative_to(rc)
                        src_root = rc
                        break
                    except Exception:
                        continue
            src_root = src_root or Path(args.paths[0])
            outp = compute_output_path(tpath, src_root, outdir, args.format)
        else:
            outp = tpath.with_suffix("." + args.format.lstrip("."))

        tasks.append((tpath, outp, {"format": args.format, "reencode": not args.no_reencode, "overwrite": args.overwrite}))

    if args.dry_run:
        logging.info("Dry run mode. The following conversions would be performed:")
        for inp, out, _ in tasks:
            logging.info("%s -> %s", inp, out)
        sys.exit(0)

    # Execute tasks with optional parallelism
    total = len(tasks)
    done_set = set(done)
    start = time.time()

    if args.workers <= 1:
        for task in tasks:
            inp, out, opts = task
            logging.info("[%d/%d] Converting %s -> %s", len(done_set) + 1, total, inp, out)
            result = worker_convert(task)
            src_str, ok, msg = result
            if ok:
                logging.info("OK: %s", src_str)
                done_set.add(src_str)
                if args.resume_file:
                    save_progress(progress_file, done_set)
            else:
                logging.error("FAILED: %s  Reason: %s", src_str, msg)
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
            future_to_task = {ex.submit(worker_convert, t): t for t in tasks}
            completed = 0
            for fut in concurrent.futures.as_completed(future_to_task):
                completed += 1
                inp, out, _ = future_to_task[fut]
                try:
                    src_str, ok, msg = fut.result()
                except Exception as e:
                    logging.error("Task raised unexpected exception: %s", e)
                    src_str, ok, msg = str(inp), False, f"exception: {e}"

                if ok:
                    done_set.add(src_str)
                    logging.info("[%d/%d] OK: %s", completed, total, src_str)
                    if args.resume_file:
                        save_progress(progress_file, done_set)
                else:
                    logging.error("[%d/%d] FAILED: %s  Reason: %s", completed, total, src_str, msg)

    elapsed = time.time() - start
    logging.info("Batch complete. %d succeeded, %d failed. Elapsed: %.1f s", len(done_set), total - len(done_set), elapsed)
    if args.resume_file:
        save_progress(progress_file, done_set)


if __name__ == "__main__":
    main()
