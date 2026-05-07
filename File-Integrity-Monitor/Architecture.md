# Architecture

## Overview
PyFIM is a lightweight File Integrity Monitoring tool that detects unauthorized file changes by comparing a trusted baseline against the current state of a directory.

It follows a snapshot-based detection model, similar to Host-based Intrusion Detection Systems (HIDS).

----
                    ┌──────────────────────────┐
                    │   Target Directory       │
                    │ (files to be monitored)  │
                    └──────────┬───────────────┘
                               │
                               ▼
               ┌──────────────────────────────┐
               │     File Scanner Engine      │
               │  (rglob directory traversal) │
               └──────────┬───────────────────┘
                          │
                          ▼
        ┌──────────────────────────────────────┐
        │     Hashing Engine (SHA-256)        │
        │  - Generates file fingerprints      │
        └──────────┬──────────────────────────┘
                   │
                   ▼
     ┌─────────────────────────────────────────┐
     │        Baseline Storage (JSON)          │
     │  - Trusted file state snapshot          │
     └──────────┬─────────────────────────────┘
                │
                ▼
     ┌─────────────────────────────────────────┐
     │       Comparison Engine                 │
     │  - Detects:                             │
     │    • New files                          │
     │    • Deleted files                     │
     │    • Modified files                    │
     └──────────┬─────────────────────────────┘
                │
                ▼
     ┌─────────────────────────────────────────┐
     │         Alert & Logging System          │
     │  - CLI alerts                          │
     │  - logs/alerts.log                     │
     └─────────────────────────────────────────┘

## Data Flow (How the system works)

```Mermaid
1. INIT MODE (--init)

   Target Folder
        ↓
   File Scanner
        ↓
   Hash Engine
        ↓
   Baseline JSON saved

--------------------------------------

2. SCAN MODE (--scan)
   Target Folder
        ↓
   File Scanner
        ↓
   Hash Engine
        ↓
   Current State
        ↓
   Comparison Engine
        ↓
   Alert System (CLI + Logs)
```
---
