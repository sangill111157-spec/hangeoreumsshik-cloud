#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step3_local_auto_builder.py
RGON local patch auto-builder (Python standard library only)

What it does
  1. clean_and_verify_py(): reads omni_*.py from shin-agent and its parent (Downloads), strips a leading or
     trailing "Copy" line and markdown code fences, then checks the syntax with compile(source, filename, "exec").
     Files with syntax errors are never used.
  2. Finds the NEWEST omni_claude_*.py for step 1 and step 2 (module name + completion marker must both be in
     the file), saves each cleaned to shin-agent/<step>.py and runs it with the current Python interpreter
     (-X utf8, timeout 180s).
     The patches are applied in the order step1 -> step2.
  3. Moves the *.bak* files the patches leave behind into backups/step_builder_<timestamp>/.
  4. --once (default) applies pending patches one time. --watch polls every 2 seconds
     (omni_*.py and omni_dispatch_queue.json) and repeats syntax check -> backup -> apply -> snapshot update.
  5. Writes brain_basket/auto_builder_receipt.json and syncs the version "v6.0.8" and the latest time into
     rgon_brain_snapshot.json (root, dashboard/, docs/).

Safety
  - A file is run only if it is syntactically valid, contains the exact step module name AND that step's
    completion marker, and is not ambiguous (matching both steps) or this builder itself.
  - A patch whose content hash is already recorded as applied is not run again (use --force to override).
  - The existing step file is backed up before it is overwritten. Nothing is deleted.

Usage:
  python step3_local_auto_builder.py                 # same as --once
  python step3_local_auto_builder.py --once
  python step3_local_auto_builder.py --watch [--interval 2]
  python step3_local_auto_builder.py --force | --dry-run | --root <dir>
