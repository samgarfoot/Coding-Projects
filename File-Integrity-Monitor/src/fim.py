import hashlib
import json
import argparse
import sys
from pathlib import Path
from datetime import datetime
from collections import deque
import time
import hmac

# ---------------- STATE ---------------- #

event_times = {
    "new": deque(),
    "deleted": deque(),
    "modified": deque()
}

last_alert_state = {}
last_behavior_alert = {}

SECRET_KEY = b"fim_secret_key"

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# ---------------- ARGPARSE ---------------- #

parser = argparse.ArgumentParser(description="PyFIM - File Integrity Monitor")

parser.add_argument("--init", type=str, help="Create baseline from target folder")
parser.add_argument("--scan", type=str, help="Scan folder and compare against baseline")
parser.add_argument("--watch", action="store_true", help="Continuously monitor folder")
parser.add_argument("--interval", type=int, default=30, help="Scan interval in seconds")

args = parser.parse_args()

# ---------------- UTIL ---------------- #

def prune_events(event_queue, window_seconds):
    current_time = time.time()

    while event_queue and current_time - event_queue[0] > window_seconds:
        event_queue.popleft()

# ---------------- WATCH MODE ---------------- #

def watch_mode(target_folder, baseline):
    print(f"[WATCH MODE] Monitoring {target_folder} every {args.interval}s\n")

    while True:
        time.sleep(args.interval)

        current_state = scan_directory(target_folder)
        compare(baseline, current_state)

# ---------------- BASELINE SECURITY ---------------- #

def generate_baseline_hash(data: dict):
    return hmac.new(
        SECRET_KEY,
        json.dumps(data, sort_keys=True).encode(),
        hashlib.sha256
    ).hexdigest()


def load_baseline(path: Path):
    with open(path, "r") as f:
        data = json.load(f)

    if "baseline" not in data or "hash" not in data:
        print("[CRITICAL] Invalid baseline format")
        sys.exit()

    expected_hash = generate_baseline_hash(data["baseline"])

    if data["hash"] != expected_hash:
        print("[CRITICAL] Baseline tampering detected!")
        sys.exit()

    return data["baseline"]


def save_baseline(baseline: dict, path: Path):
    data = {
        "baseline": baseline,
        "hash": generate_baseline_hash(baseline)
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# ---------------- FILE ANALYSIS ---------------- #

def calculate_hash(path: Path):
    try:
        hasher = hashlib.sha256()
        with path.open("rb") as f:
            while chunk := f.read(4096):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return "UNREADABLE"


def get_metadata(file_path: Path):
    try:
        stats = file_path.stat()
        return {
            "size": stats.st_size,
            "created": datetime.fromtimestamp(stats.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
            "modified": datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "extension": file_path.suffix
        }
    except Exception:
        return {
            "size": -1,
            "created": "UNKNOWN",
            "modified": "UNKNOWN",
            "extension": file_path.suffix
        }

# ---------------- SCANNING ---------------- #

def create_baseline(target_folder: Path):
    baseline = {}

    for file_path in target_folder.iterdir():
        if file_path.is_file():
            baseline[str(file_path.resolve())] = {
                "hash": calculate_hash(file_path),
                "metadata": get_metadata(file_path)
            }

    return baseline


def scan_directory(target_folder: Path):
    current = {}

    for file_path in target_folder.rglob("*"):
        if file_path.is_file():
            current[str(file_path.resolve())] = {
                "hash": calculate_hash(file_path),
                "metadata": get_metadata(file_path)
            }

    return current

# ---------------- LOGGING ---------------- #

def log_alert(severity, event_type, file_path, action, extra=None):
    log_file = LOG_DIR / "alerts.json"

    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "severity": severity,
        "event_type": event_type,
        "file": file_path,
        "action": action,
        "extra": extra or {}
    }

    with open(log_file, "a") as f:
        f.write(json.dumps(event) + "\n")

# ---------------- COMPARISON ENGINE ---------------- #

def compare(baseline, current):
    WINDOW = 10  # seconds

    baseline_files = set(baseline.keys())
    current_files = set(current.keys())

    new_files = current_files - baseline_files
    deleted_files = baseline_files - current_files
    common_files = baseline_files & current_files

    # ---------------- NEW FILES ---------------- #
    for file in new_files:
        event_times["new"].append(time.time())
        prune_events(event_times["new"], WINDOW)

        if len(event_times["new"]) > 20:
            if not last_behavior_alert.get("new_burst"):
                print("\n[CRITICAL] RANSOMWARE-LIKE FILE CREATION BURST")
                log_alert(
                    "CRITICAL",
                    "RANSOMWARE_BURST_NEW_FILES",
                    "SYSTEM",
                    "Too many file creations in time window",
                    extra={"count": len(event_times["new"]), "window": WINDOW}
                )
                last_behavior_alert["new_burst"] = True

    # ---------------- DELETED FILES ---------------- #
    for file in deleted_files:
        event_times["deleted"].append(time.time())
        prune_events(event_times["deleted"], WINDOW)

        if len(event_times["deleted"]) > 10:
            if not last_behavior_alert.get("del_burst"):
                print("\n[CRITICAL] MASS DELETION BURST DETECTED")
                log_alert(
                    "CRITICAL",
                    "DELETION_BURST",
                    "SYSTEM",
                    "Too many file deletions in time window",
                    extra={"count": len(event_times["deleted"]), "window": WINDOW}
                )
                last_behavior_alert["del_burst"] = True

    # ---------------- MODIFIED FILES ---------------- #
    for file in common_files:
        old_hash = baseline[file]["hash"]
        new_hash = current[file]["hash"]

        if old_hash != new_hash:

            event_times["modified"].append(time.time())
            prune_events(event_times["modified"], WINDOW)

            event_key = f"{file}:{new_hash}"

            if last_alert_state.get(event_key):
                continue

            last_alert_state[event_key] = True

    # ---------------- BURST DETECTION (FIXED PLACE) ---------------- #

    mod_rate = len(event_times["modified"]) / WINDOW

    if mod_rate > 3:
        if not last_behavior_alert.get("mod_burst"):
            print("\n[CRITICAL] TAMPERING BURST DETECTED")
            log_alert(
                "CRITICAL",
                "MODIFICATION_BURST",
                "SYSTEM",
                "High rate of file modifications detected",
                extra={
                    "count": len(event_times["modified"]),
                    "window": WINDOW,
                    "rate": mod_rate
                }
            )
            last_behavior_alert["mod_burst"] = True

# ---------------- CLI FLOW ---------------- #

if args.init:
    target_folder = Path(args.init).resolve()

    if not target_folder.exists():
        print("[ERROR] Folder does not exist")
        sys.exit()

    baseline = create_baseline(target_folder)
    save_baseline(baseline, Path("baseline.json"))

    print("\n[+] Baseline created successfully")
    print(f"[+] Files monitored: {len(baseline)}")

elif args.scan:
    target_folder = Path(args.scan).resolve()

    if not target_folder.exists():
        print("[ERROR] Folder does not exist")
        sys.exit()

    baseline_path = Path("baseline.json")

    if not baseline_path.exists():
        print("[ERROR] No baseline found. Run --init first.")
        sys.exit()

    baseline = load_baseline(baseline_path)

    if args.watch:
        watch_mode(target_folder, baseline)
    else:
        current = scan_directory(target_folder)
        compare(baseline, current)
