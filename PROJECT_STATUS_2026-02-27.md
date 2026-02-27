# Project Status (2026-02-27)

## Project
Telegram bot for downloading media from YouTube and Instagram.

Repository:
- `https://github.com/Glebshir/tg-media-downloader`

## What Was Completed

1. GitHub Actions workflow fixed and working.
- Workflow: `.github/workflows/deploy.yml`
- Pipeline now passes (`build-and-push` + `notify-coolify` green).
- Coolify webhook uses GitHub Secret `COOLIFY_WEBHOOK`.

2. Security fix for git remote.
- Removed embedded PAT from `origin` URL.
- Current remote is clean (`https://github.com/Glebshir/tg-media-downloader.git`).

3. Bot code fixes.
- YouTube handler fixed: URL is now stored/read from FSM state (not parsed from message title).
- Instagram handler fixed for aiogram 3 media group types.
- File sending switched to `FSInputFile`.
- Size checks use `MAX_FILE_SIZE` from config.

4. Docker/CI fixes.
- `Dockerfile` updated with build dependencies and pip tooling update.
- `requirements.txt`: removed pinned `aiohttp` to avoid dependency conflicts.

## Key Commits (main)

- `9e82655` Fix media handlers and secure Coolify webhook secret
- `a30747a` Fix Coolify webhook condition in GitHub Actions
- `70e5535` Fix Docker build deps for pip install in CI
- `6ac5fac` Fix pip dependency conflict by removing aiohttp pin

## Current Coolify State

Environment variables were added manually in Coolify:
- `BOT_TOKEN` (value still needs real token from BotFather)
- `MAX_FILE_SIZE=52428800`

Current extra variable present:
- `NIXPACKS_NODE_VERSION` (not required for this Python app)

## What Is Still Pending

1. Create Telegram bot token.
- In Telegram open `@BotFather`
- `/newbot` -> create bot -> copy token

2. Put token into Coolify.
- App -> Environment Variables -> set `BOT_TOKEN=<real_token>`
- Save and `Redeploy`

3. Verify app runtime.
- Check Coolify logs:
  - No `BOT_TOKEN not set`
  - Polling started successfully

4. Functional smoke test in Telegram.
- Send 1 YouTube URL
- Send 1 Instagram URL
- Confirm media is downloaded and sent

## Quick Resume Checklist (Tomorrow)

1. Generate token in `@BotFather`
2. Update `BOT_TOKEN` in Coolify
3. Redeploy app in Coolify
4. Check logs for startup success
5. Test YouTube + Instagram links in chat with bot
6. If any failure appears, copy the exact log lines and continue debugging

## Notes

- Do not commit real `BOT_TOKEN` to git.
- Keep `COOLIFY_WEBHOOK` only in GitHub Secrets.
- If deployment fails again, first inspect:
  - GitHub Actions run logs
  - Coolify deployment/runtime logs
