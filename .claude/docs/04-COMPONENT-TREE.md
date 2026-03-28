# Waypoint 360 - Component Tree & Design System

> Full React 18 component hierarchy with Tailwind design tokens, component specifications, props interfaces, and routing structure. 6 main views, 7+ shared components, deterministic navigation model, dark-first UI.

## Design Tokens

All tokens defined in `/frontend/src/themes/index.ts` with Tailwind Config extension in `/frontend/tailwind.config.js`.

### Colors (Tailwind CSS)

**SWA Brand Palette**
| Token | Tailwind Class | Hex Value | Usage |
|-------|---|---|---|
| Primary | `swa-blue` | `#304CB2` | Headers, active nav, primary buttons, accents |
| Secondary | `swa-gold` | `#FFBF00` | Highlights, badges, secondary actions |
| Accent | `swa-red` | `#C8102E` | Alerts, critical status, error states |

**Neutral Palette (Dark Theme)**
| Token | Tailwind Class | Hex Value | Usage |
|-------|---|---|---|
| Background | `bg-neutral-900` | `#0f172a` | Page background |
| Surface | `bg-neutral-800` | `#1e293b` | Cards, panels, elevated surfaces |
| Subtle | `bg-neutral-700` | `#334155` | Hover states, secondary surfaces |
| Border | `border-neutral-700` | `#334155` | Card borders, dividers |
| Text Primary | `text-neutral-100` | `#f1f5f9` | Body text, primary content |
| Text Secondary | `text-neutral-400` | `#cbd5e1` | Labels, hints |
| Text Muted | `text-neutral-500` | `#94a3b8` | Timestamps, metadata |

**Semantic Colors**
| Status | Tailwind | Hex | Usage |
|--------|----------|-----|-------|
| Success | `text-green-500` | `#10b981` | Complete, on-track |
| Warning | `text-yellow-500` | `#f59e0b` | At-risk, pending |
| Error | `text-red-500` | `#ef4444` | Blocked, overdue, critical |
| Info | `text-blue-500` | `#3b82f6` | In-progress, neutral info |

### Typography

**Font Stack**: `system-ui, -apple-system, sans-serif` (Tailwind default)

**Heading Scale**
| Level | Tailwind | Size | Font Weight | Usage |
|-------|----------|------|-------------|-------|
| H1 | `text-2xl font-bold` | 24px | 700 | Page titles |
| H2 | `text-lg font-semibold` | 18px | 600 | Section headers |
| H3 | `text-base font-semibold` | 16px | 600 | Card titles |
| Label | `text-sm font-semibold` | 14px | 600 | Field labels |

**Body Text**
| Level | Tailwind | Size | Line Height | Usage |
|-------|----------|------|-------------|-------|
| Body | `text-sm text-neutral-100` | 14px | 1.5 | Primary content |
| Meta | `text-xs text-neutral-500` | 12px | 1.4 | Timestamps, info |
| Caption | `text-[10px] text-neutral-600` | 10px | 1.4 | Muted captions |

### Spacing

