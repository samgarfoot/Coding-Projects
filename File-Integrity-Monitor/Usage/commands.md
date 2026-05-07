# PyFIM – Usage Commands

## 1. Create a Baseline (Trusted Snapshot)
Run this first to record the current safe state of a folder:
```
python fim.py --init /path/to/your/test_folder
```
Example (Windows):
```
python fim.py --init C:\Users\YourName\test_folder
```
Example (Linux/macOS):
```
python3 fim.py --init /home/user/test_folder
```
## 2. Run a File Integrity Scan
After making changes (or simulating an attack), run:
```
python fim.py --scan /path/to/your/test_folder
```
Example (Windows):
```
python fim.py --scan C:\Users\YourName\test_folder
```
Example (Linux/macOS):
```
python3 fim.py --scan /home/user/test_folder
```
## 3. Observe output
