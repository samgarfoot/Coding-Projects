# ⚙️ Command Usage Guide

This page explains how to run the File Triage Tool and what each command is used for.

The tool scans files within a directory, classifies them by type, detects suspicious executables, generates SHA-256 hashes for forensic tracking, and quarantines potentially risky files.

---

# 🧱 Basic Command Structure

```bash
python tool.py --path <directory>
```

### Argument	Description
```--path``` - Specifies the folder to scan and triage

If no path is provided, the current working directory is scanned by default.

## 📂 Basic Scan

Scans the current directory and processes files into categorized folders.

```python tool.py --path .```

### What this does
- Scans all top-level files in the current directory

Classifies files into:
- Images
- Documents
- PDFs
- Other
  - Detects suspicious executable files
  - Generates SHA-256 hashes for suspicious files
  - Creates log.txt containing audit events

Recommended Use
Testing the tool
Small directory triage
Demonstration environments
## 📁 Scan a Specific Directory

Scans a chosen folder and organizes files into categorized output directories.

```
python tool.py --path /Users/Name/Downloads
```

Example (Windows):
```
python tool.py --path C:\Users\Name\Downloads
```
Example (Linux/macOS):
```
python3 tool.py --path /home/user/Downloads
```
### What this does:

- Processes files inside the selected directory
- Detects potentially suspicious executables (.exe, .bat)
- Moves suspicious files into the Quarantine/ folder
- Logs all activity with timestamps and metadata

### Recommended Use
- Download folder analysis
- Malware triage simulations
- File organisation and auditing

## ⚠️ System Root Scan
Scans the system root directory.
```python tool.py --path /
```

### Security Protections
The tool includes safety controls for root-level scans:
- Requires manual confirmation
- Prevents accidental system-wide processing

### What this does
- Attempts to process files at the system root level
- Generates detailed audit logs
- Applies quarantine logic to suspicious files

### Recommended Use
- Controlled lab environments only
- Security testing
- Demonstration purposes
⚠ Warning: Root-level scans should only be performed in safe testing environments.