"""
import os
import re
import sys
import json
import glob
import time
import shutil
import hashlib
import argparse
import subprocess
from datetime import datetime, timezone, timedelta

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

DEFAULT_ROOT = r"C:\Users\sangi\Downloads\shin-agent"
VERSION_TAG = "v6.0.8"
SNAPSHOT_NAME = "rgon_brain_snapshot.json"
RECEIPT_REL = os.path.join("brain_basket", "auto_builder_receipt.json")
QUEUE_NAME = "omni_dispatch_queue.json"
RUN_TIMEOUT = 180
HISTORY_MAX = 20

# The completion markers are built from pieces on purpose, so that this file never contains the exact marker
# text of the other step scripts and can never be mistaken for one of them.
STEPS = [
    {
        "key": "step1",
        "module": "step1_ui_rgon_and_badge",
        "marker": "[STEP " + "1 UI PATCH COMPLETE]",
        "dest": "step1_ui_rgon_and_badge.py",
        "arg": lambda root: os.path.join(root, "rgon_aside_extension"),
    },
    {
        "key": "step2",
        "module": "step2_mobile_clean_layout",
        "marker": "[STEP " + "2 MOBILE CLEAN LAYOUT COMPLETE]",
        "dest": "step2_mobile_clean_layout.py",
        "arg": lambda root: root,
    },
]

FENCE_RE = re.compile(r"^\s*`{3,}\s*[A-Za-z0-9_+\-]*\s*$")
JUNK_WORDS = ("copy", "python copy", "pythoncopy", "copy code")


# ---------------------------------------------------------------------------
# small utilities
# ---------------------------------------------------------------------------
def info(msg=""):
    print(msg, flush=True)


def kst_now():
    return datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S KST")


def stamp():
    return time.strftime("%Y%m%d_%H%M%S")


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_json(path, default=None):
    try:
        with open(path, "rb") as f:
            return json.loads(f.read().decode("utf-8-sig"))
    except Exception:
        return default


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")
    os.replace(tmp, path)


def read_source(path):
    with open(path, "rb") as f:
        raw = f.read()
    for enc in ("utf-8-sig", "cp949"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("utf-8/cp949", raw, 0, 1, "cannot decode file")


def safe_mtime(path):
    try:
        return os.path.getmtime(path)
    except OSError:
        return 0.0


# ---------------------------------------------------------------------------
# 1) clean + syntax verification
# ---------------------------------------------------------------------------
def _is_junk(line):
    s = line.strip()
    return s == "" or s.lower() in JUNK_WORDS or bool(FENCE_RE.match(line))


def clean_source(text):
    """Strip leading/trailing 'Copy' lines and markdown fences. Returns (cleaned_text, changed)."""
    norm = text.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff")
    lines = norm.split("\n")
    while lines:
        if _is_junk(lines[0]):
            lines.pop(0)
            continue
        if (len(lines) > 1 and lines[0].strip().lower() == "python"
                and lines[1].strip().lower() in ("copy", "copy code")):
            del lines[0:2]
            continue
        break
    while lines and _is_junk(lines[-1]):
        lines.pop()
    cleaned = "\n".join(lines) + "\n" if lines else ""
    changed = cleaned.strip() != norm.strip()
    return cleaned, changed


def clean_and_verify_py(path):
    """Read, clean and syntax-check a python file. Never executes it."""
    res = {"path": path, "ok": False, "text": "", "cleaned": False, "error": None}
    try:
        raw_text = read_source(path)
    except Exception as e:
        res["error"] = "read error: %s" % e
        return res
    text, changed = clean_source(raw_text)
    res["text"] = text
    res["cleaned"] = changed
    if not text.strip():
        res["error"] = "empty after cleaning"
        return res
    try:
        compile(text, path, "exec", dont_inherit=True)
    except SyntaxError as e:
        res["error"] = "SyntaxError: %s (line %s)" % (e.msg, e.lineno)
        return res
    except (ValueError, MemoryError, RecursionError) as e:
        res["error"] = "%s: %s" % (type(e).__name__, e)
        return res
    res["ok"] = True
    return res


# ---------------------------------------------------------------------------
# discovery
# ---------------------------------------------------------------------------
def search_dirs(root):
    dirs = [root]
    parent = os.path.dirname(os.path.abspath(root))
    if parent and os.path.normcase(parent) != os.path.normcase(os.path.abspath(root)):
        dirs.append(parent)
    return dirs


def list_files(dirs, pattern):
    seen, out = set(), []
    for d in dirs:
        for p in glob.glob(os.path.join(d, pattern)):
            if not os.path.isfile(p):
                continue
            key = os.path.normcase(os.path.abspath(p))
            if key in seen:
                continue
            seen.add(key)
            out.append(p)
    return out


def queue_paths(root):
    paths = [os.path.join(root, QUEUE_NAME),
             os.path.join(root, "brain_basket", QUEUE_NAME),
             os.path.join(os.path.dirname(os.path.abspath(root)), QUEUE_NAME)]
    seen, out = set(), []
    for p in paths:
        k = os.path.normcase(os.path.abspath(p))
        if k not in seen:
            seen.add(k)
            out.append(p)
    return out


def read_queue_summary(root):
    files = []
    for p in queue_paths(root):
        if not os.path.isfile(p):
            continue
        data = load_json(p, None)
        n = None
        if isinstance(data, list):
            n = len(data)
        elif isinstance(data, dict):
            for k in ("items", "queue", "jobs", "tasks"):
                if isinstance(data.get(k), list):
                    n = len(data[k])
                    break
            if n is None:
                n = len(data)
        files.append({"path": p, "entries": n,
                      "mtime": datetime.fromtimestamp(safe_mtime(p)).strftime("%Y-%m-%d %H:%M:%S")})
    return {"files": files}


def signature(root):
    sig = {}
    paths = list_files(search_dirs(root), "omni_*.py") + [p for p in queue_paths(root) if os.path.isfile(p)]
    for p in paths:
        try:
            st = os.stat(p)
            sig[os.path.normcase(os.path.abspath(p))] = (st.st_mtime_ns, st.st_size)
        except OSError:
            pass
    return sig


def scan_and_pick(root):
    """Verify every omni_*.py and pick the newest omni_claude_*.py per step."""
    dirs = search_dirs(root)
    omni_files = sorted(list_files(dirs, "omni_*.py"), key=safe_mtime, reverse=True)
    scanned, cache = [], {}
    for p in omni_files:
        r = clean_and_verify_py(p)
        cache[os.path.normcase(os.path.abspath(p))] = r
        scanned.append({"path": p, "ok": r["ok"], "cleaned": r["cleaned"], "error": r["error"]})
    picks = {s["key"]: None for s in STEPS}
    for p in omni_files:
        if not re.match(r"^omni_claude_.*\.py$", os.path.basename(p), re.I):
            continue
        r = cache[os.path.normcase(os.path.abspath(p))]
        if not r["ok"]:
            continue
        t = r["text"]
        if "step3_local_auto_builder" in t:
            continue
        matches = [s for s in STEPS if s["module"] in t and s["marker"] in t]
        if len(matches) != 1:
            continue
        key = matches[0]["key"]
        if picks[key] is None:
            r["origin"] = "omni"
            picks[key] = r
    for s in STEPS:
        if picks[s["key"]] is None:
            dest = os.path.join(root, s["dest"])
            if os.path.isfile(dest):
                r = clean_and_verify_py(dest)
                if r["ok"] and s["marker"] in r["text"]:
                    r["origin"] = "existing-root-file"
                    picks[s["key"]] = r
    return scanned, picks


# ---------------------------------------------------------------------------
# apply a step
# ---------------------------------------------------------------------------
def apply_step(step, cand, root, applied, force, dry, bak_stamp):
    rec = {
        "step": step["key"], "module": step["module"], "source": None, "origin": None,
        "sha256": None, "status": "not-found", "returncode": None,
        "stdout_tail": "", "stderr_tail": "", "elapsed_sec": None,
    }
    if cand is None:
        info("   [%s] no matching omni_claude_*.py found (and no usable %s)" % (step["key"], step["dest"]))
        return rec
    text = cand["text"]
    sha = sha256_text(text)
    rec.update({"source": cand["path"], "origin": cand.get("origin"), "sha256": sha})
    if not force and applied.get(step["key"]) == sha:
        rec["status"] = "already-applied"
        info("   [%s] already applied (same content hash), skipped" % step["key"])
        return rec
    if dry:
        rec["status"] = "dry-run"
        info("   [%s] dry-run: would apply %s" % (step["key"], cand["path"]))
        return rec

    dest = os.path.join(root, step["dest"])
    try:
        if os.path.isfile(dest):
            same = False
            try:
                same = (sha256_text(clean_source(read_source(dest))[0]) == sha)
            except Exception:
                pass
            if not same:
                prev = os.path.join(root, "backups", "step_builder_" + bak_stamp, "prev_" + step["dest"])
                os.makedirs(os.path.dirname(prev), exist_ok=True)
                shutil.copy2(dest, prev)
        with open(dest, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    except Exception as e:
        rec["status"] = "failed"
        rec["stderr_tail"] = "write error: %s" % e
        info("   [%s] FAILED to save %s : %s" % (step["key"], dest, e))
        return rec

    check = clean_and_verify_py(dest)
    if not check["ok"]:
        rec["status"] = "failed"
        rec["stderr_tail"] = "post-save syntax check failed: %s" % check["error"]
        info("   [%s] FAILED post-save syntax check: %s" % (step["key"], check["error"]))
        return rec

    ext_arg = step["arg"](root)
    cmd = [sys.executable, "-X", "utf8", dest, ext_arg]
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    info("   [%s] running %s" % (step["key"], step["dest"]))
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=root, env=env, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=RUN_TIMEOUT)
        rec["returncode"] = p.returncode
        rec["stdout_tail"] = (p.stdout or "")[-3000:]
        rec["stderr_tail"] = (p.stderr or "")[-1500:]
        if p.returncode == 0 and step["marker"] in (p.stdout or ""):
            rec["status"] = "applied"
            applied[step["key"]] = sha
            info("   [%s] OK (%s)" % (step["key"], step["marker"]))
        else:
            rec["status"] = "failed"
            info("   [%s] FAILED (returncode=%s, completion marker %s)" % (
                step["key"], p.returncode, "found" if step["marker"] in (p.stdout or "") else "missing"))
    except subprocess.TimeoutExpired:
        rec["status"] = "failed"
        rec["stderr_tail"] = "timeout after %d seconds" % RUN_TIMEOUT
        info("   [%s] FAILED: timeout (%ds)" % (step["key"], RUN_TIMEOUT))
    except Exception as e:
        rec["status"] = "failed"
        rec["stderr_tail"] = "run error: %s" % e
        info("   [%s] FAILED: %s" % (step["key"], e))
    rec["elapsed_sec"] = round(time.time() - t0, 2)
    return rec


# ---------------------------------------------------------------------------
# backup tidy + snapshots
# ---------------------------------------------------------------------------
def tidy_backups(root, bak_stamp):
    moved = []
    dirs = [root] + [os.path.join(root, d) for d in ("rgon_aside_extension", "dashboard", "docs")]
    base = os.path.join(root, "backups", "step_builder_" + bak_stamp)
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for p in glob.glob(os.path.join(d, "*.bak*")):
            if not os.path.isfile(p):
                continue
            rel = os.path.relpath(p, root)
            target = os.path.join(base, rel)
            try:
                os.makedirs(os.path.dirname(target), exist_ok=True)
                n = 1
                final = target
                while os.path.exists(final):
                    final = "%s.%d" % (target, n)
                    n += 1
                shutil.move(p, final)
                moved.append({"from": rel, "to": os.path.relpath(final, root)})
            except Exception as e:
                info("   [warn] could not move %s : %s" % (rel, e))
    return moved


def sync_snapshots(root, now, brief):
    targets = [("root", root), ("dashboard", os.path.join(root, "dashboard")), ("docs", os.path.join(root, "docs"))]
    existing = {}
    for name, d in targets:
        p = os.path.join(d, SNAPSHOT_NAME)
        if os.path.isfile(p):
            data = load_json(p, None)
            if isinstance(data, dict):
                existing[name] = data
    base = existing.get("root") or (next(iter(existing.values())) if existing else {"schema": "rgon_brain_snapshot/1"})
    written = []
    for name, d in targets:
        if name != "root" and not os.path.isdir(d):
            continue
        data = dict(existing.get(name) or base)
        data["version"] = VERSION_TAG
        data["generated_at_kst"] = now
        data["synced_at_kst"] = now
        data["auto_builder"] = brief
        try:
            write_json(os.path.join(d, SNAPSHOT_NAME), data)
            written.append(os.path.relpath(os.path.join(d, SNAPSHOT_NAME), root))
        except Exception as e:
            info("   [warn] snapshot write failed (%s): %s" % (name, e))
    return written


# ---------------------------------------------------------------------------
# one build cycle
# ---------------------------------------------------------------------------
def run_cycle(args, trigger):
    root = args.root
    started = kst_now()
    bak_stamp = stamp()
    receipt_path = os.path.join(root, RECEIPT_REL)
    prev = load_json(receipt_path, {}) or {}
    applied = dict(prev.get("applied") or {})
    history = list(prev.get("history") or [])

    info("")
    info("-" * 64)
    info("[cycle] %s | trigger=%s | root=%s" % (started, trigger, root))

    scanned, picks = scan_and_pick(root)
    bad = [s for s in scanned if not s["ok"]]
    info("   scanned omni_*.py: %d (syntax errors: %d)" % (len(scanned), len(bad)))
    for s in scanned:
        tag = "OK " if s["ok"] else "ERR"
        extra = " (cleaned: Copy/fence removed)" if s["cleaned"] else ""
        info("      [%s] %s%s%s" % (tag, s["path"], extra, "" if s["ok"] else "  -> " + str(s["error"])))

    steps = []
    for step in STEPS:
        steps.append(apply_step(step, picks.get(step["key"]), root, applied, args.force, args.dry_run, bak_stamp))

    ran_any = any(s["status"] in ("applied", "failed") for s in steps)
    moved = []
    if ran_any and not args.dry_run:
        moved = tidy_backups(root, bak_stamp)
        info("   backups moved to backups/step_builder_%s : %d file(s)" % (bak_stamp, len(moved)))

    ok = not any(s["status"] == "failed" for s in steps)
    finished = kst_now()
    brief = {
        "last_run_kst": finished,
        "trigger": trigger,
        "ok": ok,
        "steps": {s["step"]: s["status"] for s in steps},
    }

    snapshots = []
    if not args.dry_run:
        snapshots = sync_snapshots(root, finished, brief)
        info("   snapshot version -> %s : %s" % (VERSION_TAG, ", ".join(snapshots) or "none"))

    summary = {"time": finished, "trigger": trigger, "ok": ok, "steps": brief["steps"]}
    history.append(summary)
    history = history[-HISTORY_MAX:]

    receipt = {
        "schema": "auto_builder_receipt/1",
        "tool": "step3_local_auto_builder.py",
        "version": VERSION_TAG,
        "mode": "watch" if args.watch else "once",
        "trigger": trigger,
        "root": root,
        "started_at_kst": started,
        "finished_at_kst": finished,
        "ok": ok,
        "dry_run": bool(args.dry_run),
        "scanned": scanned,
        "steps": steps,
        "moved_backups": moved,
        "queue": read_queue_summary(root),
        "snapshots_updated": snapshots,
        "applied": applied,
        "history": history,
    }
    if not args.dry_run:
        try:
            write_json(receipt_path, receipt)
            info("   receipt: " + receipt_path)
        except Exception as e:
            info("   [warn] receipt write failed: %s" % e)
    return receipt


# ---------------------------------------------------------------------------
# watch loop
# ---------------------------------------------------------------------------
def watch(args):
    interval = max(0.5, float(args.interval))
    info("[watch] polling every %.1fs (omni_*.py + %s). Ctrl+C to stop." % (interval, QUEUE_NAME))
    last = signature(args.root)
    try:
        while True:
            time.sleep(interval)
            cur = signature(args.root)
            if cur == last:
                continue
            for _ in range(5):  # debounce: wait until the file stops changing
                time.sleep(1.0)
                nxt = signature(args.root)
                if nxt == cur:
                    break
                cur = nxt
            changed = sorted(os.path.basename(k) for k in cur if cur.get(k) != last.get(k))
            try:
                run_cycle(args, "watch:" + ",".join(changed[:5]))
            except Exception as e:
                info("[watch] cycle error: %r" % (e,))
            last = signature(args.root)
    except KeyboardInterrupt:
        info("")
        info("[watch] stopped by user.")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="RGON local patch auto-builder")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--once", action="store_true", help="apply pending patches once (default)")
    g.add_argument("--watch", action="store_true", help="keep watching for new patch files")
    ap.add_argument("--interval", type=float, default=2.0, help="watch polling interval in seconds (default 2)")
    ap.add_argument("--root", default=DEFAULT_ROOT, help="project folder (default: %s)" % DEFAULT_ROOT)
    ap.add_argument("--force", action="store_true", help="apply even if the same content was already applied")
    ap.add_argument("--dry-run", action="store_true", help="only report, change nothing")
    args = ap.parse_args()
    args.root = os.path.abspath(args.root)

    info("=" * 64)
    info(" RGON LOCAL AUTO BUILDER  (%s)  mode=%s" % (VERSION_TAG, "watch" if args.watch else "once"))
    info(" root: " + args.root)
    info("=" * 64)

    if not os.path.isdir(args.root):
        info("[ERROR] project folder not found: " + args.root)
        sys.exit(1)

    try:
        receipt = run_cycle(args, "startup")
    except Exception as e:
        info("[ERROR] build cycle failed: %r" % (e,))
        sys.exit(2)

    if args.watch:
        watch(args)

    info("")
    if not receipt.get("ok"):
        info("[warn] some steps failed. See the receipt: " + os.path.join(args.root, RECEIPT_REL))
    info("[STEP 3 LOCAL AUTO BUILDER COMPLETE]")


if __name__ == "__main__":
    main()
Copy