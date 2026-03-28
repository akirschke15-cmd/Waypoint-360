# Waypoint 360 - Edge Cases

## Empty States

| View | Condition | What to Show |
|------|-----------|-------------|
| Dashboard (pre-seed) | No program data loaded | Seed prompt: "Initialize Waypoint 360 with sample data" button → POST /program/seed |
| Dashboard (post-delete) | POST /program/reset successful | Same seed prompt, fresh state |
| Workstream Grid | All workstreams deleted | "No workstreams assigned. Create or import workstreams." |
| Workstream Detail | Workstream with 0 deliverables | "No deliverables assigned to this workstream" message, empty list |
| Gate Timeline | Workstream with 0 deliverables for a gate | Cell shows "--" (dash) instead of progress bar |
| Gate Timeline | All workstreams have no deliverables | Entire matrix shows dashes, "No deliverables in scope" notice |
| Risk Heatmap | 0 risks in program | "No risks identified. Add risks to track." message, empty matrix with "--" cells |
| Dependency Graph | 0 dependencies between workstreams | "No dependencies detected." message, isolated nodes only |
| AI Chat | First visit, no chat history | Placeholder text: "Ask about Waypoint status, workstreams, risks, or gate readiness" |
| AI Chat | Chat message list empty | Show placeholder, not blank page |
| Person List | Person not assigned to any workstreams | Show as "Unassigned" in gray, no workstream card |
| Risk Detail | Risk with notes = null | Notes section shows "--" (no additional context) |

## Error States

| HTTP Status | Condition | User Message | Recovery Action | Frontend Code |
|-------------|-----------|-------------|----------------|---------------|
| 400 | Invalid request body (missing required fields) | "Invalid request. Please check your input." | Show form validation errors inline | Client validates before send |
| 400 | Invalid enum value (e.g., status="invalid") | "Invalid status value. Choose from: Complete, OnTrack, AtRisk, Blocked" | Show dropdown with valid options | Form input uses select/radio |
| 404 | Workstream ID not found | "Workstream not found. It may have been deleted." | Show back link to dashboard | Router.back() or navigate('/') |
| 404 | Program data not loaded | "Program not initialized. Click 'Initialize' to load sample data." | Show seed button | POST /program/seed |
| 404 | Dependency graph workstream missing | "One or more workstreams in dependency chain not found." | Show list of missing IDs, back link | Render only valid edges |
| 409 | Circular dependency detected (A→B→C→A) | "Circular dependency detected. Workstreams cannot depend on themselves directly or indirectly." | Show dependency chain visually, offer to delete edge | Highlight cycle in graph |
| 422 | Gate status transition invalid (Blocked → Complete) | "Cannot transition from Blocked directly to Complete. Must resolve risks first." | Show valid transitions as buttons | Disable invalid transitions |
| 500 | Database connection error | "Connection error. Retrying..." (auto-retry) | Show retry button after 3 failed attempts | Axios interceptor with exponential backoff |
| 500 | LangGraph node execution fails | "AI query failed. Please try again." | Show retry button | User can resend message |
| 500 | Seed data load fails | "Failed to initialize sample data. Check server logs." | Show retry button, manual reset option | POST /program/seed retry |

## Loading States

All pages use `<Loader2 className="animate-spin" size={32} />` spinner from lucide-react.

**Loading Indicators by Page**
- **Dashboard**: Full-page centered spinner on initial load (while fetching /program)
- **Workstream Detail**: Spinner at top-right corner while fetching specific workstream
- **Gate Timeline**: Skeleton row while calculating readiness (20ms−100ms typical)
- **Dependency Graph**: Spinner centered in SVG container while computing layout
- **AI Chat**: Spinner next to chat input while LLM responds, disappears when message arrives
- **Risk Heatmap**: Spinner overlay while sorting by severity

**No skeleton screens yet** (deferred to Phase 4). Use spinners only.

## Specific Edge Cases

### Data Integrity & State

- [ ] **Workstream with scope_in = null**: `scope_in.split('|').filter(Boolean)` safely returns empty array, no crashes
- [ ] **Gate readiness = "complete" but dependencies blocked**: Show warning badge "Dependency risk"
- [ ] **Multiple workstreams owned by same person**: Person card shows count badge "3 workstreams", list all on hover
- [ ] **Person with role = null**: Display as "Unassigned role" in italics, can be updated
- [ ] **Risk with impact/likelihood = 0**: Severity score = 0, shows as "No severity" in light gray
- [ ] **Deliverable end_date before start_date**: Show error on save "End date must be after start date"
- [ ] **Gate exit criteria = empty array**: Gate shows "0/0 criteria met", progress bar is 0% (not full)

### Graph & Visualization

- [ ] **Circular dependencies (A→B→C→A)**: D3 graph detects cycle, highlights nodes in red, shows alert
- [ ] **Self-referential dependency (A→A)**: Validation rejects on POST, shows "A workstream cannot depend on itself"
- [ ] **Disconnected graph nodes**: Show orphaned workstreams separately at bottom, labeled "No dependencies"
- [ ] **Graph with 100+ edges**: D3 force-directed layout degrades gracefully, may have overlapping edges
- [ ] **D3 pan/zoom with 0 dependencies**: Graph renders 13 isolated nodes, zoom-to-fit shows all
- [ ] **Resize browser while D3 renders**: Graph recalculates layout, no crashes, smooth reflow

