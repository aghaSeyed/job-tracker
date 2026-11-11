# Job Tracker

A small local web app for tracking software-engineering job applications in Tehran. It crawls
Iranian job boards, highlights openings at well-known high-paying companies (Digikala, Snapp group,
Tapsi, crypto exchanges, gold apps, payment companies), and lets you track follow-up status:
applied, interview, rejected and so on.

Pure Python standard library: no pip dependencies.

## Features

- Crawls **Jobinja** and **Jobvision** (Tehran, software keywords such as PHP, backend, Python, Go, Java, DevOps).
- Flags jobs from the target companies listed in `companies.json`.
- Per-job status (`new`, `saved`, `applied`, `interview`, `offer`, `rejected`, `ignored`) and a free-text note.
  The applied date is recorded automatically.
- Tabs: target companies, all jobs, my applications, company directory (careers page and search links).
- Filters: text search, status, source, "engineering only", "hide rejected/ignored".
- "Refresh from sites" button runs the crawl in the background.
- "+ Add job" for internal company sites and boards that can't be crawled.

## Run

### Docker

```bash
docker compose up -d --build     # http://127.0.0.1:8765
docker compose logs -f
docker compose down              # stops; data is kept in the job-data volume
```

### Without Docker

```bash
python3 server.py                # http://127.0.0.1:8765
```

Needs Python 3.10+. Don't run both at once, they use the same port.

## Configuration

| Env var    | Default     | Meaning                                         |
|------------|-------------|-------------------------------------------------|
| `HOST`     | `127.0.0.1` | Bind address (the Docker image uses `0.0.0.0`)  |
| `PORT`     | `8765`      | Port                                            |
| `DATA_DIR` | project dir | Where state files are written (`/data` in Docker) |

The compose file publishes the port on `127.0.0.1` only. The app has **no authentication**, so only
expose it on a trusted network.

## Data files

Written to `DATA_DIR` and git-ignored:

- `tracker.json`: your statuses and notes, keyed by job URL (or `company:<name>`)
- `manual.json`: jobs you added by hand
- `jobs.json`: latest crawl result

Re-crawling replaces `jobs.json` only. Your statuses and notes are never overwritten.

## Customizing

- **Target companies:** edit `companies.json`. Each entry has `name`, `group`, `aliases` and `careers`.
  A job matches when an alias appears in the company name of the posting. Keep aliases specific,
  because generic words cause false matches.
- **Keywords and depth:** `KEYWORDS` and `PAGES` at the top of `crawl.py`.
- **Engineering filter:** the `ENG` and `NOENG` regexes in `static/index.html`.

## Project layout

```
server.py            HTTP server and JSON API
crawl.py             Jobinja and Jobvision crawler (also runnable alone: python3 crawl.py)
companies.json       target company list
static/index.html    the whole UI
Dockerfile, docker-compose.yml, .dockerignore
report.py            older static HTML report generator (superseded by the web UI)
```

### API

| Method | Path          | Body                                | Purpose                       |
|--------|---------------|-------------------------------------|-------------------------------|
| GET    | `/api/data`   |                                     | jobs, companies, tracker, crawl state |
| POST   | `/api/track`  | `{key, status?, note?}`             | save status or note           |
| POST   | `/api/manual` | `{title, url, company?, salary?}`   | add a job by hand             |
| POST   | `/api/crawl`  |                                     | start a crawl (409 if running) |

## Known limitations

- **Jobvision** uses an undocumented API (`candidateapi.jobvision.ir`) that may change without notice.
- **Candoo** is unreachable from the crawler, and company career pages are not crawled yet.
  Use "+ Add job" for those.
- Jobinja hides salaries for logged-out users, so most Jobinja rows have no salary.
- The "Posted" column mixes ISO dates (Jobvision) with Persian relative text (Jobinja), so sorting
  across sources is approximate.
- Be polite: the crawler sleeps between requests. Check each site's terms before heavy use.
