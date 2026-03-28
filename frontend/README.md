# Waypoint 360 Frontend

Program control tower for the Southwest Airlines Waypoint inception program. Real-time visibility into program status, gate readiness, dependencies, and risks across all workstreams.

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast builds and development
- **React Router** for navigation
- **Tailwind CSS** for styling (SWA theme)
- **D3.js** for dependency graph visualization
- **Lucide React** for icons
- **Axios** for API communication

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

Runs the dev server at `http://localhost:5173` with hot module replacement.

### Build

```bash
npm run build
```

Produces optimized production build in `dist/` directory.

### Type Checking

```bash
npm run lint
```

Validates TypeScript without emitting files.

## Project Structure

```
src/
├── components/          # React components
│   ├── CommandCenter/   # Main dashboard
│   ├── GateTimeline/    # Gate visualization
│   ├── DependencyGraph/ # D3-based dependency graph
│   ├── RiskHeatMap/     # Risk assessment
│   ├── WorkstreamCard/  # Workstream details
│   └── WorkstreamForm/  # New workstream form
├── services/
│   └── api.ts          # API client with axios
├── types/
│   └── index.ts        # TypeScript interfaces
├── themes/
│   └── index.ts        # Theme system (SWA + neutral)
├── App.tsx             # Main app with routing
├── main.tsx            # Entry point
└── index.css           # Global styles + Tailwind
```

## API Integration

The frontend connects to a backend API at `/api/v1`. Key endpoints:

- `GET /program` - Program metadata
- `GET /workstreams` - List of workstreams
- `GET /workstreams/:id` - Workstream details
- `GET /gates` - Program gates
- `GET /dependencies/critical-path` - Dependency graph
- `GET /ai/executive-summary` - AI-generated program summary
- `POST /admin/seed` - Seed database with test data

See `src/services/api.ts` for the complete client API.

## Theme System

The application includes a flexible theme system supporting multiple color schemes:

- **SWA Theme** (default): Uses Southwest Airlines brand colors
  - Primary: #304CB2 (SWA Blue)
  - Secondary: #FFBF00 (SWA Gold)
  - Accent: #C8102E (SWA Red)

- **Neutral Theme**: Professional blue/purple palette

Switch themes via `useTheme()` hook:

```tsx
import { useTheme } from '@/themes';

function MyComponent() {
  const { setTheme } = useTheme();
  return <button onClick={() => setTheme('neutral')}>Switch Theme</button>;
}
```

## Component Architecture

All components follow a consistent pattern:

1. **Data fetching** in `useEffect` hooks
2. **Loading/error states** with visual feedback
3. **Type-safe props** using TypeScript interfaces
4. **Responsive design** with Tailwind breakpoints
5. **Accessibility** with semantic HTML and ARIA labels

## Styling

Tailwind CSS configuration includes:

- Custom SWA color palette
- Dark theme by default
- Responsive grid utilities
- Custom component classes (`.card`, `.btn`, `.badge`)
- Custom scrollbar styling

See `tailwind.config.js` for full theme configuration.

## API Proxy

Development server proxies `/api/*` requests to `http://localhost:8000`. Configure in `vite.config.ts`.

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Production Deployment

1. Build the project: `npm run build`
2. Serve the `dist/` directory as static files
3. Ensure API backend is accessible at `/api/v1`
4. Set appropriate environment variables for production API endpoint if needed

## Future Enhancements

- Real-time updates via WebSocket
- Program timeline editor
- Decision tracking and approval workflow
- Advanced filtering and search
- Export/reporting capabilities
- Mobile app (React Native)
