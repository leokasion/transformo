# Transformo
**A lite processing server engine for automated file conversion, media transcoding, and Linux package migration.**

![Build Status](https://github.com/leokasion/transformo/actions/workflows/docker-build.yml/badge.svg)

---

### 🚀 Deployment (Full Stack)
The easiest way to run the full stack is using Docker Compose:

```bash
docker-compose up -d
```

# Project: Transformo
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
