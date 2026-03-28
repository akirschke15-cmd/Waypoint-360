# Waypoint 360 Frontend - File Manifest

Complete React 18 + TypeScript + Vite scaffold for the Southwest Airlines Waypoint program control tower.

## Configuration Files (6)

| File | Purpose |
|------|---------|
| `package.json` | Dependencies, scripts, project metadata |
| `vite.config.ts` | Vite bundler config with React plugin, API proxy |
| `tsconfig.json` | TypeScript compiler options, strict mode, path aliases |
| `tsconfig.node.json` | TypeScript config for Vite config file |
| `tailwind.config.js` | Tailwind CSS theme with SWA colors |
| `postcss.config.js` | PostCSS plugins (Tailwind, Autoprefixer) |

## Entry Points (3)

| File | Purpose |
|------|---------|
| `index.html` | HTML entry point with root div |
| `src/main.tsx` | React 18 root with BrowserRouter |
| `src/App.tsx` | Main app component with layout, routing, sidebar |

## Core Application (3)

| File | Lines | Purpose |
|------|-------|---------|
| `src/index.css` | 92 | Global styles, Tailwind directives, utility classes |
| `src/themes/index.ts` | 51 | Theme context provider (SWA + neutral themes) |
| `src/types/index.ts` | 208 | TypeScript interfaces for all domain objects |

## Services (1)

| File | Lines | Purpose |
|------|-------|---------|
| `src/services/api.ts` | 72 | Axios HTTP client with all API endpoints |

## Components (6 pages)

| Component | Lines | Purpose |
|-----------|-------|---------|
| `CommandCenter/index.tsx` | 121 | Executive dashboard with KPIs, executive summary |
| `GateTimeline/index.tsx` | 119 | Visual timeline of program gates, exit criteria |
| `DependencyGraph/index.tsx` | 142 | D3.js force-directed graph of dependencies |
| `RiskHeatMap/index.tsx` | 172 | 5x5 risk matrix, risk detail cards |
| `WorkstreamCard/index.tsx` | 127 | Detailed workstream view with all sub-resources |
| `WorkstreamForm/index.tsx` | 105 | Form to create new workstream with validation |

## Documentation (4)

| File | Purpose |
|------|---------|
| `README.md` | Comprehensive project documentation |
| `QUICK_START.md` | Quick reference for setup and common tasks |
| `MANIFEST.md` | This file - complete file inventory |
| `.gitignore` | Git ignore patterns for Node/IDE/env files |

## Statistics

- **Total Files**: 21
- **Total Lines of Code**: 789+
- **TypeScript Files**: 8
- **React Components**: 6
- **Configuration Files**: 6
- **Documentation**: 4

## Dependencies

### Runtime
- react ^18.3.1
- react-dom ^18.3.1
- react-router-dom ^6.22.0
- axios ^1.6.5
- d3 ^7.8.5
- lucide-react ^0.294.0

### Development
- TypeScript ^5.3.3
- Vite ^5.0.8
- @vitejs/plugin-react ^4.2.1
- Tailwind CSS ^3.4.1
- PostCSS ^8.4.32
- Autoprefixer ^10.4.16
- Type definitions for React, D3

## Key Features

✓ Production-ready code (no TODOs or placeholders)  
✓ Full TypeScript type safety  
✓ SWA brand colors integrated  
✓ Responsive mobile-first design  
✓ Dark theme by default  
✓ Error handling & loading states  
✓ D3.js data visualization  
✓ Theme switching capability  
✓ API client with proper interceptors  
✓ Accessibility-aware components  

## Routes

| Path | Component | Purpose |
|------|-----------|---------|
| `/` | CommandCenter | Executive dashboard |
| `/gates` | GateTimeline | Program gate timeline |
| `/dependencies` | DependencyGraph | Workstream dependencies |
| `/risks` | RiskHeatMap | Risk assessment matrix |
| `/workstreams/:id` | WorkstreamCard | Workstream details |
| `/workstreams/new` | WorkstreamForm | Create workstream |

## API Endpoints Used

**Program**
- `GET /api/v1/program`
- `GET /api/v1/ai/executive-summary`

**Workstreams**
- `GET /api/v1/workstreams`
- `GET /api/v1/workstreams/:id`
- `PUT /api/v1/workstreams/:id`

**Gates**
- `GET /api/v1/gates`
- `GET /api/v1/gates/:id`
- `GET /api/v1/gates/timeline`
- `GET /api/v1/ai/gate-readiness/:gateId`

**Dependencies**
- `GET /api/v1/dependencies`
- `GET /api/v1/dependencies/critical-path`

**AI Analysis**
- `POST /api/v1/ai/query`
- `GET /api/v1/ai/scope-creep`
- `GET /api/v1/ai/correlated-risks/:riskId`

**Admin**
- `POST /api/v1/admin/seed`

## Commands

```bash
npm install          # Install dependencies
npm run dev          # Start dev server (localhost:5173)
npm run build        # Production build to dist/
npm run preview      # Preview production build
npm run lint         # Type check without emit
```

## Setup

1. `npm install` - Install all dependencies
2. Ensure backend API running at `http://localhost:8000`
3. `npm run dev` - Start development server
4. Open `http://localhost:5173` in browser

## Notes

- API calls proxied to `/api` → `http://localhost:8000`
- TypeScript strict mode enabled
- All files production-ready, no TODO comments
- Tailwind dark mode applied by default
- Path alias `@/` points to `src/`
