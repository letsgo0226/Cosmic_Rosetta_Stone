# Rosetta777 — GitHub-only publishing (proposed)

GitHub Pages publishes static files. It **cannot run the Python microkernel upon each HTTP request**, and **cannot protect JSON using Bearer authorization**. This is a public, read-only registry; for authenticated dynamic AI API operations use a separate cloud host later.

## Files added without modifying the original microkernel

- .github/workflows/rosetta777-pages.yml — verifies the kernel, runs unit tests, builds a site and optionally syncs YouTube metadata; then publishes to GitHub Pages.
- scripts/build_pages.py — generates index.html, data/check.json and data/index.json using the Python standard library.
- site/index.html — public search UI; data are inserted with safe textContent, not innerHTML.
- tests/test_pages.py — five offline unit tests with simulated API pagination.
- GITHUB_PAGES_SETUP.md — this guide.

## Activation after review

1. Review and merge the deployment pull request into main. Existing kernel and current Actions workflow are not modified.
2. In repository **Settings → Pages → Build and deployment**, choose **Source: GitHub Actions**.
3. Open **Actions**, select **Rosetta777 — verify and publish static index**, and manually run the workflow on main. Wait for the deployment to reach SUCCESS.
4. Optional: under **Settings → Secrets and variables → Actions** add a **repository secret** named YT_KEY with the YouTube Data API key and a **repository variable** named YT_ID with the verified UC-prefixed channel ID. Without the API key, the pipeline attempts the official public YouTube RSS feed for up to the latest ~15 uploads, using the verified @777alaje handle. YouTube's public channel HTML may block ID discovery; if so, the index explicitly reports rss_unavailable and does not fabricate records.
5. GitHub Actions checks approximately every six hours (minute 23 UTC), but schedules can be delayed or disabled due to repository inactivity.

Expected URL only after a successful Pages deployment:

https://letsgo0226.github.io/Cosmic_Rosetta_Stone/

This is **not a verified live link** until GitHub Pages confirms it.

## Public read-only files

- data/check.json — four core checks, sha256 and exact byte size
- data/index.json — timestamped public YouTube titles/IDs and reversible G257 address
- index.html — title/ID search interface

## Security and limits

- The original 2,045-byte plaintext kernel remains unchanged.
- No arbitrary Brainfuck/shell code execution endpoint exists in GitHub Pages.
- The official YouTube Data API is used when a key exists; otherwise the channel's public YouTube page is read once to resolve its ID, followed by the official YouTube RSS feed. This RSS path is best-effort, can fail if YouTube changes its HTML, and covers only recent uploads. API queries remain capped at 100 pages, with a 15-second request timeout.
- API key is kept in Actions secrets, not published in JSON, website, or source code.
- Metadata are public; the index records coverage as recent_only, public_uploads, or none. Subtitles, semantic interpretation and guaranteed availability are NOT provided.
- All published Pages content is public and unauthenticated. Do not put secrets or private information in the index.
- An authenticated, on-demand Python AI API still requires a separate running backend such as Railway or Render.
