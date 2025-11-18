# CF_Copilot Deployment Guide

Complete guide for deploying the Career Fair Copilot application.

## Quick Start (Development)

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### Option 1: Manual Setup

#### Backend
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

Backend will be available at: http://localhost:8000

#### Frontend
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at: http://localhost:5173

### Option 2: Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Production Deployment

### Environment Variables

Create `.env` file in the root directory:

```env
# Backend
DATABASE_URL=postgresql://user:password@localhost/cf_copilot
DEBUG=False
AVG_WALKING_SPEED_MPS=1.4
AVG_INTERACTION_TIME_MIN=5.0

# Frontend
VITE_API_URL=https://your-api-domain.com/api/v1
```

### Building for Production

#### Backend

```bash
cd backend

# Install production dependencies
pip install -r requirements.txt

# Collect static files (if any)
# Set up PostgreSQL database
export DATABASE_URL="postgresql://user:password@localhost/cf_copilot"

# Run with production server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Frontend

```bash
cd frontend

# Build for production
npm run build

# The dist/ directory contains the production build
# Serve with any static file server (nginx, Apache, etc.)
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### Docker Production Deployment

1. **Build images:**
```bash
docker build -t cf-copilot-backend ./backend
docker build -t cf-copilot-frontend ./frontend
```

2. **Run with docker-compose:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. **Use with orchestration (Kubernetes, ECS, etc.):**
   - Create deployment manifests
   - Set up load balancers
   - Configure auto-scaling
   - Set up monitoring

## Cloud Deployment Options

### AWS

**Option 1: Elastic Beanstalk**
- Upload Docker configuration
- Set environment variables
- Deploy

**Option 2: ECS + ALB**
- Push images to ECR
- Create ECS task definitions
- Set up Application Load Balancer
- Configure auto-scaling

**Option 3: EC2**
- Launch EC2 instance
- Install Docker
- Run docker-compose

### Google Cloud Platform

**Cloud Run:**
```bash
# Build and push backend
gcloud builds submit --tag gcr.io/PROJECT_ID/cf-copilot-backend ./backend
gcloud run deploy cf-copilot-backend --image gcr.io/PROJECT_ID/cf-copilot-backend

# Build and push frontend
gcloud builds submit --tag gcr.io/PROJECT_ID/cf-copilot-frontend ./frontend
gcloud run deploy cf-copilot-frontend --image gcr.io/PROJECT_ID/cf-copilot-frontend
```

### Heroku

**Backend:**
```bash
cd backend
heroku create cf-copilot-api
git push heroku main
```

**Frontend:**
- Deploy to Netlify, Vercel, or Cloudflare Pages
- Point API calls to Heroku backend

### Vercel (Frontend Only)

```bash
cd frontend
vercel deploy --prod
```

Update `vite.config.ts` to point to your backend URL.

## Database Migration

### SQLite to PostgreSQL

1. Export data from SQLite:
```bash
sqlite3 cf_copilot.db .dump > dump.sql
```

2. Import to PostgreSQL:
```bash
psql -U user -d cf_copilot -f dump.sql
```

3. Update `DATABASE_URL` environment variable

### Automated Migrations

Using Alembic:
```bash
cd backend
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Monitoring & Logging

### Application Monitoring

**Prometheus + Grafana:**
- Add prometheus-fastapi-instrumentator
- Set up Grafana dashboards
- Monitor API response times, error rates

**Sentry:**
```python
# backend/app/main.py
import sentry_sdk

sentry_sdk.init(dsn="your-dsn-here")
```

### Logging

**Backend:**
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

**View logs:**
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Performance Optimization

### Backend
- Enable caching with Redis
- Use connection pooling for database
- Implement rate limiting
- Enable gzip compression

### Frontend
- Code splitting
- Lazy loading components
- Image optimization
- CDN for static assets

### Database
- Add indexes on frequently queried fields
- Use database query optimization
- Set up read replicas for scaling

## Security Checklist

- [ ] Enable HTTPS (SSL/TLS certificates)
- [ ] Set secure CORS origins
- [ ] Use environment variables for secrets
- [ ] Enable rate limiting
- [ ] Implement authentication (if needed)
- [ ] Regular dependency updates
- [ ] Database backups
- [ ] Input validation and sanitization
- [ ] SQL injection prevention (using ORM)
- [ ] XSS protection

## Backup & Recovery

### Database Backup

**Automated backups:**
```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
pg_dump -U user cf_copilot > backup_$DATE.sql
```

**Restore:**
```bash
psql -U user -d cf_copilot < backup_YYYYMMDD.sql
```

## Troubleshooting

### Backend won't start
- Check Python version (3.11+)
- Verify all dependencies installed
- Check database connection
- Review logs: `docker-compose logs backend`

### Frontend build fails
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node version (18+)
- Verify API endpoint configuration

### Database connection errors
- Verify DATABASE_URL format
- Check database server is running
- Ensure correct credentials

### CORS errors
- Update CORS origins in backend config.py
- Verify frontend URL matches allowed origins

## Scaling

### Horizontal Scaling
- Run multiple backend instances
- Use load balancer (nginx, AWS ALB)
- Redis for shared session storage

### Vertical Scaling
- Increase server resources
- Optimize database queries
- Add caching layer

## CI/CD Pipeline

### GitHub Actions Example

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and deploy
        run: |
          docker build -t cf-copilot-backend ./backend
          docker build -t cf-copilot-frontend ./frontend
          # Push to registry
          # Deploy to server
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/aish1999999/CF_Copilot/issues
- Documentation: See Plan.md and PROGRESS.md

---

**Last Updated**: November 18, 2025
