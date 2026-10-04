# 🦊 Maple Hollow Studio

An autonomous YouTube studio for **Maple Hollow**, a 3D animated series of funny adventures with life lessons for kids 8–14.
Bots write, voice, animate, edit, QA, publish and analyse. You only watch each episode and approve it.
Everything runs on free tiers, 24/7, with your laptop off.

**Dashboard:** `https://<your-github-user>.github.io/<repo>/`

## The bots

| Bot | Runs on | Does |
|---|---|---|
| 🖋️ Writer | Claude Code routine (daily, cloud) | Writes a new episode from `bible.md`, learns from analytics, revises from your notes |
| 🎙️ Voice actor | GitHub Actions | Kokoro open-source TTS, one voice per character, lip-sync timing, subtitles |
| 🎬 Animators | GitHub Actions, 4 machines in parallel | Blender 4.5 builds the characters, sets and camera work and renders the episode |
| ✂️ Editor & QA | GitHub Actions | Adds a HyperFrames "Today's lesson" end card (`cards/endcard/`), upscales to 1080p, mixes music + voices, loudness to YouTube spec, Short, thumbnail, quality checks |
| 🚀 Publisher | GitHub Actions | On your **approved** label: schedules episode + Short on YouTube (made-for-kids, captions, thumbnail) |
| 📊 Analyst | GitHub Actions (nightly) | Views, retention, subscribers → `docs/analytics.json` → dashboard + writer |
| 🩺 Doctor | GitHub Actions | Retries any failed run once, files script errors back to the writer |

Flow: `episodes/epNNN.json` → **Produce** workflow → review ticket (GitHub issue) → you label **approved** or **redo** → **Publish**.

## Your one-time setup (about 30 minutes)

**1. Connect YouTube** (free):
1. Create the channel (use a Brand Account so you can add managers later) and verify it by phone at youtube.com/verify (needed for custom thumbnails).
2. Go to console.cloud.google.com → new project → *APIs & Services → Library*: enable **YouTube Data API v3** and **YouTube Analytics API**.
3. *OAuth consent screen*: External, add yourself as a user, then **Publish app → In production**. If you leave it in "Testing", the login expires every 7 days.
4. *Credentials → Create credentials → OAuth client ID → Desktop app* → download the JSON as `client_secret.json` into this folder.
5. Run:
   ```bash
   pip install google-auth-oauthlib google-api-python-client
   python pipeline/youtube.py auth client_secret.json
   ```
   Sign in with the channel's Google account. The login is stored as the GitHub secret `YT_TOKEN`, and analytics start that night.

**2. Turn on auto-upload.** Google locks videos uploaded through new API projects to *private* until the project passes a free
compliance audit. Apply at https://support.google.com/youtube/contact/yt_api_form (say it's a personal tool that uploads your own channel's videos).
Until then, approving an episode posts a 2-minute **manual upload checklist** with every file and all the text ready to paste.
After approval:
```bash
gh variable set AUTO_UPLOAD --body true
```

## Daily routine (about 10 minutes)
Open the dashboard → **Waiting for your review** → watch → open the ticket →
- add the label **approved**, or
- comment what to change (e.g. "Bolt's joke in scene 3 isn't clear; make the ending shorter") and add **redo**.

## Make it better over time
- **Music:** drop YouTube Audio Library tracks into `music/` (safe for monetization). Otherwise a music-box tune is generated per episode.
- **Characters, sets, props:** everything is data in `pipeline/world.py`. Add a prop or setting there and the writer can use it (`check.py --vocab`).
- **Render quality:** `RES`/`SAMPLES` in `.github/workflows/produce.yml` (higher = slower; free runners are CPU-only).

## Honest limits
- **Monetization:** YouTube Partner Program needs 1,000 subscribers + 4,000 watch hours (or 10M Shorts views in 90 days). Made-for-kids
  videos get no personalised ads, comments or notification bell, so growth and revenue per view are lower than for general audiences. Expect months, not weeks.
- **"AI slop" risk:** YouTube demonetizes *mass-produced, repetitive* content. What protects you: an original recurring cast,
  real stories with structure, varied episodes, a pace of about one a day, and your review of every video. Don't approve weak episodes; send them back with **redo**.
- **Look:** this is a clean, toy-like stylised 3D look rendered on free CPUs, not Pixar. The biggest upgrades are human voice acting
  and hand-modelled characters.
- **Writer:** routines run on your Claude subscription. If a run is skipped, nothing breaks; the next run catches up.
