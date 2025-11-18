# Career Fair Copilot - Comprehensive System Design & Implementation Plan

## High-Level Goals (What the System Must Do)

1. Let user pick a major/profile and preferences
2. Ingest a career-fair map + companies list + hall area
3. Score and recommend which booths to visit (alignment with major, priorities)
4. Fetch & aggregate company details + recent news + jobs (scraping/APIs)
5. Generate tailored talking points and tailor the user's resume to selected job descriptions
6. Produce an optimized route/schedule maximizing interactions per unit time given travel times, queue lengths, and user time budget
7. Re-plan in real-time as queues or time change

## Core Concepts & Data Model

### User Profile
- Major
- Skills
- Experience
- Resume (PDF)
- Preferences (target roles, commute tolerance, company priority)

### Booth Node
- id
- company_id
- coordinates (x, y on map)
- service_time_estimate
- queue_length (dynamic)
- company metadata

### Graph
- Nodes = booths + entrances + amenities
- Edges = walkable paths with distance and traversal time

### Company Record
- name
- sector
- website
- careers URLs
- scraped job postings
- news snippets
- score vectors (embeddings)

### Itinerary
- Ordered list of booth visits with:
  - Arrival time
  - Service duration
  - Travel time
  - Expected wait

## Inputs

1. **Floor Plan**: Image or geo-free 2D map; JSON describing nodes or automated map-to-graph tool
2. **Number of Companies**: Hall area (for density/expected travel time)
3. **Live Queue Data**: Manual updates, operator feed, or sensor-based (QR scan, BLE, volunteer input)

## Technical Architecture

### Frontend
- **React Native** (mobile)
- **React** (web admin UI)

### Backend
- **FastAPI** (Python) or Node.js/Express for APIs

### Database
- **PostgreSQL** (primary relational)
- **Redis** (caching, realtime queue/state)

### Vector DB
- **Pinecone** / Milvus / Weaviate for embeddings

### Search/Index
- **Elasticsearch** (company/job search + news)

### Scraping
- **Playwright** (JS) for dynamic sites
- **Scrapy** for simpler pages
- Use rate-limits & robots.txt

### NLP & ML
- **Hugging Face transformers** (text embeddings & classification)
- **spaCy** for parsing
- **OpenAI/HF LLM** for tailored text generation (optional)

### Orchestration
- **Docker + Kubernetes** for scale

### Auth & Storage
- **OAuth** + encrypted S3 for resumes

## Algorithms — Scoring, Routing, Scheduling

### Company Scoring

```
Score(company, user) = w_major * major_alignment
                     + w_role * role_alignment
                     + w_interest * user_interest
                     + w_recency * news_relevance
```

- **major_alignment**: Via taxonomy match / embedding similarity between company description and major keywords
- **role_alignment**: Via embedding of JD vs user resume/skills

### Travel Graph & Shortest Path

- Build graph G(V,E) from map (nodes = booths; edges = walkable paths)
- Edge weight = travel_time (distance / walking_speed)
- Use **Dijkstra** (or A*) for shortest path queries between nodes

### Itinerary Optimization

**Core Problem**: Time-Constrained Orienteering / Prize-Collecting TSP

**Inputs**:
- Travel times
- Service times (including expected queue wait = queue_length * avg_interaction_time)
- Total time budget

**Objective**: Maximize sum of booth utilities (company score) subject to total time ≤ budget

**Approaches**:
1. **Greedy heuristic**: Repeatedly pick next node with max marginal utility/travel_time ratio; compute path with Dijkstra
2. **Dynamic Programming / ILP** (small N): Formulate as integer program (select subset + order) and solve with OR-Tools for higher quality when N small
3. **Metaheuristic** (GA / Simulated Annealing) for larger instances
4. Use Dijkstra to compute pairwise shortest travel times, then run the chosen solver on the condensed full-graph

### Real-Time Replanning

- Recompute itinerary when queue lengths change or user is delayed
- Use incremental update: re-evaluate remaining nodes and re-run greedy/ILP on remaining time

### Queue & Service-Time Model

```
service_time_estimate = base_interaction_time(role, type)
                      + expected_wait(queue_length, avg_service_per_person)
```

- Update queue_length from crowdsourced inputs, company-provided feed, or sensor scans

