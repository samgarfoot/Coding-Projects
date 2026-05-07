import shutil
import hashlib
import argparse
from datetime import datetime
from pathlib import Path
import os
import sys

# =========================
# SUMMARY COUNTERS
# =========================
total_files = 0
moved_files = 0
suspicious_files = 0
quarantined_files = 0
hashes_generated = 0

# =========================
# ARGPARSE
# =========================
parser = argparse.ArgumentParser(description="File Triage Tool")

parser.add_argument(
    "--path",
    type=str,
    default=".",
    help="Folder to scan (default: current directory)"
)

args = parser.parse_args()

# =========================
# LOG INIT
# =========================
with open("log.txt", "w") as log_file:
    log_file.write("==== FILE TRIAGE LOG ====\n\n")

# =========================
# HELPERS
# =========================
def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_file_hash(path: Path):
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(4096):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_file_metadata(path: Path):
    stats = path.stat()
    return {
        "size": stats.st_size,
        "created": datetime.fromtimestamp(stats.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
        "modified": datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        "extension": path.suffix
    }


def log(event_type, file_name, message="", severity="INFO",
        file_hash="N/A", destination="N/A",
        size="N/A", extension="N/A",
        created="N/A", modified="N/A"):

    with open("log.txt", "a") as log_file:
        log_file.write(f"""
==================================================
Timestamp   : {get_time()}
Event       : {event_type}
Severity    : {severity}
File        : {file_name}
Extension   : {extension}
Size        : {size} bytes
Created     : {created}
Modified    : {modified}
Destination : {destination}
Hash        : {file_hash}
Details     : {message}
==================================================

""")


# =========================
# SETTINGS
# =========================
folder = Path(args.path).expanduser().resolve()

USER_BASE = Path.home()

# =========================
# SAFETY (kept minimal)
# =========================
if folder == Path("/").resolve():
    confirm = input("⚠ SYSTEM ROOT DETECTED. Type YES: ")
    if confirm != "YES":
        sys.exit()

# =========================
# OUTPUT FOLDERS
# =========================
OUTPUT_DIRS = ["Images", "Documents", "PDFs", "Other", "Quarantine"]

for f in OUTPUT_DIRS:
    (folder / f).mkdir(parents=True, exist_ok=True)

# =========================
# 🔥 FIXED SCANNING (IMPORTANT)
# =========================
# ONLY scan top-level files in the folder
# (prevents double counting, recursion bugs, and output pollution)

IGNORE_FILES = {".DS_Store"}  # note: no leading dot needed

all_files = [
    f for f in folder.iterdir()
    if f.is_file()
    and f.name not in IGNORE_FILES
    and f.name not in ["main.py", "log.txt"]
]

# =========================
# PROCESS FILES
# =========================
for file_path in all_files:

    total_files += 1

    metadata = get_file_metadata(file_path)
    file_hash = "N/A"

    # CATEGORY
    if file_path.suffix in [".jpg", ".png"]:
        category = "Images"
    elif file_path.suffix == ".txt":
        category = "Documents"
    elif file_path.suffix == ".pdf":
        category = "PDFs"
    else:
        category = "Other"

    # SUSPICIOUS
    is_suspicious = file_path.suffix in [".exe", ".bat"]

    if is_suspicious:
        suspicious_files += 1

        log(
            "SUSPICIOUS FILE DETECTED",
            file_path.name,
            "Executable detected",
            "HIGH",
            size=metadata["size"],
            extension=metadata["extension"],
            created=metadata["created"],
            modified=metadata["modified"]
        )

        file_hash = get_file_hash(file_path)
        hashes_generated += 1

        log(
            "HASH GENERATED",
            file_path.name,
            "SHA256 calculated",
            "INFO",
            file_hash=file_hash,
            size=metadata["size"],
            extension=metadata["extension"],
            created=metadata["created"],
            modified=metadata["modified"]
        )

        category = "Quarantine"

    destination = folder / category / file_path.name

    shutil.move(str(file_path), str(destination))
    moved_files += 1

    log(
        "FILE MOVED",
        file_path.name,
        f"Moved to {category}",
        "INFO",
        file_hash=file_hash,
        destination=str(destination),
        size=metadata["size"],
        extension=metadata["extension"],
        created=metadata["created"],
        modified=metadata["modified"]
    )

    if is_suspicious:
        quarantined_files += 1

        log(
            "FILE QUARANTINED",
            file_path.name,
            "Isolated suspicious file",
            "HIGH",
            file_hash=file_hash,
            destination=str(destination),
            size=metadata["size"],
            extension=metadata["extension"],
            created=metadata["created"],
            modified=metadata["modified"]
        )

# =========================
# SUMMARY REPORT
# =========================
print("\n" + "="*50)
print("📊 FILE TRIAGE SUMMARY")
print("="*50)
print(f"Total files scanned    : {total_files}")
print(f"Files moved            : {moved_files}")
print(f"Suspicious files       : {suspicious_files}")
print(f"Quarantined files      : {quarantined_files}")
print(f"Hashes generated       : {hashes_generated}")
print("="*50 + "\n")
