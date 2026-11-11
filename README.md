# job-tracker (web app)
    python3 server.py        # open http://127.0.0.1:8765
- Tabs: target companies / all jobs / my applications / company directory
- Status dropdown + note per job, saved to tracker.json
- "Refresh from sites" runs the crawler (Jobinja + Jobvision, Tehran)
- "+ Add job" for internal company sites (saved to manual.json)
- Edit companies.json to change target companies

## Docker
    docker compose up -d --build     # http://127.0.0.1:8765
Statuses, notes and crawl results live in the `job-data` volume (`/data`), so they survive rebuilds.