## Resume Tailoring & Talking Points (NLP Pipeline)

### Resume Parsing
- Parse PDF → structured JSON (sections: experience, education, skills)
- Use hybrid parser (GROBID + custom spaCy models)

### Job Parsing
- Scrape JD → extract responsibilities, required skills, keywords, seniority, role type

### Matching & Tailoring
- Compute embedding similarity between JD + company page and resume sections to rank relevance
- Generate suggested edits:
  - Add bullet points with quantifiable outcomes that match JD keywords
  - Reorder experience to highlight relevant roles/skills
  - Produce a tailored summary and suggested keywords
- Use an LLM (with prompt templates) to produce 3–5 concise, high-ROI resume bullets and a one-paragraph elevator pitch for the booth conversation

### ATS-Safety
- Provide an ATS score (simple classifier based on keyword coverage)
- Downloadable tailored PDF

### Talking Points Generator
- **Input**: Company objectives, user's role fit, recent news
- **Output**: 4–6 talking bullets:
  - Quick intro
  - 2 role-fit bullets
  - 1 question
  - 1 closing ask (contact/next steps)

## Company Data Ingestion & Scrapers

### Sources
- Company careers pages
- LinkedIn jobs (respect TOS)
- Official press releases
- RSS feeds
- Google News (via API)
- Public Glassdoor-like summaries (watch policies)

### Implementation
- Use **Playwright** for dynamic pages, **Scrapy** for batch jobs
- Store raw HTML, structured job postings, and extracted text
- Respect robots.txt, API Terms, rate limits, and cache results
- Use scheduled crawls + on-demand crawl for companies the user selects

### News Aggregator
- Use news API (Google News API / Bing News Search) where possible to avoid heavy scraping
- Summarize with an LLM to extract most recent 3–5 points relevant to recruitment/hiring

## UI/UX Flows

1. **Mobile Onboarding**: Select major, upload resume, set time budget and preferences
2. **Map View**: Floor plan with booth pins, color-coded by score & queue length
3. **Planner View**: List of suggested companies, utility score, expected time cost, and "Add to route"
4. **Route View**: Visual route + expected times; allow manual adjustment
5. **Company Card**: Company summary, top jobs, last 3 news bullet points, tailored talking points, button to tailor resume
6. **On-Visit Quick Card**: Elevator pitch, 2–3 talking points, question list, ability to mark "connected" or "skipped"
7. **Export**: Tailored resume PDF and CSV of companies visited or planned

## Privacy, Legal & Ethical Considerations

- Explicit consent for resume storage and scraping personalization
- Encrypt resumes at rest; access logging and deletion endpoints
- Follow robots.txt and site Terms-of-Service; prefer official APIs (LinkedIn, Indeed) where allowed
- Avoid encouraging deceptive claims in tailored resumes — only suggest rephrasing and emphasizing real experiences

## Metrics & Evaluation

### Core Metrics
- Interactions/hour
- Booths visited per fair
- Average time per interaction
- Conversion proxies (follow-up requests)
- User satisfaction (post-fair survey)

### Offline Simulation
- Simulate crowds & travel to validate routing heuristics before real deployment

## MVP Scope (Minimum to Test Core Value)

### Inputs
- Manual map upload or simple coordinate import + list of booths

### Features
- Basic user profile + resume upload & parsing
- Company scoring by major alignment (taxonomy + embeddings)
- Route planner: construct graph from coordinates and run greedy itinerary + Dijkstra paths
- Simple resume tailoring: keyword match + LLM-generated bullets
- Simple scraper: fetch company homepage and careers page for selected companies (on-demand)
- Mobile/web UI with map + itinerary export

**Time**: ~8–12 weeks

## Phased Roadmap & Sprint Plan

### Phase 0 (1 week)
Requirements, data model, UX wireframes, sample map formats

### Phase 1 — MVP (6–8 weeks)
- **Week 1–2**: Backend APIs, DB schema, user/resume upload, resume basic parser
- **Week 3**: Map ingestion, graph builder, Dijkstra implementation, greedy itinerary
- **Week 4**: Frontend UI for map + planner + company cards
- **Week 5**: Basic scraping pipeline (Playwright) for company pages
- **Week 6–8**: Resume tailoring (embedding match + LLM prompt templates), export PDF, end-to-end testing

