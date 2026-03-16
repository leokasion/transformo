# Project: Transformo
**Lead Architect:** Senior SysAdmin (Argentina-based, 25yr exp)
**Tech Stack:** Python/Flask, Debian-slim, Docker/Docker-compose

## Core Architecture: "Split-Brain" Worker
1. **Web Container (Face):** Handles UI/Uploads. Stateless.
2. **Worker Container (Muscle):** Directory watcher for shared volumes. 
   - Resource-pinned: `--cpus=0.5`, `--memory=512m`.
   - Security: Uses `subprocess` for system tools (ffmpeg, alien, etc.).

## Operational Principles
- **No Persistence:** Files must be deleted immediately after conversion.
- **Privacy First:** Show masked logs only (e.g., `my_se...ct.mp4`).
- **Source-Available:** Use a proprietary license for transparency without open competition.
- **Async Strategy:** Use "Email-to-Download" with time-limited unique hash links to avoid timeout and spam traps.

## Coding Standards
- Default Language: American English.
- Use Python/Flask for the backend glue.
- Prioritize native Linux system automation (shutil, os, subprocess).
- Preferred Base: Debian-slim for production-grade containers.