**Base Unit**: 4px (Tailwind's default)

| Token | Pixels | Usage |
|-------|--------|-------|
| `p-3` / `gap-3` | 12px | Small gaps, tight spacing |
| `p-4` / `gap-4` | 16px | Standard padding, gaps |
| `p-6` / `gap-6` | 24px | Container padding |
| `p-8` | 32px | Large padding (desktop) |

**Common Patterns**:
- Container padding: `p-6 lg:p-8` (24px mobile, 32px desktop)
- Card padding: `p-4` or `p-6`
- Gap between items: `gap-3` or `gap-4`

### Borders & Shadows

- Border width: `border` (1px)
- Border radius: `rounded-lg` (8px), `rounded-md` (6px)
- Border color: `border-neutral-700` (primary), `border-neutral-600` (hover)
- Shadow: `shadow-lg` (rarely used, dark theme doesn't need shadows)

### Responsive Breakpoints

- Mobile: < 640px (default, no prefix)
- Tablet: 640px+ (`sm:` prefix)
- Desktop: 1024px+ (`lg:` prefix)
- Large: 1280px+ (`xl:` prefix)

Example: `hidden lg:flex` = hidden on mobile, visible on desktop

---

## Component Hierarchy

```
App (ThemeProvider)
│
└── AppLayout (Sidebar + Header + Routes)
    ├── Sidebar (navigation, theme toggle)
    ├── Header (page title, date)
    └── Routes (6 pages)
        ├── / → CommandCenter
        ├── /gates → GateTimeline
        ├── /dependencies → DependencyGraph
        ├── /risks → RiskHeatMap
        ├── /workstreams/:id → WorkstreamCard
        └── /workstreams/new → WorkstreamForm
```

---

## Page Routes & Components

| Route | Component | Purpose | Auth Required |
|-------|-----------|---------|---|
| `/` | `CommandCenter` | Program dashboard, KPIs, AI chat | Yes |
| `/gates` | `GateTimeline` | 4-gate timeline matrix | Yes |
| `/dependencies` | `DependencyGraph` | D3 dependency visualization | Yes |
| `/risks` | `RiskHeatMap` | Risk heatmap with severity/likelihood | Yes |
| `/workstreams/:id` | `WorkstreamCard` | Detailed workstream view & edit | Yes |
| `/workstreams/new` | `WorkstreamForm` | Create new workstream | Yes |

---

## Component Specifications

### Layout Components

#### App (Entry Point)
**Props**: None
**Behavior**: Wraps entire app in `ThemeProvider(defaultTheme="swa")`, renders `AppLayout`

#### AppLayout
**State**:
- `sidebarOpen: boolean` (mobile menu toggle)

**Renders**:
- Flex container with Sidebar (fixed left) + main area (flex-1)
- Header (sticky top) with page title and hamburger (mobile)
- Routes content area with `p-6 lg:p-8` padding

#### Sidebar
**Props**:
```typescript
interface SidebarProps {
  open: boolean;
  setOpen: (open: boolean) => void;
}
```

**Content**:
- Logo: "Waypoint 360" (text-xl font-bold text-swa-blue)
- Subtitle: "Program Control Tower" (text-[10px] uppercase)
- 4 nav links: Dashboard, Gate Timeline, Dependencies, Risks
- Theme toggle button (Palette icon)
- Footer: "Southwest Airlines / AgentOps | Waypoint"

**Styling**: `w-64 bg-neutral-800 border-r border-neutral-700` (fixed on desktop, overlay on mobile)

#### Header
**Content**:
- Hamburger button (mobile only, `lg:hidden`)
- Page title (derived from route)
- Current date formatted

**Styling**: `sticky top-0 z-30 bg-neutral-800/95 border-b border-neutral-700 px-6 py-3 backdrop-blur-sm`

---

### Page Components

#### CommandCenter (/)
**Sections**:
1. Program Banner (name, status, current phase)
2. KPI Cards (6-card grid: workstreams, gate progress, deliverables, at-risk, dependencies, decisions)
3. Workstream List (expandable table: name, owner, status, deliverables %)
4. AI Chat Widget (query input, response panel)
5. Gate Progress Mini (4-gate timeline)
6. Critical Dependencies Alert (if blockers exist)

#### GateTimeline (/gates)
**Sections**:
1. Filter Bar (by gate, workstream, status)
2. Matrix Table (workstreams × gates, expandable cells)
3. Gate Details Sidebar (if gate selected)

#### DependencyGraph (/dependencies)
**Sections**:
1. D3 Force-Directed Graph (nodes=workstreams, links=dependencies)
2. Filter Bar (criticality, status, workstream multiselect)
3. Zoom/Pan Controls (+/-, Reset)
4. Tooltip (hover shows details)
5. Critical Path Alert (if circular deps)
6. Sidebar Details (if node selected)

#### RiskHeatMap (/risks)
**Sections**:
1. Severity × Likelihood Matrix (5×5 grid)
2. Legend (axes, colors)
3. Filter & Sort Bar (status, threshold, sort by)
4. Risk Cards Panel (list below matrix)
5. Risk Details Sidebar (if risk selected)

#### WorkstreamCard (/workstreams/:id)
**Sections** (collapsible):
1. Header (name, status, owner, actions)
2. Scope (baseline, scope in, scope out)
3. Deliverables (table: name, gate, status)
4. Risks (filtered list)
5. Decisions (timeline or list)
6. Dependencies (needs from, provides to)
7. Status Updates (timeline, newest first)
8. Team Members (list, manage button)

**Edit Mode**: Toggles all text fields to editable (textarea for long text), adds Save/Cancel buttons

#### WorkstreamForm (/workstreams/new)
**Fields**:
1. Name (text, required, max 100 chars)
2. Short Name (text, required, max 20 chars, alphanumeric)
3. Purpose (textarea, required, 10-500 chars)
4. Owner (dropdown, optional, searchable)
5. Initial Status (radio/select, optional, default: "Planned")
6. Scope In (textarea, optional, max 1000 chars)
7. Scope Out (textarea, optional, max 1000 chars)

**Buttons**: Submit ("Create Workstream", disabled until required fields filled), Cancel

---

### Shared Components

#### StatusIndicator
**Props**:
```typescript
interface StatusIndicatorProps {
  status: 'complete' | 'on_track' | 'at_risk' | 'blocked' | 'planned';
}
```
**Renders**: Colored dot + label text (e.g., "On Track")

#### Badge
**Props**:
```typescript
interface BadgeProps {
  label: string;
  color?: 'primary' | 'success' | 'warning' | 'error' | 'info';
  size?: 'sm' | 'md' | 'lg';
}
```
**Renders**: `inline-block px-2 py-1 rounded text-xs font-semibold bg-{color} text-white`

#### Card
**Props**:
```typescript
interface CardProps {
  title?: string;
  children: ReactNode;
  footer?: ReactNode;
  onClick?: () => void;
  hoverable?: boolean;
}
```
**Renders**: `bg-neutral-800 border border-neutral-700 rounded-lg p-4` (+ hover effect if hoverable)

#### LoadingSpinner
**Props**:
```typescript
interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
}
```
**Renders**: Animated SVG spinner + optional text

---

## API Integration Points

| Component | Endpoint | Method | Purpose |
|-----------|----------|--------|---------|
| App/CommandCenter | `/api/v1/program/` | GET | Fetch program overview |
| CommandCenter | `/api/v1/ai/query` | POST | Send AI chat query |
| CommandCenter | `/api/v1/ai/summary` | GET | Fetch executive summary |
| GateTimeline | `/api/v1/gates/timeline` | GET | Fetch gate × workstream matrix |
| DependencyGraph | `/api/v1/dependencies/` | GET | Fetch dependency graph (nodes + links) |
| RiskHeatMap | *Derived from workstreams* | - | Filter risks from workstream data |
| WorkstreamCard | `/api/v1/workstreams/:id` | GET | Fetch workstream detail |
| WorkstreamCard | `/api/v1/workstreams/:id` | PUT | Update workstream |
| WorkstreamForm | `/api/v1/workstreams/` | POST | Create new workstream |

**Error Handling**: Axios interceptor in `services/api.ts` logs errors and rejects promise. Components wrap in try-catch or error boundary.

---

## Mobile Responsiveness

**Grid Patterns**:
```tsx
<!-- 1 col mobile, 2 col tablet, 3 col desktop -->
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">

<!-- 1 col mobile, 2 col desktop -->
<div className="grid grid-cols-1 lg:grid-cols-2 gap-4">

<!-- 1 col mobile, hide on mobile, show on desktop -->
<div className="hidden lg:flex">
```

**Touch Targets**: All buttons and links ≥ 44×44px (Tailwind py-2 px-3 minimum)

**Tables on Mobile**: `overflow-x-auto` wrapper with `min-w-[120px]` per column

---

## Accessibility

- All nav links have text labels (not icon-only)
- Form fields have associated `<label>` elements
- Status badges use color + text (not color-alone)
- Hover states visible on all interactive elements
- Keyboard navigation: Tab, Enter, Esc support
- Sidebar hamburger button has `aria-label="Open sidebar"`
- TODO: ARIA live regions for async notifications

---

## Theme System

**ThemeProvider Context** (`/frontend/src/themes/index.ts`):
```typescript
export type ThemeName = 'swa' | 'neutral';

export const useTheme = () => {
  const { currentTheme, setTheme, colors } = useContext(ThemeContext);
  // Switch theme: setTheme(currentTheme === 'swa' ? 'neutral' : 'swa')
};
```

**Theme Toggle**: Sidebar palette button switches between SWA (branded) and Neutral (blue-toned) themes. Persisting theme preference (localStorage) is optional future enhancement.
