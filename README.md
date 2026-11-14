# OrbitWatch: Planet X and SPHEREx

NASA Space Apps Challenge 2026 entry. A public web app that makes it easy to see how the sky changes over time. **A change is a lead, not a discovery.**

## Run it
Open `index.html` in a modern browser. No install, account, key or server needed.

## What the web app does
- **Explore:** 20 simulated sky fields; click a pink box for a plain-words explanation.
- **Blink**, **Date slider**, **Show difference** and **Compare** (drag-to-wipe) between the earlier and later observation.
- **Spot the mover:** a short game that teaches the idea.
- **Candidate queue:** filters, adjustable ranking weights, your verdict (saved on this device), copyable evidence note.
- **How it works:** a five-step explanation.
- **Real NASA data:** opens the official IRSA SPHEREx Data Explorer for a position, and lets you load **two of your own PNG images** into the same viewer.

## Data integrity
The sky images and candidates in the demo are **simulated**, and the page says so. Real data enters only through the two images you load. To prepare them: find two exposures of the same spot from different dates in IRSA, make two aligned PNGs (same orientation and scale), load them, and check anything interesting against JPL small-body tools. Copy IRSA's exact acknowledgment and DOI from its SPHEREx page.

## Optional API starter (not connected to the page)
`docker compose up --build` starts the API (port 8000), PostGIS and Redis. Change the sample database password first.

- `GET /health`
- `POST /v1/score`: same formula as the page, `(motion*w1 + signal*w2 + cross_match*w3 - artifact_risk*w4) / sum(weights)`
- `GET /v1/spherex/explorer?ra=&dec=&radius_arcsec=`: IRSA link
- `GET /v1/known-objects/{designation}`: JPL Small-Body Database lookup
- `POST /v1/reviews`: in-memory prototype

Known gaps: the page does not call the API (it would need CORS); `schema.sql` uses UUID candidate ids but the API accepts text ids; reviews are in memory with no login or size limit; Redis is not used yet.

## Files
```
index.html                the web app
services/api/             main.py, schema.sql, Dockerfile, requirements.txt
docker-compose.yml        API + PostGIS + Redis
docs/OrbitWatch_Presentation.pptx   21-slide interactive deck (clickable menu, page anatomy, use cases)
docs/OrbitWatch_Report.docx         full explanation in points
```

## Status
The page script has passed a syntax check only. Test it in a browser (desktop and phone) before submitting, and test the IRSA link and preset coordinates.
