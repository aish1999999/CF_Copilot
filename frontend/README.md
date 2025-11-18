# CF_Copilot Frontend

React + TypeScript frontend for the Career Fair Copilot application.

## Features

- 🎯 Company search and filtering by major, position type, and ballroom
- 🗺️ Interactive floor map visualization
- 🧭 Intelligent route optimization
- 👤 User profile management
- 📱 Fully responsive design
- ⚡ Fast and modern UI with Tailwind CSS

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Axios** - API client
- **Lucide React** - Icons

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on http://localhost:8000

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at http://localhost:5173

### Build for Production

```bash
npm run build
npm run preview
```

## Project Structure

```
src/
├── components/          # React components
│   ├── CompanyCard.tsx
│   ├── CompanyList.tsx
│   ├── FilterPanel.tsx
│   ├── FloorMap.tsx
│   ├── RoutePlanner.tsx
│   └── UserProfileModal.tsx
├── services/            # API client
│   └── api.ts
├── types/               # TypeScript types
│   └── index.ts
├── App.tsx              # Main app component
└── main.tsx             # Entry point
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## API Integration

The frontend communicates with the FastAPI backend through Axios. The API base URL is configured in `src/services/api.ts`.

### Key Endpoints Used

- `GET /api/v1/companies/` - Fetch companies with filters
- `GET /api/v1/companies/filters/*` - Get filter options
- `GET /api/v1/booths/` - Get booth locations
- `POST /api/v1/routing/optimize/` - Optimize route

## Features

### Company Discovery
- Search companies by name
- Filter by major, position type, ballroom
- View platinum sponsors
- See company details and booth locations

### Route Planning
- Select companies to visit
- Set time budget
- Generate optimized route
- View step-by-step itinerary with timing

### Floor Map
- Interactive SVG map of booths
- Visual booth selection
- Zoom controls
- Queue indicators

### User Profile
- Set major and experience level
- Configure time budget
- Personalized recommendations (coming soon)

## Styling

This project uses Tailwind CSS for styling. The configuration is in `tailwind.config.js`. Custom colors and utilities are defined for the primary brand color.

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## License

Educational use only.
