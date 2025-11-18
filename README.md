# CF_Copilot - Career Fair Copilot

An intelligent career fair navigation and optimization system for University of Houston Engineering & Technology Career Fair.

## 🎯 Project Status

**Phase 1 (Backend MVP): COMPLETED ✅**
- Fully functional REST API
- 21 companies from Fall 2025 ETCF
- Intelligent routing optimization
- Company scoring system
- Database seeded and tested

**Phase 2 (Frontend MVP): COMPLETED ✅**
- React + TypeScript application
- Interactive floor map visualization
- Company search and filtering
- Route planner with optimization
- User profile management
- Fully integrated with backend

## 🚀 Features

### Backend (Completed)
- ✅ Company search and filtering by major, position type, ballroom
- ✅ Intelligent route optimization (greedy heuristic)
- ✅ Dijkstra's algorithm for shortest paths
- ✅ Company scoring based on user profile
- ✅ Real-time queue length updates
- ✅ User profile management
- ✅ Time-constrained booth visit planning
- ✅ RESTful API with comprehensive documentation

### Frontend (Completed)
- ✅ Interactive floor map with booth visualization
- ✅ Company cards with detailed information
- ✅ Advanced search and filtering (major, position, ballroom)
- ✅ Manual booth selection and deselection
- ✅ Route planner with time budget optimization
- ✅ User profile modal for preferences
- ✅ Responsive design for mobile and desktop
- ✅ Zoom controls for floor map navigation
- ✅ Step-by-step itinerary with arrival times

### Future Enhancements (Phase 3+)
- 🔲 Resume upload and tailoring
- 🔲 NLP-based talking points generation
- 🔲 Web scraping for company details
- 🔲 Real-time queue tracking via BLE/QR
- 🔲 News aggregation for companies
- 🔲 Advanced optimization with OR-Tools

## 📊 Quick Stats

- **Companies**: 21 (Day 1)
- **Majors**: 32 engineering disciplines
- **Booths**: 21 locations across 3 ballrooms
- **API Endpoints**: 15+
- **Algorithms**: Dijkstra, Greedy optimization, Multi-factor scoring

## 🏗️ Architecture

