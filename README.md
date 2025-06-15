# GeniusO4 Front-End Application

This document describes the architecture, components, data flow, and coding conventions of the GeniusO4 front-end application to help automated code generation tools (such as Codex) understand and navigate the codebase without confusion.

## Table of Contents
1. Introduction
2. Technology Stack
3. Project Structure
4. How to Run
   - Frontend V2 (experimental)
5. Data Flow and JSON Schema
6. UI Components
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
   - Spinner
7. Indicator Categories and Grouping
8. Tooltip Rules
9. Virtual Candles (Forecast)
10. Legend Usage
11. Development Workflow
12. Building and Testing
13. License

## 1. Introduction
The GeniusO4 application visualizes financial data and analysis overlays returned by a machine learning model. It uses the `lightweight-charts` library для отрисовки интерактивных свечей. This README provides detailed information about file organization, component responsibilities, and data contracts.

## 2. Technology Stack
- React (version 18)  
- JavaScript (ES6) or TypeScript  
- `lightweight-charts` — используется для отрисовки интерактивных свечей
 - Tailwind CSS и Headless UI для пользовательских элементов управления
- Axios or Fetch API for data requests  
- Redux or React Context for state management  
- Jest and React Testing Library for unit tests  

## 3. Project Structure
```
.
├── api/            # FastAPI backend
├── frontend/       # React application
├── frontend_v2/    # React + TypeScript (experimental)
│   ├── src
│   │   ├── components/
│   │   ├── pages/
│   │   ├── data/
│   │   ├── services/
│   │   └── utils/
│   └── package.json
├── configs/
├── docs/
├── run.py
├── docker-compose.yml
└── deploy.sh
```

## 4. How to Run
Run backend and frontend together:
```bash
python run.py --mode dev
```
The script starts FastAPI on port 8000 and the Vite dev server on 5173.

To launch only the React app:
```bash
cd frontend
npm install
npm run dev
```

### Frontend V2 (experimental)
```bash
cd frontend_v2
npm install
npm run dev
```

## 5. Data Flow and JSON Schema
1. Fetch JSON responses using `fetchAnalysis()`.  
2. Validate required fields in each section of the response:
   - Overlays: require `date` and `level` or `start_point` and `end_point`.  
   - Forecast: array `virtual_candles` containing objects `{ time, open, high, low, close, explanation }`.  
3. On missing fields, call:
   ```js
   console.warn('Missing fields for section ' + sectionName);
   ```
   Do not break application flow.

## 6. UI Components
### TradingViewChart
- Renders the main TradingView chart and manages overlay series.
- Provides callbacks for legend metadata and series toggling.

### ChartControls
- Small toolbar with buttons to switch chart type and toggle side panels.

### AnalysisControls
- Form inputs for symbol, interval and limit selection.

### IndicatorsSidebar
- Left sliding panel listing indicator groups.
- Built with Tailwind classes and Headless UI Disclosure panels.
- Categories (in strict order):
  1. Overlays
  2. Volume
  3. Momentum
  4. Volatility
  5. MACD
  6. Model Analysis
  7. Forecast

### CommentsPanel
- Right panel with tabs "Primary Analysis" and "Explanation".
- Shows text from `primary_analysis` and `explanation` fields.
- Can be collapsed using the `commentsOpen` flag.

### InsightsPanel
- Displays additional analytics under the comments.

### Legend
- Renders below the main chart and toggles series visibility:
  ```js
  series.applyOptions({ visible: !visible });
  ```

### VolumePanel
### OscillatorsPanel
### MACDPanel

### Spinner
- Small SVG component used for loading state animations.

Example usage of side panel flags:
```jsx
const [sidebarOpen, setSidebarOpen] = useState(true);
const [commentsOpen, setCommentsOpen] = useState(true);

<ChartControls
  type={chartType}
  onChange={setChartType}
  setSidebarOpen={setSidebarOpen}
  setCommentsOpen={setCommentsOpen}
/>

<Home
  sidebarOpen={sidebarOpen}
  commentsOpen={commentsOpen}
  setSidebarOpen={setSidebarOpen}
  setCommentsOpen={setCommentsOpen}
 />
```

## 7. Indicator Categories and Grouping
Defined in `src/data/indicatorGroups.js`. Each category maps to an array of indicator keys and display names.

## 8. Tooltip Rules
- Disable default TradingView tooltips for all series.  
- Implement custom tooltips only for:
  - support_resistance_levels  
  - fibonacci_analysis  
  - price_prediction (forecast candles)  

## 9. Virtual Candles (Forecast)
- Use `chart.addCandlestickSeries({ priceFormat: { type: 'ohlc' } })`.  
- Render `virtual_candles` data as series with `opacity: 0.4`.  
- Include entry in Legend with icon "⧉" and label "Forecast".  

## 10. Legend Usage
- Obtain series list via `chart.getSeries()`.  
- Generate `legendItems` array: `{ name, color, icon, visible }`.  
- Render clickable legend elements to toggle visibility.

## 11. Development Workflow
- Work on atomic tasks (one feature or bug fix per pull request).  
- Write unit tests for each critical component:  
  - CommentsPanel  
  - TradingViewChart forecast update  
  - Sidebar toggles  
  - Legend click handling  

## 12. Building and Testing
- Build: `npm run build` with no errors or warnings.
- Test: `npm test` should pass all tests.

## 13. License
Specify project license here.
