"""
Interactive chart of real household consumption per capita (a World Bank proxy
for median household disposable income), normalized to a selectable start year.

Data source: World Bank indicator NE.CON.PRVT.PC.KD
  "Households and NPISHs Final consumption expenditure per capita
   (constant 2015 US$)"

Output: a single self-contained HTML file with
  - a checkbox per country (include / exclude)
  - a start-year selector (the series are re-normalized to start year = 100)
Normalization is recomputed client-side in JavaScript, so no server is needed.
"""

import json
import urllib.request

# 1. Countries to fetch (ISO3 code -> display name)
COUNTRIES = {
    'USA': 'USA',
    'DEU': 'Germany',
    'NLD': 'Netherlands',
    'FRA': 'France',
    'GBR': 'UK',
    'IRL': 'Ireland',
    'ITA': 'Italy',
    'GRC': 'Greece',
    'ESP': 'Spain',
    'CHN': 'China',
    'IND': 'India',
}

INDICATOR = 'NE.CON.PRVT.PC.KD'

# Per-country line colours
COLORS = {
    'USA': '#1f77b4',
    'Germany': '#d62728',
    'Netherlands': '#9467bd',
    'France': '#ff7f0e',
    'UK': '#8c564b',
    'Ireland': '#2ca02c',
    'Italy': '#e377c2',
    'Greece': '#17becf',
    'Spain': '#bcbd22',
    'China': '#000000',
    'India': '#7f7f7f',
}


def fetch_country(iso3):
    """Return {year: value} for one country from the World Bank API."""
    url = (
        f'https://api.worldbank.org/v2/country/{iso3}'
        f'/indicator/{INDICATOR}?format=json&per_page=20000'
    )
    with urllib.request.urlopen(url, timeout=60) as resp:
        payload = json.load(resp)

    series = {}
    rows = payload[1] if len(payload) > 1 and payload[1] else []
    for row in rows:
        if row['value'] is not None:
            series[int(row['date'])] = float(row['value'])
    return series


# 2. Fetch every country
raw = {}
for iso3, name in COUNTRIES.items():
    print(f'Fetching {name} ({iso3})...')
    raw[name] = fetch_country(iso3)

# 3. Common year range across all countries that have data
all_years = sorted(set().union(*[set(s.keys()) for s in raw.values()]))
min_year, max_year = all_years[0], all_years[-1]
print(f'Year range: {min_year}-{max_year}')

# Build a dense {country: {year: value or None}} structure for the front end
data = {}
for name, series in raw.items():
    data[name] = {y: series.get(y) for y in all_years}

# Candidate start years offered in the selector (only years with broad coverage)
start_years = [y for y in all_years if y % 5 == 0 or y in (2008, 2020)]
default_start = 2000 if 2000 in start_years else start_years[0]

# 4. Emit a self-contained interactive HTML file
payload = {
    'years': all_years,
    'data': data,
    'colors': COLORS,
    'startYears': start_years,
    'defaultStart': default_start,
    'countries': list(raw.keys()),
}

