# CF_Copilot Backend

FastAPI backend for the Career Fair Copilot application.

## Features

- Company search and filtering
- Booth location management
- Route optimization using Dijkstra's algorithm
- Greedy heuristic for time-constrained booth visiting
- User profile management
- Company scoring based on major/role alignment

## Setup

### Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Initialize Database

```bash
# Extract data from PDFs
python scripts/extract_pdf_data.py

# Seed database with company data
python scripts/seed_database.py
```

### Run the Application

```bash
# Option 1: Using run.py
python run.py

# Option 2: Using uvicorn directly
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## API Endpoints

### Companies

- `GET /api/v1/companies` - Get all companies with optional filters
  - Query params: `major`, `position_type`, `ballroom`, `search`, `platinum_only`
- `GET /api/v1/companies/{id}` - Get company by ID
- `GET /api/v1/companies/booth/{booth_number}` - Get company by booth
- `GET /api/v1/companies/filters/majors` - Get all majors
- `GET /api/v1/companies/filters/ballrooms` - Get all ballrooms
- `GET /api/v1/companies/filters/position-types` - Get position types

### Booths

- `GET /api/v1/booths` - Get all booths
- `GET /api/v1/booths/{booth_number}` - Get booth details
- `PATCH /api/v1/booths/{booth_number}/queue` - Update queue length

### Routing

- `POST /api/v1/routing/optimize` - Generate optimized route
- `POST /api/v1/routing/calculate-time` - Calculate time for booth sequence
- `GET /api/v1/routing/shortest-path` - Find shortest path between booths

### Users

- `POST /api/v1/users` - Create user
- `GET /api/v1/users/{id}` - Get user details
- `PATCH /api/v1/users/{id}/profile` - Update user profile

## Database Schema

- **companies** - Company information
- **position_types** - Position types offered by companies
- **majors_recruited** - Majors recruited by companies
- **booths** - Booth locations and coordinates
- **users** - User accounts
- **user_profiles** - User profiles with preferences
- **itineraries** - Planned routes
- **itinerary_items** - Individual visits in a route

## Architecture

```
backend/
├── app/
│   ├── models/          # SQLAlchemy models
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic
│   │   ├── graph_builder.py      # Graph construction
│   │   ├── routing_optimizer.py  # Route optimization
│   │   └── scoring.py            # Company scoring
│   ├── config.py        # Configuration
│   ├── database.py      # Database setup
│   └── main.py          # FastAPI app
├── scripts/             # Utility scripts
└── tests/               # Tests
```

## Configuration

Create a `.env` file in the backend directory:

```env
DATABASE_URL=sqlite:///./cf_copilot.db
DEBUG=True
AVG_WALKING_SPEED_MPS=1.4
AVG_INTERACTION_TIME_MIN=5.0
```

## Testing

```bash
pytest tests/
```
