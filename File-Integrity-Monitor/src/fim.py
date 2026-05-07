import hashlib
import json
import argparse
import sys
from pathlib import Path
from datetime import datetime

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

parser = argparse.ArgumentParser(description="PyFIM - File Integrity Monitor")

parser.add_argument("--init", type=str, help="Create baseline from target folder")
parser.add_argument("--scan", type=str, help="Scan folder and compare against baseline")

args=parser.parse_args()

def load_baseline(path: Path):
    with open(path, "r") as f:
        return json.load(f)

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
    stats = file_path.stat()
    
    return {
        "size": stats.st_size,
        "created": datetime.fromtimestamp(stats.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
        "modified": datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        "extension": file_path.suffix
    }

def create_baseline(target_folder: Path):
    baseline = {}
    for file_path in target_folder.iterdir():

        if file_path.is_file():
            baseline[str(file_path.resolve())] = {
                "hash": calculate_hash(file_path),
                "metadata": get_metadata(file_path)
            }
    return baseline

def save_baseline(baseline: dict, path: Path):
    with open(path, "w") as f:
        json.dump(baseline, f, indent=4)

def log_alert(severity, event_type, file_path, action):
    LOG_DIR.mkdir(exist_ok=True)

    log_file = LOG_DIR / "alerts.log"

    with open(log_file, "a") as f:
        f.write(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
            f"[{severity}] [{event_type}] {file_path} - {action}\n"
        )

def scan_directory(target_folder: Path):
    current = {}

    for file_path in target_folder.rglob("*"):

        if file_path.is_file():
            current[str(file_path.resolve())] = {
                "hash": calculate_hash(file_path),
                "metadata": get_metadata(file_path)
            }

    return current

def compare(baseline, current):

    changes_detected = 0

    baseline_files = set(baseline.keys())
    current_files = set(current.keys())

    new_files = current_files - baseline_files
    deleted_files = baseline_files - current_files
    common_files = baseline_files & current_files

    # NEW FILES
    for file in new_files:
        print("\n[HIGH] [NEW FILE] DETECTED")
        print(f"File: {file}")
        print("Action: Investigate immediately")

        log_alert("HIGH", "NEW FILE", file, "Investigate immediately")
        changes_detected += 1

    # DELETED FILES
    for file in deleted_files:
        print("\n[MEDIUM] FILE MISSING")
        print(f"File: {file}")
        print("Action: Check for deletion or tampering")

        log_alert("MEDIUM", "FILE MISSING", file, "Check for deletion or tampering")
        changes_detected += 1

    # MODIFIED FILES
    for file in common_files:
        if baseline[file]["hash"] != current[file]["hash"]:
            print("\n[HIGH] FILE MODIFIED")
            print(f"File: {file}")
            print("Action: Possible tampering detected")

            log_alert("HIGH", "FILE MODIFIED", file, "Possible tampering detected")
            changes_detected += 1
            
    if changes_detected == 0:
        print("\n[OK] No changes detected - system is stable")
    else:
        print(f"\n[SUMMARY] Total changes detected: {changes_detected}")

if args.init:

    target_folder = Path(args.init).resolve()
    if not target_folder.exists():

        print("[ERROR] Folder does not exist")
        sys.exit()

    if not any(target_folder.iterdir()):
        print("[WARNING] Folder is empty")

    baseline = create_baseline(target_folder)

    save_baseline(baseline, Path("baseline.json"))
    print("\n[+] Baseline created successfully")
    
    print(f"[+] Files monitored: {len(baseline)}")
    
    print("\n[+] Files included in baseline:")
    
    for i, file in enumerate(baseline.keys(), 1):
        print(f"{i}. {file}")

if args.scan:

    target_folder = Path(args.scan).resolve()

    if not target_folder.exists():
        print("[ERROR] Folder does not exist")
        sys.exit()

    baseline_path = Path("baseline.json")

    if not baseline_path.exists():
        print("[ERROR] No baseline found. Run --init first.")
        sys.exit()

    baseline = load_baseline(baseline_path)
    current = scan_directory(target_folder)

    compare(baseline, current)