```
CF_Copilot/
├── backend/              # FastAPI REST API ✅
│   ├── app/
│   │   ├── models/      # Database models (SQLAlchemy)
│   │   ├── routes/      # API endpoints
│   │   ├── services/    # Business logic (routing, scoring)
│   │   └── config.py    # Application settings
│   ├── scripts/         # Data extraction & seeding
│   ├── tests/           # Unit tests
│   ├── Dockerfile       # Container configuration
│   └── run.py           # Application entry point
├── frontend/            # React + TypeScript app ✅
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── services/    # API client layer
│   │   ├── types/       # TypeScript definitions
│   │   └── App.tsx      # Main application
│   ├── Dockerfile       # Production build
│   └── vite.config.ts   # Build configuration
├── data/
│   ├── raw/            # PDF booklets
│   └── processed/      # Extracted JSON data
├── docker-compose.yml  # Multi-service orchestration
├── Plan.md             # Comprehensive system design
├── PROGRESS.md         # Development milestones
├── DEPLOYMENT.md       # Deployment guide
└── ISSUES.md           # Known issues tracking
```

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.104+
- **Database**: SQLite with SQLAlchemy ORM
- **Algorithms**: NetworkX (Dijkstra's), Custom greedy optimizer
- **Data Processing**: Pandas, JSON
- **Server**: Uvicorn with auto-reload
- **Testing**: pytest, httpx

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite 5.4
- **Styling**: Tailwind CSS 3.4
- **HTTP Client**: Axios
- **State Management**: React Hooks (useState, useEffect)
- **Visualization**: SVG-based interactive floor maps

### DevOps
- **Containerization**: Docker & Docker Compose
- **Deployment**: Ready for AWS, GCP, Heroku, Vercel
- **Documentation**: OpenAPI/Swagger UI

## 📖 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Start both backend and frontend
docker-compose up --build

# Or run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Access points:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Manual Setup

#### Backend Setup

```bash
cd backend

# Install dependencies
pip install fastapi uvicorn sqlalchemy pydantic networkx

# Extract data and seed database
python scripts/extract_pdf_data.py
python scripts/seed_database.py

# Run server
python run.py
```

Backend available at: http://localhost:8000

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend available at: http://localhost:5173

### API Examples

```bash
# Health check
curl http://localhost:8000/health

# Get all companies
curl http://localhost:8000/api/v1/companies/

# Filter by major
curl "http://localhost:8000/api/v1/companies/?major=Chemical%20Engineering"

# Get platinum sponsors
curl "http://localhost:8000/api/v1/companies/?platinum_only=true"

# Optimize route
curl -X POST http://localhost:8000/api/v1/routing/optimize/ \
  -H "Content-Type: application/json" \
  -d '{"company_ids":[1,2,3,4,5],"time_budget_minutes":180}'
```

## 🎯 How to Use

### Getting Started
1. **Set Your Profile**: Click the "Update Profile" button to enter your major and time budget
2. **Browse Companies**: Use the search bar and filters to find companies recruiting for your major
3. **Select Companies**: Click on company cards or booths on the map to select them
4. **Optimize Route**: Set your time budget and click "Optimize Route" to get the best itinerary
5. **Follow Your Plan**: Use the step-by-step itinerary with arrival times and locations

### Key Features

#### Company Search & Filtering
- Search by company name
- Filter by major (32+ engineering disciplines)
- Filter by position type (Full-Time, Internships, Co-Op)
- Filter by ballroom location (Waldorf, Imperial, Grand)
- View platinum sponsors

#### Interactive Floor Map
- Visual representation of booth locations
- Color-coded booths (selected = blue, available = gray)
- Zoom controls for better navigation
- Switch between ballrooms
- Click booths to toggle selection

#### Route Optimization
- Input your time budget (in minutes)
- Algorithm maximizes companies visited within time constraint
- Shows step-by-step itinerary with:
  - Walking times between booths
  - Estimated arrival times
  - Expected service times
  - Total route duration

## 🎓 Use Cases

1. **Targeted Search**: "I'm a Mechanical Engineering student looking for internships"
2. **Time Optimization**: "I only have 2 hours, which companies should I visit?"
3. **Comprehensive Planning**: "I want to visit all platinum sponsors first"
4. **Location-Based**: "Show me all companies in the Waldorf ballroom"
5. **Career Exploration**: "What companies hire Software Engineers?"

## 📈 Performance

- **API Response**: < 100ms for company queries
- **Route Optimization**: < 500ms for 20 companies
- **Graph Building**: < 1s for 21 booths
- **Database**: ~50KB SQLite

## 📝 Documentation

- **[Plan.md](Plan.md)** - Complete system architecture and design
- **[PROGRESS.md](PROGRESS.md)** - Development milestones and achievements
- **[ISSUES.md](ISSUES.md)** - Known issues and resolutions
- **[backend/README.md](backend/README.md)** - Backend API documentation

## 🔜 Roadmap

### Phase 1: Backend MVP ✅ COMPLETED
- REST API with FastAPI
- Database models and seeding
- Route optimization algorithms
- Company scoring system

### Phase 2: Frontend MVP ✅ COMPLETED
- React + TypeScript application
- Interactive floor map
- Company search and filtering
- Route planner interface
- User profile management

### Phase 3: Enhanced Features (Future)
1. **Resume Intelligence**
   - PDF resume upload and parsing
   - AI-powered resume tailoring for each company
   - ATS compatibility checking

2. **NLP & AI Features**
   - Company-specific talking points generation
   - Interview question prediction
   - Personalized conversation starters

3. **Data Enrichment**
   - Web scraping for company details
   - News aggregation and summarization
   - Glassdoor/LinkedIn integration

4. **Advanced Optimization**
   - OR-Tools for complex route optimization
   - Multi-day career fair planning
   - Dynamic re-routing based on real-time data

5. **Real-time Features**
   - Queue tracking via BLE/QR codes
   - Live booth availability updates
   - Push notifications for route adjustments

## 🤝 Contributing

This is a student project for UH Engineering Career Fair. Currently in active development.

## 📄 License

Educational use only.

## 🔗 Links

### Development
- **Frontend Application**: http://localhost:5173 (dev) / http://localhost:3000 (Docker)
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **GitHub Repository**: https://github.com/aish1999999/CF_Copilot

### Documentation
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide for production
- **[Plan.md](Plan.md)** - Original system architecture and design
- **[PROGRESS.md](PROGRESS.md)** - Development milestones and achievements
- **[ISSUES.md](ISSUES.md)** - Known issues and troubleshooting

---

**Built with ❤️ for UH Engineering students**

**Tech Stack**: FastAPI • React • TypeScript • Tailwind CSS • SQLite • NetworkX • Docker

**Algorithms**: Dijkstra's Shortest Path • Greedy Route Optimization • Multi-Factor Scoring