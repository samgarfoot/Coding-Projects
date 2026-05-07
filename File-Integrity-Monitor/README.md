# 🛡️ PyFIM – File Integrity Monitor (Mini EDR Sensor)

## Overview
PyFIM (Python File Integrity Monitor) is a lightweight host-based security monitoring tool designed to detect unauthorized file changes in real time. It builds a cryptographic baseline of files using SHA-256 hashing and continuously compares system state against this baseline to identify suspicious activity.

The project simulates a core component of modern Host-based Intrusion Detection Systems (HIDS) and early-stage EDR (Endpoint Detection & Response) sensors, commonly used in SOC environments for endpoint telemetry collection and tamper detection.

## ⚙️ Core Features
🔐 File Integrity Monitoring
SHA-256 hashing for reliable tamper detection
Baseline creation and secure storage (baseline.json)

### Detection of:
- 🆕 New files
- ❌ Deleted files
- ✏️ Modified files

## 📁 Deep Directory Scanning
- Recursive scanning using `rglob`
- Full filesystem visibility within target directory

Metadata collection:

- File size
- Creation time
- Last modified time
- File extension

## Advanced Detection Engine
- Real-time change comparison against baseline
- Deduplication system to prevent repeated alerts

Structured severity classification:
      - HIGH → file creation/modification
      - MEDIUM → file deletion

## Behavior & Anomaly Detection
- Time-window based detection using event tracking

Burst detection logic for suspicious activity patterns:
      - 🚨 Ransomware-like file creation spikes
      - 🚨 Mass deletion behavior
      - 🚨 Rapid modification bursts
      - Sliding window event analysis using `deque`

## Alert Intelligence Layer
- JSON-formatted structured logging

Event enrichment with metadata:
      - timestamps (UTC ISO format)
      - event category (creation, deletion, modification)
      - hash comparison data
      - severity classification
      
## Watch Mode (Continuous Monitoring)
- Real-time monitoring mode using interval scanning
- Configurable scan interval `(--interval)`
- Continuous baseline comparison loop
- Lightweight polling-based detection engine

## CLI Interface

Built using argparse with simple operational modes:
- `--init <folder>` → create baseline snapshot
- `--scan <folder>` → run single comparison
- `--watch` → continuous monitoring mode

## Detection Logic

PyFIM compares filesystem state using three core sets:
- New Files → present in current scan but not baseline
- Deleted Files → present in baseline but missing in current scan
- Modified Files → same file path but different SHA-256 hash

On top of this, PyFIM introduces:
- Event rate tracking (time-window analysis)
- Burst detection thresholds for abnormal behavior
- Duplicate alert suppression using event keys

## Logging System
All alerts are stored in structured JSON format:
`logs/alerts.json`

Each event includes:
- Timestamp (UTC)
- Severity level
- Event type
- Target file/system context
- Action description
- Additional metadata (hashes, counters, behavior stats)

## Security Simulation Value
This project simulates core components of:
- Host-based Intrusion Detection Systems (HIDS)
- Endpoint Detection & Response (EDR) sensors
- Basic SIEM telemetry ingestion formats
- Ransomware behavior detection patterns

## 🚀 Current Enhancements Implemented
- ✔ Deduplication system for repeated alerts
- ✔ Time-window based behavioral detection
- ✔ JSON structured logging (SIEM-ready format)
- ✔ Continuous watch mode
- ✔ Event rate anomaly detection
- ✔ Improved alert categorization and severity tagging

## Future Expansion Ideas
- Process monitoring (process creation / tree analysis)
- Network connection tracking per process
- Simple SIEM correlation engine
- Auto-response actions (kill process / quarantine files)
Threat intelligence integration (hash reputation lookup)
