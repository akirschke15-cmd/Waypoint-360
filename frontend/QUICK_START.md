# Waypoint 360 Frontend - Quick Start

## Installation

```bash
cd frontend
npm install
```

## Development Server

```bash
npm run dev
```

Starts Vite dev server at `http://localhost:5173`

- Hot module reloading enabled
- API calls proxied to `http://localhost:8000/api`

## Build for Production

```bash
npm run build
```

Outputs optimized production bundle to `dist/`

## Type Checking

```bash
npm run lint
```

Validates TypeScript without emitting files.

## Project Layout

```
src/
├── components/          # React components (6 pages)
├── services/api.ts      # Axios API client
├── types/index.ts       # TypeScript interfaces
├── themes/index.ts      # Theme system
├── App.tsx              # Main app with routing
├── main.tsx             # React entry point
└── index.css            # Global styles + Tailwind
```

## Key Features

- **CommandCenter**: Executive dashboard with program status, KPIs, blockers
- **GateTimeline**: Visual timeline of program gates and readiness criteria
- **DependencyGraph**: D3.js visualization of workstream dependencies
- **RiskHeatMap**: Risk assessment with probability/impact matrix
- **Workstream Details**: Detailed view of deliverables, team, risks, decisions
- **Workstream Form**: Create new workstreams with validation

## API Integration

Backend API expected at `/api/v1`:

- Program metadata
- Workstreams CRUD
- Gates and timeline
- Dependencies & critical path
- AI-assisted analysis (executive summary, scope creep, risk correlation)

See `src/services/api.ts` for all endpoints.

## Theme Customization

Default: SWA theme (blue #304CB2, gold #FFBF00, red #C8102E)

Switch themes:
```tsx
import { useTheme } from '@/themes';

const { setTheme } = useTheme();
setTheme('neutral');  // or 'swa'
```

## Styling

Tailwind CSS with custom utilities:
- `.card` - Card component
- `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-danger`
- `.badge`, `.badge-success`, `.badge-warning`, `.badge-error`, `.badge-info`
- `.input`, `.label` - Form elements
- `.grid-responsive` - Responsive grid

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Requirements

- Node.js 18+
- npm or yarn

## Debugging

Enable React DevTools Chrome extension for debugging components and hooks.

Network requests: Open Chrome DevTools > Network tab to inspect API calls.

## Production Deployment

1. `npm run build` produces `dist/` folder
2. Deploy `dist/` as static files to web server
3. Configure API base URL if not `/api/v1`
4. Ensure CORS headers allow frontend origin
