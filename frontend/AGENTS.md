# Frontend Agent Notes

## Purpose

This directory contains the existing Next.js Kanban demo UI used as the starting point for the MVP.

Current status:
- Frontend-only implementation (no backend API integration yet).
- Single page app at `/` rendering a 5-column Kanban board.
- Local in-memory state only (resets on refresh).

## Stack

- Next.js 16 (App Router)
- React 19 + TypeScript
- Tailwind CSS v4
- `@dnd-kit` for drag and drop
- Vitest + Testing Library for unit/component tests
- Playwright for end-to-end tests

## High-Level Structure

- `src/app/layout.tsx`
  - Global layout, metadata, and font setup (`Space_Grotesk`, `Manrope`).
- `src/app/page.tsx`
  - App entrypoint. Renders `KanbanBoard`.
- `src/app/globals.css`
  - Global CSS variables and base styles, aligned with project color scheme.
- `src/components/`
  - `KanbanBoard.tsx`: top-level board state and DnD context.
  - `KanbanColumn.tsx`: editable column title, sortable cards, add-card form.
  - `KanbanCard.tsx`: draggable card with remove action.
  - `KanbanCardPreview.tsx`: drag overlay preview.
  - `NewCardForm.tsx`: inline form for new cards.
- `src/lib/kanban.ts`
  - Board types, seed data, drag move logic, ID generation helper.

## Current Behavior

- Board initializes from static `initialData` in `src/lib/kanban.ts`.
- Columns are fixed in count (5) but titles are editable.
- Cards can be:
  - moved within and across columns via drag and drop
  - added to a column
  - removed from a column
- No authentication, persistence, or AI integration yet.

## Testing Setup

- Unit/component tests:
  - `src/lib/kanban.test.ts`
  - `src/components/KanbanBoard.test.tsx`
- E2E tests:
  - `tests/kanban.spec.ts`
- Config:
  - `vitest.config.ts`
  - `playwright.config.ts`

## NPM Scripts

- `npm run dev`
- `npm run build`
- `npm run start`
- `npm run lint`
- `npm run test` / `npm run test:unit`
- `npm run test:e2e`
- `npm run test:all`

## Integration Notes For Next Phases

- Treat this directory as an existing UI baseline; preserve core UX where practical.
- Backend integration should replace local state source progressively, not rewrite UI first.
- Keep frontend changes focused on MVP requirements only.
