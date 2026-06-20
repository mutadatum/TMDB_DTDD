# mutadatum

> Does killing the dog kill the box office?

A static data site correlating dog deaths in films (via [DoesTheDogDie.com](https://www.doesthedogdie.com/)) with worldwide box office gross (via [TMDB](https://www.themoviedb.org/)).

Built for [mutadatum.com](https://mutadatum.com) — data journalism for the curious.

---

## How it works

```
scripts/fetch_data.py   — fetches & joins TMDB + DTDD data → data/movies.json
index.html              — static site reads movies.json, renders scatter plot
.github/workflows/      — GitHub Actions runs the fetch script every Sunday
```

Data refreshes weekly via GitHub Actions. The site is fully static — no server,
no database, no running costs beyond GitHub Pages.

## Setup

### 1. Add API keys as GitHub secrets

In your repo → **Settings → Secrets and variables → Actions**, add:

| Secret name    | Where to get it                          |
|----------------|------------------------------------------|
| `TMDB_API_KEY` | [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api) |
| `DTDD_API_KEY` | [doesthedogdie.com/profile](https://www.doesthedogdie.com/profile) |

### 2. Enable GitHub Pages

Repo → **Settings → Pages** → Source: **Deploy from a branch** → branch: `main`, folder: `/ (root)`.

### 3. Run the first data fetch

Go to **Actions → Refresh movie data → Run workflow** to populate `data/movies.json` immediately
(rather than waiting for the Sunday cron).

### 4. Run locally

```bash
# Fetch data (needs env vars set)
TMDB_API_KEY=xxx DTDD_API_KEY=xxx python scripts/fetch_data.py

# Serve the site (browsers block local file:// fetch)
python -m http.server 8000
# then open http://localhost:8000
```

## Data notes

- Films with worldwide gross < $1M USD are excluded (unreported/VOD releases)
- Films with fewer than 20 DTDD community votes on "dogs dying" are excluded
- Dog-death confidence is a continuous 0–100% score, not a binary
- Point size on the chart encodes number of DTDD votes (larger = more confident rating)
- Data is committed back to this repo weekly; download it at `data/movies.json`

## Attribution

This site uses the DoesTheDogDie.com API (free tier) and TMDB API.
Per DoesTheDogDie.com's terms, attribution is required on all public uses of their data.

> Data sourced from [DoesTheDogDie.com](https://www.doesthedogdie.com/) and [The Movie Database](https://www.themoviedb.org/).

## Licence

Code: MIT. Data: subject to TMDB and DoesTheDogDie.com terms of service.
