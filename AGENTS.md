# Agent Guidelines for Codex

This document provides conventions and best practices for the Codex AI agent to generate code accurately and consistently for the GeniusO4 front-end project.

## 1. Purpose
Ensure that the Codex agent:
- Understands project structure.
- Follows coding conventions.
- Produces unambiguous, focused changes.

## 2. Project Structure
- `api/` – FastAPI backend
- `frontend/` – React + Vite application
  - `src/components` – reusable components
  - `src/pages` – route pages
  - `src/services` – API helpers
  - `src/data` – static indicator definitions
- `run.py` – helper script to launch both services

## 3. How to Run
- Start backend and frontend together:
  ```bash
  python run.py dev
  ```
- Start only the frontend:
  ```bash
  cd frontend
  npm install
  npm run dev
  ```

## 4. Component List
- TradingViewChart
- ChartControls
- AnalysisControls
- IndicatorsSidebar
- CommentsPanel
- InsightsPanel
- Legend
- VolumePanel
- OscillatorsPanel
- MACDPanel

## 5. General Conventions
1. Refer to exact file paths in prompts.
2. Use full component, function, and variable names as in the codebase.
3. Do not add or remove unrelated code.
4. Adhere to existing code style:
   - Indentation: 2 spaces or project setting.
   - Quotes: single or double consistent with surrounding code.
   - Semicolons: follow project convention.
5. Import only necessary modules.

## 6. Task Description Format
Each mini-task must include:
- **Title**: Short imperative verb phrase.
- **Files to Modify**: Exact relative paths.
- **Changes**: Step-by-step instructions.
- **Validation**: Criteria to verify correct implementation.

### Example
\`\`\`
Title: Enable custom tooltips for support_resistance_levels

Files to Modify:
- src/components/TradingViewChart.jsx

Changes:
1. Locate \`supportSeriesRef\` initialization.
2. Disable default tooltip: \`supportSeriesRef.current.applyOptions({ priceLineVisible: false })\`.
3. Subscribe to \`chart.subscribeCrosshairMove\` to show a custom popup with \`type\`, \`level\`, \`date\`, \`explanation\`.
4. Unsubscribe on cleanup.

Validation:
- Hovering over a support line shows a custom popup with correct fields.
- No tooltips appear for other series.
\`\`\`

## 7. Common Patterns
- Use \`useRef\` for chart and series references.
- Update series via \`setData\`, \`applyOptions\`, \`setMarkers\`, \`setRegions\`.
- Parse JSON in \`analysisValidator.js\` and log warnings on missing fields.

## 8. Error Handling
- Use \`console.warn\` for non-critical missing data.
- Do not throw exceptions for optional sections.

## 9. Testing
Include Jest tests for:
- Correct rendering of CommentsPanel with \`explanation\`.
- Forecast candles appearing in TradingViewChart.
- Sidebar group order and checkbox toggles.
- Legend toggling visibility.

## 10. Documentation Updates
After code changes:
- Update this AGENTS.md if any conventions change.
- Ensure README.md reflects any new architecture or component changes.
