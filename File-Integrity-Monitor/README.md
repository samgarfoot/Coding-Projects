PyFIM – File Integrity Monitor
📌 Overview
PyFIM (Python File Integrity Monitor) is a lightweight security tool designed to detect unauthorized file changes within a target directory. It builds a cryptographic baseline of files using SHA-256 hashing and continuously compares current file states against the stored baseline to detect:
🆕 Newly added files
❌ Deleted files
✏️ Modified or tampered files
This project simulates a core component of real-world Host-based Intrusion Detection Systems (HIDS) used in cybersecurity monitoring and SOC environments.
⚙️ Features
🔐 SHA-256 File Hashing for tamper detection
📁 Recursive directory scanning using rglob
🧾 Baseline generation & persistence in JSON format
📊 Metadata tracking (size, creation time, modification time, extension)
🚨 Change detection engine
New file detection (HIGH severity)
Modified file detection (HIGH severity)
Deleted file detection (MEDIUM severity)
📝 Alert logging system with timestamps
💻 Simple CLI interface using argparse
🧠 How It Works
1. Baseline Creation
When run with --init, the tool scans a target directory and stores:
File path
SHA-256 hash
Metadata
This baseline is saved as baseline.json.
2. Scanning Mode
When run with --scan, the tool:
Recalculates hashes for all current files
Loads the saved baseline
Compares both states
3. Detection Logic
Changes are classified into:
New Files → exist now but not in baseline
Deleted Files → existed in baseline but missing now
Modified Files → same file path but different hash
4. Logging System
All detected events are logged to:
logs/alerts.log
Each entry includes:
Timestamp
Severity level
Event type
File path
Action recommendation
🧪 Example Usage
Create Baseline
python fim.py --init /path/to/folder
Scan for Changes
python fim.py --scan /path/to/folder
📂 Project Structure
PyFIM/
│
├── fim.py
├── baseline.json
├── logs/
│   └── alerts.log
└── README.md
🔐 Security Relevance
This tool demonstrates key cybersecurity concepts:
File integrity verification
Hash-based tamper detection
Change auditing
Basic forensic logging
Host-based monitoring principles
It mirrors techniques used in:
SOC monitoring tools
Endpoint detection systems (EDR/HIDS)
Compliance auditing (PCI-DSS, ISO 27001)
🚀 Future Improvements
⏱️ Continuous real-time monitoring (watchdog integration)
📡 Email/Discord alerting system
🧠 Machine learning anomaly detection layer
🗄️ SQLite database storage instead of JSON
🔐 Digital signature verification (HMAC or RSA)
📊 Dashboard UI (Flask or React-based SOC panel)
🧵 Multi-threaded scanning for performance scaling