### Phase 2 — Improvements (6–8 weeks)
- ILP/OR-Tools solver, better heuristics
- Richer scraping, news aggregator, vector DB
- Add ATS scoring and advanced resume edits

### Phase 3 — Real-time & Scale (6–12 weeks)
- Realtime queue integration (BLE/QR)
- Live replanning
- Multi-user concurrency
- Deploy to cloud, monitoring

### Phase 4 — Integrations / Partnerships
- Integrate with career fair organizers
- Company-provided feeds
- Job boards; data partnerships

## Implementation Details & Libraries (Recommended)

### Resume Parsing
- GROBID (XML)
- pyresparser
- spaCy

### Embeddings & LLMs
- OpenAI embeddings / local HF models (sentence-transformers)

### Optimization
- OR-Tools (routing and ILP)
- NetworkX (graph operations)
- SciPy for heuristics

### Scraping
- Playwright
- Scrapy
- BeautifulSoup

### Vector DB
- Pinecone / Milvus / Weaviate

### Frontend Mapping
- Mapbox GL (for coordinate-based maps) or SVG canvas for custom floorplans

### PDF Generation
- WeasyPrint / pdfkit / Puppeteer for tailored resume export

### Monitoring
- Prometheus + Grafana

## Risks & Mitigations

1. **Data quality for maps**: Provide a manual booth-editor UI to annotate the floor if auto-parsing fails
2. **Scraping legal risks**: Prefer official APIs; use rate-limits and legal review
3. **LLM hallucinations in resume suggestions**: Constrain prompts; require user approval; validate extracted facts with source text
4. **Real-time queue reliability**: Use fallback heuristics if live feed unavailable

## Example Algorithmic Flow (High Level)

1. Build graph G from map coordinates
2. For each company:
   - Fetch metadata & job postings
   - Compute company_score = f(user_profile, embeddings)
3. Compute pairwise shortest paths via Dijkstra on G
4. Solve or heuristic-select itinerary maximizing sum(company_scores) subject to time_budget
5. Generate tailored resume bullets and talking points via embedding alignment + LLM templates
6. Present route and allow on-device replanning when new queue data arrives

## Deliverables per Milestone

1. Data ingestion module + graph builder
2. Route optimizer + Dijkstra service
3. Company scraper + news aggregator
4. Resume parser + tailoring engine (embedding matcher + LLM prompts)
5. Mobile/web UI + export
6. Tests: unit, integration, simulation harness

## Project Structure

```
CF_Copilot/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app entry point
│   │   ├── config.py               # Configuration
│   │   ├── database.py             # Database connection
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── company.py
│   │   │   ├── booth.py
│   │   │   └── itinerary.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── companies.py
│   │   │   ├── booths.py
│   │   │   ├── routing.py
│   │   │   └── resume.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── scraper.py          # Web scraping service
│   │   │   ├── resume_parser.py    # Resume parsing
│   │   │   ├── graph_builder.py    # Graph construction
│   │   │   ├── routing.py          # Dijkstra & optimization
│   │   │   ├── scoring.py          # Company scoring
│   │   │   └── nlp.py              # NLP & embeddings
│   │   ├── schemas/
│   │   │   └── __init__.py
│   │   └── utils/
│   │       └── __init__.py
│   ├── scripts/
│   │   ├── extract_pdf_data.py     # Extract from career fair PDFs
│   │   ├── seed_database.py        # Seed initial data
│   │   └── test_routing.py         # Test routing algorithms
│   ├── tests/
│   │   ├── test_routing.py
│   │   ├── test_scraper.py
│   │   └── test_resume_parser.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Map/
│   │   │   ├── CompanyList/
│   │   │   ├── RoutePlanner/
│   │   │   ├── ResumeUpload/
│   │   │   └── TalkingPoints/
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── types/
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── package.json
│   └── tsconfig.json
├── data/
│   ├── raw/
│   │   ├── Day 1 - Fall 2025 ETCF Booklet.pdf
│   │   └── Day 2 - Fall 2025 ETCF Booklet (1).pdf
│   ├── processed/
│   │   ├── companies.json
│   │   ├── booths.json
│   │   └── map_coordinates.json
│   └── seeds/
├── docker-compose.yml
├── README.md
└── Plan.md
```
