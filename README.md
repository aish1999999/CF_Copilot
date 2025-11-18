# CF_Copilot - Career Fair Copilot

An intelligent career fair navigation and optimization system for University of Houston Engineering & Technology Career Fair.

## 🎯 Project Status

**Phase 1 (Backend MVP): COMPLETED ✅**
- Fully functional REST API
- 21 companies from Fall 2025 ETCF
- Intelligent routing optimization
- Company scoring system
- Database seeded and tested

**Phase 2 (Frontend): Pending**

## 🚀 Features

### Current (Backend)
- ✅ Company search and filtering by major, position type, ballroom
- ✅ Intelligent route optimization (greedy heuristic)
- ✅ Dijkstra's algorithm for shortest paths
- ✅ Company scoring based on user profile
- ✅ Real-time queue length updates
- ✅ User profile management
- ✅ Time-constrained booth visit planning

### Planned (Frontend)
- 🔲 Interactive floor map visualization
- 🔲 Company cards with detailed information
- 🔲 Route planner with drag-and-drop
- 🔲 Manual booth selection
- 🔲 Priority-based routing
- 🔲 Resume upload and tailoring
- 🔲 Talking points generation

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
│   │   ├── models/      # Database models
│   │   ├── routes/      # API endpoints
│   │   └── services/    # Business logic
│   ├── scripts/         # Data extraction & seeding
│   └── tests/           # Unit tests
├── frontend/            # React app (Pending)
├── data/
│   ├── raw/            # PDF booklets
│   └── processed/      # Extracted JSON data
├── Plan.md             # Comprehensive system design
├── PROGRESS.md         # Development progress
└── ISSUES.md           # Known issues tracking
```

## 🛠️ Technology Stack

### Backend (Implemented)
- **Framework**: FastAPI
- **Database**: SQLite (SQLAlchemy ORM)
- **Algorithms**: NetworkX (graphs), Custom greedy optimizer
- **Data Processing**: Pandas, JSON

### Frontend (Planned)
- **Framework**: React with TypeScript
- **Styling**: Tailwind CSS
- **State**: React Context API
- **Visualization**: SVG/Canvas for maps

## 📖 Quick Start

### Backend Setup

```bash
# Navigate to backend
cd backend

# Install dependencies
pip install fastapi uvicorn sqlalchemy pydantic networkx

# Extract data from PDFs
python scripts/extract_pdf_data.py

# Seed database
python scripts/seed_database.py

# Run server
python run.py
```

Server will be available at: http://localhost:8000
API docs: http://localhost:8000/docs

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

## 🎓 Use Cases

1. **Manual Booth Selection**: Select companies you want to visit, get optimized route
2. **Time-Constrained Planning**: Maximize companies visited within time budget
3. **Major-Based Filtering**: Find companies recruiting for your major
4. **Queue-Aware Routing**: Dynamically adjust route based on queue lengths
5. **Priority Routing**: Prioritize platinum sponsors or preferred companies

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

## 🔜 Next Steps

### Immediate (Phase 2)
1. Create React frontend application
2. Implement company list with search/filter
3. Build interactive floor map
4. Create route planner UI
5. Add user profile interface

### Future (Phase 3+)
1. Resume parsing and tailoring
2. NLP-based talking points
3. Web scraping for company details
4. News aggregation
5. Advanced optimization (OR-Tools)
6. Real-time queue tracking via BLE/QR

## 🤝 Contributing

This is a student project for UH Engineering Career Fair. Currently in active development.

## 📄 License

Educational use only.

## 🔗 Links

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **GitHub**: https://github.com/aish1999999/CF_Copilot

---

**Built with ❤️ for UH Engineering students**
**Powered by FastAPI, React, and intelligent algorithms**