# Frontend Agent Notes

## Purpose

This directory contains the existing Next.js Kanban demo UI used as the starting point for the MVP.

Current status:
- Sign-in gate is implemented in frontend (`user` / `password`).
- Unauthenticated users see login UI first.
- After successful login, the 5-column Kanban board is shown.
- Logout returns the user to the login screen.
- Board state is still local in-memory (resets on refresh).

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
  - App entrypoint. Renders `AuthGate`.
- `src/app/globals.css`
  - Global CSS variables and base styles, aligned with project color scheme.
- `src/components/`
  - `AuthGate.tsx`: login/session check UI and auth flow.
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
- Authentication is present (via backend auth API + cookie session).
- Persistence and AI integration are not implemented yet.

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
