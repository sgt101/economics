# Household consumption per capita

An interactive chart comparing real household consumption per capita across a
set of countries, as a proxy for median household disposable income.

## The chart

- **[▶ View the live chart](https://htmlpreview.github.io/?https://github.com/sgt101/economics/blob/main/household_consumption_per_capita.html)** —
  renders the interactive page in your browser.
- Source file: [household_consumption_per_capita.html](household_consumption_per_capita.html)
  (GitHub shows this as raw HTML; use the link above to render it). It is a
  single self-contained file and loads Plotly from a CDN, so an internet
  connection is needed.

> Prefer a cleaner URL? Enable **GitHub Pages** for this repo (Settings → Pages →
> deploy from `main`), then the chart is served directly at
> `https://sgt101.github.io/economics/household_consumption_per_capita.html`.

It shows two stacked charts that share the same controls:

1. **Normalized** — each country's series re-based to the selected start
   year = 100.
2. **Unnormalized** — the raw per-capita values in constant 2015 US$.

Controls:

- A **checkbox per country** to include or exclude it from both charts.
- A **start-year selector**; the normalized chart re-bases to that year and
  both charts begin there.

## Data source

World Bank indicator **`NE.CON.PRVT.PC.KD`** —
*"Households and NPISHs Final consumption expenditure per capita
(constant 2015 US$)"*, fetched live from the World Bank API:

```
https://api.worldbank.org/v2/country/{ISO3}/indicator/NE.CON.PRVT.PC.KD?format=json
```

Countries covered: USA, Germany, Netherlands, France, UK, Ireland, Italy,
Greece, Spain, China, India. Available data spans roughly 1960–2024 (coverage
varies by country).

> Note: the World Bank has no "median household disposable income" series, so
> household consumption per capita is used as a proxy. It tracks spending and is
> a *mean* per-capita figure, not a median.

## Processing steps

[median-household-disposable-ppp.py](median-household-disposable-ppp.py)
generates the HTML:

1. **Fetch** each country's full time series from the World Bank API by ISO3
   code, keeping only years with a non-null value.
2. **Align** the series onto a common, sorted list of years.
3. **Embed** the raw values, colours, country list and candidate start years
   into the HTML page as a JSON blob.
4. **Normalize in the browser**: when a start year is chosen, each selected
   country's values are divided by that country's start-year value and
   multiplied by 100. The unnormalized chart plots the raw values directly.

All normalization happens client-side in JavaScript, so the chart re-computes
instantly as you change the controls — no server required.

## Regenerating

```bash
uv run --no-project python median-household-disposable-ppp.py
```

This re-fetches the latest World Bank data and rewrites
`household_consumption_per_capita.html`.
