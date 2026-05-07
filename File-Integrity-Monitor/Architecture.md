# Architecture

## Overview
PyFIM is a lightweight File Integrity Monitoring and behavioral detection tool that monitors filesystem changes by continuously comparing a trusted baseline against real-time directory state. It combines cryptographic file fingerprinting (SHA-256), structured telemetry logging, and time-window based anomaly detection to identify suspicious activity patterns such as rapid file creation, deletion bursts, and modification spikes.

It follows an extended snapshot + behavioral hybrid model, similar to modern Host-based Intrusion Detection Systems (HIDS) and early-stage Endpoint Detection & Response (EDR) sensors, providing both state-based and activity-based detection capabilities.

----
                ┌──────────────────────────┐
                │   Target Directory       │
                │ (Monitored Filesystem)   │
                └──────────┬───────────────┘
                           │
                           ▼
        ┌────────────────────────────────────┐
        │     File Discovery Layer           │
        │  (rglob recursive traversal)       │
        │  - Detects all files in scope      │
        └──────────┬─────────────────────────┘
                   │
                   ▼
        ┌────────────────────────────────────┐
        │      File Analysis Engine         │
        │  - SHA-256 hashing                │
        │  - Metadata extraction            │
        │  - File fingerprint generation    │
        └──────────┬─────────────────────────┘
                   │
                   ▼
        ┌────────────────────────────────────┐
        │   Baseline Management Layer       │
        │  - Trusted snapshot (JSON)        │
        │  - HMAC integrity verification    │
        │  - Baseline loading/saving        │
        └──────────┬─────────────────────────┘
                   │
                   ▼
        ┌────────────────────────────────────┐
        │     State Comparison Engine       │
        │  - Diff baseline vs current state │
        │  - Detects:                      │
        │     • New files                  │
        │     • Deleted files              │
        │     • Modified files             │
        └──────────┬─────────────────────────┘
                   │
                   ▼
        ┌────────────────────────────────────┐
        │  Behavioral Analytics Layer       │
        │  - Time-window event tracking     │
        │  - Burst detection (deque logic)  │
        │  - Ransomware-style pattern detection
        │  - Rate-based anomaly detection   │
        └──────────┬─────────────────────────┘
                   │
                   ▼
        ┌────────────────────────────────────┐
        │   Alert Deduplication Engine      │
        │  - Prevent duplicate alerts       │
        │  - Event key tracking             │
        │  - State memory (last alerts)     │
        └──────────┬─────────────────────────┘
                   │
                   ▼
        ┌────────────────────────────────────┐
        │     Telemetry & Logging Layer     │
        │  - JSON structured logs           │
        │  - Timestamped event records      │
        │  - Severity classification        │
        │  - EDR/SIEM-ready output format   │
        └──────────┬─────────────────────────┘
                   │
                   ▼
        ┌────────────────────────────────────┐
        │        Output Interfaces          │
        │  - CLI real-time alerts          │
        │  - logs/alerts.json ingestion     │
        │  - Watch mode continuous stream   │
        └────────────────────────────────────┘

## Data Flow (How the system works)

1. INIT MODE (--init)
```Mermaid
   Target Folder
        ↓
   File Scanner
        ↓
   Hash Engine (SHA-256 + Metadata)
        ↓
   Baseline Builder
        ↓
   HMAC Integrity Wrapper (Baseline Protection)
        ↓
   Baseline JSON Saved (baseline.json)

```
2. SCAN MODE (--scan)
```Mermaid
   Target Folder
        ↓
   File Scanner (rglob traversal)
        ↓
   Hash Engine (SHA-256 + Metadata)
        ↓
   Current State Snapshot
        ↓
   Comparison Engine (diff baseline vs current)
        ↓
   ┌──────────────────────────────────────┐
   │ Detection Outputs                    │
   │ - New Files                         │
   │ - Deleted Files                     │
   │ - Modified Files                    │
   └──────────────────────────────────────┘
        ↓
   Behavioral Analytics Layer
   (time-window + rate detection)
        ↓
   Deduplication Engine
   (event key suppression)
        ↓
   Alert Generation Engine
   (severity classification + enrichment)
        ↓
   ┌──────────────────────────────┐
   │ Output Layer                 │
   │ - CLI alerts                │
   │ - JSON logs (alerts.json)   │
   └──────────────────────────────┘

```
3. WATCH MODE (--watch)
```Mermaid
   Target Folder
        ↓
   Continuous Loop (interval-based)
        ↓
   File Scanner
        ↓
   Hash Engine
        ↓
   Current State Snapshot
        ↓
   Comparison Engine
        ↓
   Behavioral Analytics Layer
        ↓
   Alert System
        ↓
   Repeat cycle (state updated each interval)
```
---