html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Household consumption per capita</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
  body {{ font-family: Arial, sans-serif; margin: 24px; color: #434241; }}
  h1 {{ font-size: 20px; color: #000; }}
  .layout {{ display: flex; gap: 24px; align-items: flex-start; }}
  #chart {{ flex: 1 1 auto; }}
  .controls {{ flex: 0 0 220px; padding: 12px 16px; background: #FBE8DB;
              border-radius: 8px; }}
  .controls h2 {{ font-size: 14px; margin: 0 0 8px; }}
  label.country {{ display: block; margin: 4px 0; font-size: 14px; cursor: pointer; }}
  select {{ font-family: Arial; font-size: 14px; padding: 4px; width: 100%; }}
  .swatch {{ display: inline-block; width: 12px; height: 12px; margin-right: 6px;
            border-radius: 2px; vertical-align: middle; }}
</style>
</head>
<body>
<h1>Real household consumption per capita</h1>
<p style="color:#747271;font-size:13px;margin-top:-6px;">
  World Bank NE.CON.PRVT.PC.KD (constant 2015 US$), normalized to the selected
  start year = 100. A proxy for median household disposable income.</p>

<div class="layout">
  <div style="flex:1 1 auto;">
    <div id="chart"></div>
    <div id="chart2"></div>
  </div>
  <div class="controls">
    <h2>Start year</h2>
    <select id="startYear"></select>
    <h2 style="margin-top:16px;">Countries</h2>
    <div id="countryBoxes"></div>
  </div>
</div>

<script>
const CFG = {payload};

const startSel = document.getElementById('startYear');
CFG.startYears.forEach(y => {{
  const o = document.createElement('option');
  o.value = y; o.textContent = y;
  if (y === CFG.defaultStart) o.selected = true;
  startSel.appendChild(o);
}});

const boxWrap = document.getElementById('countryBoxes');
CFG.countries.forEach(c => {{
  const lab = document.createElement('label');
  lab.className = 'country';
  const cb = document.createElement('input');
  cb.type = 'checkbox'; cb.checked = true; cb.value = c;
  cb.addEventListener('change', render);
  const sw = document.createElement('span');
  sw.className = 'swatch'; sw.style.background = CFG.colors[c];
  lab.appendChild(cb); lab.appendChild(sw);
  lab.appendChild(document.createTextNode(' ' + c));
  boxWrap.appendChild(lab);
}});
startSel.addEventListener('change', render);

function selectedCountries() {{
  return Array.from(boxWrap.querySelectorAll('input:checked')).map(cb => cb.value);
}}

function render() {{
  const start = parseInt(startSel.value, 10);
  const years = CFG.years.filter(y => y >= start);
  const chosen = selectedCountries();
  const traces = [];   // normalized (index)
  const traces2 = [];  // raw constant 2015 US$

  chosen.forEach(c => {{
    const base = CFG.data[c][start];
    if (base == null) return;  // no baseline -> cannot normalize
    const xs = [], ys = [], ysRaw = [];
    years.forEach(y => {{
      const v = CFG.data[c][y];
      if (v != null) {{ xs.push(y); ys.push(v / base * 100); ysRaw.push(v); }}
    }});
    const line = {{ color: CFG.colors[c], width: 2.5 }};
    traces.push({{ x: xs, y: ys, mode: 'lines', name: c, line: line }});
    traces2.push({{ x: xs, y: ysRaw, mode: 'lines', name: c, line: line }});
  }});

  const lastYear = years[years.length - 1];
  const baseLayout = {{
    margin: {{ t: 36, r: 20, b: 50, l: 70 }},
    height: 480,
    xaxis: {{ title: 'Year', dtick: 5, gridcolor: '#ECECEC' }},
    legend: {{ orientation: 'h', y: -0.18 }},
    plot_bgcolor: '#FFFFFF', paper_bgcolor: '#FFFFFF',
  }};

  const layout = Object.assign({{}}, baseLayout, {{
    title: {{ text: 'Normalized (' + start + ' = 100)', font: {{ size: 14 }} }},
    yaxis: {{ title: 'Index (' + start + ' = 100)', gridcolor: '#ECECEC' }},
    shapes: [{{ type: 'line', x0: start, x1: lastYear,
               y0: 100, y1: 100, line: {{ color: '#A8A5A2', dash: 'dash', width: 1 }} }}],
  }});

  const layout2 = Object.assign({{}}, baseLayout, {{
    title: {{ text: 'Unnormalized (constant 2015 US$)', font: {{ size: 14 }} }},
    yaxis: {{ title: 'Per capita (constant 2015 US$)', gridcolor: '#ECECEC' }},
  }});

  const opts = {{ responsive: true, displaylogo: false }};
  Plotly.react('chart', traces, layout, opts);
  Plotly.react('chart2', traces2, layout2, opts);
}}

render();
</script>
</body>
</html>
""".format(payload=json.dumps(payload))

out_path = 'household_consumption_per_capita.html'
with open(out_path, 'w') as f:
    f.write(html)

print(f'Wrote {out_path}')