### Temporal & Workflow

- [ ] **Gate already "complete" but risk marked "at_risk"**: Show warning "Gate is complete but risks remain"
- [ ] **Workstream status inferred as "blocked" due to dependency**: Status overrides manual assignment, shows badge
- [ ] **Gate without any workstreams assigned**: Gate row in timeline shows "--" for all cells, "No workstreams in gate"
- [ ] **Dependency on workstream not yet in this gate**: Allow cross-gate dependencies, show visual link
- [ ] **Archive completed gate**: Move to separate "Archived Gates" section, hide from main timeline
- [ ] **Reopen gate after marked complete**: Reset workstream status inference, recalculate readiness

### API & Concurrency

- [ ] **Rapid PATCH requests on same workstream**: Second request overwrites first; implement optimistic locking if race condition risk
- [ ] **Delete workstream while viewing its detail page**: Redirect to 404 → dashboard, show "Workstream deleted"
- [ ] **Seed while program already seeded**: Clear existing data, reload seed, no duplicates
- [ ] **POST /program/reset during API call**: Abort pending requests, empty state confirmed
- [ ] **LangGraph timeout (>30 sec response time)**: User can cancel, shows "Query took too long"
- [ ] **Streaming chat response interrupted**: Show partial message + "Connection lost" indicator

### UI & Input

- [ ] **AI chat input > 2000 characters**: Show warning "Message too long (max 2000)", prevent send
- [ ] **Workstream name = 0 characters**: Validation error "Name required", input stays focused
- [ ] **Scope change with 20+ deliverables**: Show multi-select modal, no dropdown lag (virtualize list if >100)
- [ ] **Theme toggle during animation**: Ensure smooth transition, no flashing
- [ ] **Mobile viewport < 640px width**: Dependency graph collapses to list view, timeline becomes scrollable
- [ ] **Print dashboard**: Hide interactive elements (buttons, chat), show readable snapshot

### Risk & Severity

- [ ] **Risk impact = 5, likelihood = 1**: Severity = 5, shows as "Medium" in yellow-orange
- [ ] **Risk impact = 5, likelihood = 5**: Severity = 25, shows as "Critical" in red, blinks (highest priority)
- [ ] **Update risk severity retroactively**: Heatmap re-sorts instantly, no page reload
- [ ] **Risk marked "resolved"**: Move to separate "Resolved Risks" section, keep audit trail
- [ ] **Risk with null severity**: Display as "Unscored" in gray, prompt to assess

### Performance

- [ ] **Dashboard with 1000+ risks**: Heatmap is paginated or virtualized, <2 sec initial render
- [ ] **Dependency graph with 500 edges**: D3 layout completes in <5 sec, pan/zoom responsive
- [ ] **AI chat with 100+ message history**: Scroll to latest message, older messages lazy-load on scroll up
- [ ] **Seed data load on slow network (3G)**: Show progress indicator "Loading 13 workstreams...", no timeout <30 sec
- [ ] **Resize window 10 times rapidly**: Graph reflows each time, no memory leak, no dropped events

### Accessibility & Internationalization

- [ ] **Screen reader user navigates dependency graph**: Graph has ARIA labels on each node, edges announced
- [ ] **User with colorblind vision**: Risk heatmap shows icon + color + text label, not color alone
- [ ] **Keyboard-only navigation**: Tab through all interactive elements, Enter/Space activates buttons
- [ ] **Page text overlaps on mobile (< 320px)**: Text wraps, buttons don't overlap, readable layout
- [ ] **Date format in different locale**: Show ISO 8601 (2026-03-28), or accept user locale preference (deferred to Phase 4)

### Uncommon but Critical

- [ ] **Gate status is null (database corruption)**: Treat as "Blocked", show warning banner "Data inconsistency detected"
- [ ] **Person assigned to workstream but person deleted**: Show "Unknown person (deleted)" in italics, allow reassignment
- [ ] **Workstream marked complete but no deliverables**: Validation allows (deliverables optional), show "No deliverables tracked"
- [ ] **Dependency edge points to deleted workstream**: Remove edge, show notification "Dependency removed (workstream deleted)"
- [ ] **Chat query contains profanity or policy violation**: Claude API may refuse, show "Query rejected by policy"

## Error Recovery Checklist

- [ ] All 400/404/500 errors show user-friendly message (no HTTP codes in UI)
- [ ] Retry buttons visible on transient errors (500, network timeout)
- [ ] No error details leaked to frontend (stack traces never shown)
- [ ] Axios interceptor catches and handles all error codes
- [ ] Modal/dialog closes on error, form input preserved for resubmit
- [ ] Network errors trigger exponential backoff (1s → 2s → 4s max 30s)
- [ ] Seed failure shows rollback confirmation "Data rolled back, please try again"
- [ ] Chat error doesn't clear message history, user can resend
