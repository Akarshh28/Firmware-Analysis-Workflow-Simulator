"""
entropy_analysis.py - Shannon entropy scan (Phase 2, Step A of the roadmap).

Uses scipy for the entropy calculation as specified in the project roadmap.
Slides a fixed-size window across the file and flags any run of
consecutive high-entropy windows as a likely compressed/encrypted region.
"""

import os
import numpy as np
from scipy.stats import entropy as scipy_entropy

from config import (
    ENTROPY_WINDOW_SIZE, ENTROPY_HIGH_THRESHOLD, ENTROPY_MIN_RUN_WINDOWS,
    MAX_FILE_SIZE_FOR_ENTROPY,
)


def shannon_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = np.bincount(np.frombuffer(data, dtype=np.uint8), minlength=256)
    probs = counts / counts.sum()
    probs = probs[probs > 0]
    return float(scipy_entropy(probs, base=2))


def analyze_entropy(path: str):
    """
    Returns a dict:
        {
          "success": bool,
          "error": str or None,
          "windows_scanned": int,
          "flagged_regions": [ {"start_offset": int, "end_offset": int, "avg_entropy": float}, ... ],
          "verdict": "clean" | "possible_compression_or_encryption" | "not_analyzed"
        }
    Never raises - all failure modes come back as success=False with a reason.
    """
    result = {
        "success": False,
        "error": None,
        "windows_scanned": 0,
        "flagged_regions": [],
        "verdict": "not_analyzed",
    }

    if not os.path.isfile(path):
        result["error"] = "file does not exist"
        return result

    size = os.path.getsize(path)
    if size == 0:
        result["error"] = "file is empty (0 bytes)"
        return result
    if size > MAX_FILE_SIZE_FOR_ENTROPY:
        result["error"] = f"file too large for entropy scan ({size} bytes > {MAX_FILE_SIZE_FOR_ENTROPY} cap)"
        return result

    try:
        window_entropies = []
        with open(path, "rb") as f:
            offset = 0
            while True:
                chunk = f.read(ENTROPY_WINDOW_SIZE)
                if not chunk:
                    break
                window_entropies.append((offset, shannon_entropy(chunk)))
                offset += len(chunk)
    except PermissionError:
        result["error"] = "permission denied reading file"
        return result
    except OSError as e:
        result["error"] = f"OS error while reading file: {e}"
        return result
    except Exception as e:
        result["error"] = f"unexpected error during entropy scan: {e}"
        return result

    result["windows_scanned"] = len(window_entropies)

    # Find consecutive runs of high-entropy windows
    run_start = None
    run_vals = []
    flagged = []
    for offset, ent in window_entropies:
        if ent >= ENTROPY_HIGH_THRESHOLD:
            if run_start is None:
                run_start = offset
            run_vals.append(ent)
        else:
            if run_start is not None and len(run_vals) >= ENTROPY_MIN_RUN_WINDOWS:
                flagged.append({
                    "start_offset": run_start,
                    "end_offset": offset,
                    "avg_entropy": round(sum(run_vals) / len(run_vals), 3),
                })
            run_start = None
            run_vals = []
    # tail run
    if run_start is not None and len(run_vals) >= ENTROPY_MIN_RUN_WINDOWS:
        flagged.append({
            "start_offset": run_start,
            "end_offset": window_entropies[-1][0] + ENTROPY_WINDOW_SIZE,
            "avg_entropy": round(sum(run_vals) / len(run_vals), 3),
        })

    result["flagged_regions"] = flagged
    result["success"] = True
    result["verdict"] = "possible_compression_or_encryption" if flagged else "clean"
    return result
