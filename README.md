# GeniusO4 Front-End Application

This document describes the architecture, components, data flow, and coding conventions of the GeniusO4 front-end application to help automated code generation tools (such as Codex) understand and navigate the codebase without confusion.

## Table of Contents
1. Introduction  
2. Technology Stack  
3. Project Structure  
4. Data Flow and JSON Schema  
5. UI Components  
   - TradingViewChartComponent  
   - IndicatorsSidebar  
   - CommentsPanel  
   - Legend  
   - VolumePanel  
   - OscillatorsPanel  
   - MACDPanel  
6. Indicator Categories and Grouping  
7. Tooltip Rules  
8. Virtual Candles (Forecast)  
9. Legend Usage  
10. Development Workflow  
11. Building and Testing  
12. License  

## 1. Introduction
The GeniusO4 application visualizes financial data and analysis overlays returned by a machine learning model. It uses the TradingView Charting Library for rendering interactive charts. This README provides detailed information about file organization, component responsibilities, and data contracts.

## 2. Technology Stack
- React (version 18)  
- JavaScript (ES6) or TypeScript  
- TradingView Charting Library  
- Material-UI for user interface controls  
- Axios or Fetch API for data requests  
- Redux or React Context for state management  
- Jest and React Testing Library for unit tests  

## 3. Project Structure
```
/src
  /components
    TradingViewChart.jsx
    IndicatorsSidebar.jsx
    CommentsPanel.jsx
    Legend.jsx
    VolumePanel.jsx
    OscillatorsPanel.jsx
    MACDPanel.jsx
  /data
    analysisLoader.js
    analysisValidator.js
    indicatorGroups.js
  /assets
    (icons, styles)
  App.jsx
  index.jsx
README.md
AGENTS.md
package.json
```

## 4. Data Flow and JSON Schema
1. Fetch JSON responses using `fetchAnalysis()`.  
2. Validate required fields in each section of the response:
   - Overlays: require `date` and `level` or `start_point` and `end_point`.  
   - Forecast: array `virtual_candles` containing objects `{ time, open, high, low, close, explanation }`.  
3. On missing fields, call:
   ```js
   console.warn('Missing fields for section ' + sectionName);
   ```
   Do not break application flow.

## 5. UI Components
### TradingViewChartComponent
- Initializes the main TradingView chart.  
- Adds series for price candles, technical overlays, forecast candles, and commentary markers.  
- Exposes update and retrieval methods for series and regions.

### IndicatorsSidebar
- Left sliding panel with seven fixed categories.  
- Uses MUI Accordion and Checkbox controls.  
- Categories (in strict order):
  1. Overlays  
  2. Volume  
  3. Momentum  
  4. Volatility  
  5. MACD  
  6. Model Analysis  
  7. Forecast  

### CommentsPanel
- Right panel with tabs: "Primary Analysis" and "Explanation".  
- "Primary Analysis": displays text from `primary_analysis` JSON fields.  
- "Explanation": displays `explanation` from each active overlay section.

### Legend
- Renders below the main chart.  
- Displays active series with color markers or icons.  
- Toggles series visibility on click via:
  ```js
  series.applyOptions({ visible: !visible });
  ```

## 6. Indicator Categories and Grouping
Defined in `src/data/indicatorGroups.js`. Each category maps to an array of indicator keys and display names.

## 7. Tooltip Rules
- Disable default TradingView tooltips for all series.  
- Implement custom tooltips only for:
  - support_resistance_levels  
  - fibonacci_analysis  
  - price_prediction (forecast candles)  

## 8. Virtual Candles (Forecast)
- Use `chart.addCandlestickSeries({ priceFormat: { type: 'ohlc' } })`.  
- Render `virtual_candles` data as series with `opacity: 0.4`.  
- Include entry in Legend with icon "⧉" and label "Forecast".  

## 9. Legend Usage
- Obtain series list via `chart.getSeries()`.  
- Generate `legendItems` array: `{ name, color, icon, visible }`.  
- Render clickable legend elements to toggle visibility.

## 10. Development Workflow
- Work on atomic tasks (one feature or bug fix per pull request).  
- Write unit tests for each critical component:  
  - CommentsPanel  
  - TradingViewChart forecast update  
  - Sidebar toggles  
  - Legend click handling  

## 11. Building and Testing
- Remove legacy dependencies: `plotly.js`, `react-dash`, `echarts`.  
- Build: `npm run build` with no errors or warnings.  
- Test: `npm test` should pass all tests.

## 12. License
Specify project license here.
