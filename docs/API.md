# CF_Copilot API Documentation

Comprehensive API documentation for the Career Fair Copilot backend service.

**Base URL**: `http://localhost:8000`
**API Version**: v1
**API Prefix**: `/api/v1`

---

## Table of Contents

1. [Authentication](#authentication)
2. [Companies](#companies)
3. [Booths](#booths)
4. [Users](#users)
5. [Routing & Optimization](#routing--optimization)
6. [NLP Services](#nlp-services)
7. [Web Scraping](#web-scraping)
8. [Export](#export)
9. [Error Handling](#error-handling)
10. [Rate Limiting](#rate-limiting)

---

## Authentication

### POST `/token`

Obtain JWT access token for authentication.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass"
```

### GET `/auth/google`

Initiate Google OAuth flow.

**Response:** Redirects to Google OAuth consent screen

---

## Companies

### GET `/api/v1/companies/`

Get list of all companies at the career fair.

**Query Parameters:**
- `major` (optional): Filter by recruiting major
- `position_type` (optional): Filter by position type (Full-Time, Internship, Co-Op)
- `ballroom` (optional): Filter by ballroom location
- `platinum_only` (optional): Filter platinum sponsors only (boolean)

**Response:**
```json
[
  {
    "id": 1,
    "name": "TechCorp Solutions",
    "booth_number": "101",
    "ballroom": "Waldorf",
    "recruiting_majors": ["Computer Science", "Software Engineering"],
    "position_types": ["Full-Time", "Internship"],
    "is_platinum_sponsor": true,
    "coordinate_x": 10.0,
    "coordinate_y": 10.0,
    "description": "Leading technology company...",
    "website": "https://techcorp.example.com"
  }
]
```

**Examples:**
```bash
# Get all companies
curl "http://localhost:8000/api/v1/companies/"

# Filter by major
curl "http://localhost:8000/api/v1/companies/?major=Computer%20Science"

# Filter by position type
curl "http://localhost:8000/api/v1/companies/?position_type=Internship"

# Platinum sponsors only
curl "http://localhost:8000/api/v1/companies/?platinum_only=true"
```

### GET `/api/v1/companies/{company_id}`

Get details for a specific company.

**Path Parameters:**
- `company_id`: Company ID (integer)

**Response:**
```json
{
  "id": 1,
  "name": "TechCorp Solutions",
  "booth_number": "101",
  "ballroom": "Waldorf",
  "recruiting_majors": ["Computer Science"],
  "position_types": ["Full-Time", "Internship"],
  "is_platinum_sponsor": true,
  "coordinate_x": 10.0,
  "coordinate_y": 10.0
}
```

---

## Booths

### GET `/api/v1/booths/`

Get all booth locations.

**Response:**
```json
[
  {
    "booth_number": "101",
    "ballroom": "Waldorf",
    "coordinate_x": 10.0,
    "coordinate_y": 10.0,
    "company_id": 1
  }
]
```

### GET `/api/v1/booths/{booth_number}`

Get specific booth details.

---

## Users

### POST `/api/v1/users/`

Create a new user profile.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "major": "Computer Science",
  "graduation_year": 2025,
  "time_budget_minutes": 120,
  "preferred_position_types": ["Internship"]
}
```

### GET `/api/v1/users/{user_id}`

Get user profile.

### PUT `/api/v1/users/{user_id}`

Update user profile.

---

## Routing & Optimization

### POST `/api/v1/routing/optimize/`

Optimize route for selected companies.

**Request Body:**
```json
{
  "company_ids": [1, 2, 3, 4, 5],
  "time_budget_minutes": 120,
  "start_location": "entrance",
  "avg_interaction_time": 5.0,
  "algorithm": "greedy"
}
```

**Algorithms:**
- `greedy`: Fast greedy heuristic (default)
- `ilp`: Integer Linear Programming (exact, slower)
- `simulated_annealing`: Metaheuristic optimization
- `genetic`: Genetic algorithm

**Response:**
```json
{
  "route": [
    {
      "company_id": 1,
      "booth_number": "101",
      "travel_time": 2.0,
      "service_time": 5.0,
      "arrival_time": 2.0,
      "score": 10.0
    },
    {
      "company_id": 3,
      "booth_number": "103",
      "travel_time": 1.5,
      "service_time": 5.0,
      "arrival_time": 8.5,
      "score": 8.0
    }
  ],
  "total_time": 28.5,
  "total_score": 27.0,
  "companies_visited": 3,
  "time_remaining": 91.5
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/routing/optimize/" \
  -H "Content-Type: application/json" \
  -d '{
    "company_ids": [1,2,3],
    "time_budget_minutes": 60,
    "algorithm": "greedy"
  }'
```

### POST `/api/v1/routing/replan/`

Replan route based on real-time changes.

**Request Body:**
```json
{
  "current_route": [...],
  "current_position": 2,
  "reason": "delay",
  "delay_minutes": 10,
  "time_budget_minutes": 120
}
```

**Replan Reasons:**
- `delay`: Time delay occurred
- `queue_change`: Queue lengths changed
- `booth_closure`: Booth closed
- `priority_addition`: Add high-priority company

---

## NLP Services

### POST `/api/v1/nlp/parse-resume`

Parse PDF resume and extract structured data.

**Request:**
- Content-Type: `multipart/form-data`
- Body: PDF file upload

**Response:**
```json
{
  "success": true,
  "personal_info": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "(123) 456-7890"
  },
  "education": [
    {
      "degree": "B.S. Computer Science",
      "institution": "University of Houston",
      "graduation_year": "2024"
    }
  ],
  "experience": [...],
  "skills": ["Python", "JavaScript", "React"],
  "projects": [...]
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/nlp/parse-resume" \
  -F "file=@resume.pdf"
```

### POST `/api/v1/nlp/tailor-resume`

Tailor resume to match job description.

**Request Body:**
```json
{
  "resume_text": "Resume content...",
  "job_description": "Job description...",
  "company_name": "TechCorp"
}
```

**Response:**
```json
{
  "success": true,
  "match_score": 75.5,
  "matched_skills": ["Python", "React", "AWS"],
  "missing_skills": ["Kubernetes", "Docker"],
  "suggestions": [
    "Add Kubernetes if you have experience",
    "Highlight cloud platform experience"
  ],
  "ats_score": 85.0
}
```

### POST `/api/v1/nlp/generate-talking-points`

Generate personalized talking points for a company.

**Request Body:**
```json
{
  "company_name": "TechCorp",
  "company_info": {
    "name": "TechCorp",
    "recruiting_majors": ["Computer Science"],
    "keywords": ["AI", "Cloud"]
  },
  "resume_data": {...},
  "job_description": "...",
  "news_articles": [...]
}
```

**Response:**
```json
{
  "success": true,
  "company_name": "TechCorp",
  "talking_points": [
    "Mention experience with Python and AI",
    "Highlight cloud platform projects"
  ],
  "questions_to_ask": [
    "What technologies does your team use for AI?",
    "What's the engineering culture like at TechCorp?"
  ],
  "conversation_starters": [
    "I'm excited about TechCorp's work in AI..."
  ],
  "key_topics": ["AI", "Cloud Computing", "Python"]
}
```

---

## Web Scraping

### POST `/api/v1/scraping/scrape-company`

Scrape company information from public sources.

**Request Body:**
```json
{
  "company_name": "TechCorp Solutions",
  "website_url": "https://techcorp.example.com",
  "linkedin_url": "https://linkedin.com/company/techcorp"
}
```

**Response:**
```json
{
  "success": true,
  "company_name": "TechCorp Solutions",
  "description": "Leading technology company...",
  "industry": "Technology",
  "size": "1000-5000 employees",
  "headquarters": "San Francisco, CA",
  "benefits": ["Health Insurance", "401k"],
  "scraped_at": "2024-01-18T12:00:00"
}
```

### POST `/api/v1/scraping/scrape-news`

Scrape recent news about a company.

**Request Body:**
```json
{
  "company_name": "TechCorp",
  "days_back": 30,
  "max_articles": 10
}
```

**Response:**
```json
{
  "success": true,
  "company_name": "TechCorp",
  "articles": [
    {
      "title": "TechCorp Launches New AI Platform",
      "source": "Tech News",
      "published_date": "2024-01-15",
      "url": "..."
    }
  ]
}
```

### POST `/api/v1/scraping/scrape-jobs`

Scrape job postings for a company.

**Request Body:**
```json
{
  "company_name": "TechCorp",
  "position_types": ["Internship", "Full-Time"],
  "max_jobs": 20
}
```

---

## Export

### POST `/api/v1/export/route-pdf`

Export route itinerary as PDF.

**Request Body:**
```json
{
  "route": [...],
  "user_name": "John Doe",
  "total_time": 60.0,
  "total_score": 85.0,
  "companies_visited": 5,
  "event_name": "UH Engineering Career Fair"
}
```

**Response:** PDF file download

### POST `/api/v1/export/route-csv`

Export route itinerary as CSV.

**Response:** CSV file download

### POST `/api/v1/export/talking-points-pdf`

Export talking points as PDF.

---

## Error Handling

All API endpoints follow standard HTTP status codes and return errors in JSON format:

```json
{
  "error": "Error type",
  "detail": "Detailed error message",
  "timestamp": 1705584000.0
}
```

### HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Error Examples

```json
{
  "error": "Invalid input",
  "detail": "time_budget_minutes must be positive",
  "timestamp": 1705584000.0
}
```

---

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

- **Default limit**: 100 requests per minute per IP
- **Scraping endpoints**: 10 requests per minute
- **Export endpoints**: 20 requests per minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705584060
```

---

## Pagination

Endpoints returning lists support pagination:

**Query Parameters:**
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20, max: 100)

**Response:**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5
  }
}
```

---

## WebSocket Endpoints

### `/ws/routing`

Real-time routing updates via WebSocket.

**Connect:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/routing');
```

**Messages:**
```json
{
  "type": "route_update",
  "data": {
    "route": [...],
    "update_reason": "queue_change"
  }
}
```

---

## Health & Metrics

### GET `/health`

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### GET `/metrics`

Get API metrics (admin only).

**Response:**
```json
{
  "total_requests": 1500,
  "avg_duration": 0.234,
  "endpoints": {
    "GET /api/v1/companies/": {
      "count": 500,
      "avg_duration": 0.150
    }
  }
}
```

---

## Best Practices

1. **Authentication**: Include bearer token in Authorization header for protected endpoints
2. **Content-Type**: Set `Content-Type: application/json` for JSON requests
3. **Error Handling**: Always check response status code and handle errors gracefully
4. **Rate Limits**: Implement exponential backoff when rate limited
5. **Caching**: Cache company data to reduce API calls
6. **Pagination**: Use pagination for large datasets

---

## SDKs & Client Libraries

### Python
```python
from cf_copilot import CFCopilotClient

client = CFCopilotClient(
    base_url="http://localhost:8000",
    api_key="your_api_key"
)

# Get companies
companies = client.companies.list(major="Computer Science")

# Optimize route
route = client.routing.optimize(
    company_ids=[1, 2, 3],
    time_budget=120
)
```

### JavaScript
```javascript
import { CFCopilot } from 'cf-copilot-js';

const client = new CFCopilot({
  baseURL: 'http://localhost:8000',
  apiKey: 'your_api_key'
});

// Get companies
const companies = await client.companies.list({
  major: 'Computer Science'
});

// Optimize route
const route = await client.routing.optimize({
  companyIds: [1, 2, 3],
  timeBudget: 120
});
```

---

## Support

For API support and questions:
- **Documentation**: https://docs.cfcopilot.com
- **GitHub Issues**: https://github.com/aish1999999/CF_Copilot/issues
- **Email**: support@cfcopilot.com

---

**Last Updated**: 2025-01-18
**API Version**: 1.0.0
