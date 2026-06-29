import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# 1. Define the extended timeline (1993 to 2026)
years_extended = np.arange(1993, 2027)

# 2. Historical median data estimates (USD PPP constant equivalents)
# Splitting data into historical tracking (1993-2006) and contemporary tracking (2007-2026)
data_2007_onwards = {
    'USA':         [36500, 36200, 35500, 35200, 35400, 35600, 35900, 37200, 39300, 40400, 41500, 42300, 44200, 45800, 46500, 44200, 45300, 46100, 46600, 47100],
    'Germany':     [29800, 30200, 30100, 30500, 31000, 31200, 31400, 32100, 32900, 33800, 34400, 35100, 35600, 35800, 36100, 35900, 36100, 36800, 37200, 37500],
    'Netherlands': [31000, 31600, 31200, 30800, 30400, 29900, 29400, 29900, 30600, 31400, 32100, 32800, 33600, 34200, 34800, 34500, 35200, 35800, 36300, 36600],
    'France':      [28200, 28400, 28700, 28900, 28800, 28600, 28500, 28700, 29100, 29600, 30100, 30600, 31300, 31400, 32100, 31900, 32400, 32900, 33300, 33500],
    'UK':          [27000, 26800, 26900, 26600, 26100, 26300, 26200, 26500, 27300, 27700, 27800, 28100, 28500, 28900, 28400, 27600, 27800, 28300, 28600, 28900],
    'Ireland':     [26200, 25800, 24400, 22800, 22100, 21900, 22300, 23000, 24200, 25000, 26500, 27800, 29000, 29400, 30100, 29700, 30400, 31100, 31700, 32200],
    'Italy':       [24200, 23800, 23100, 22800, 22200, 21100, 20400, 20300, 20700, 21100, 21500, 21800, 22000, 21300, 22200, 22100, 22500, 22900, 23200, 23400]
}

hist_trends = {
    'USA':         [27800, 28400, 29100, 29800, 30600, 31800, 32600, 33500, 33100, 33300, 33900, 34500, 35100, 35800],
    'Germany':     [27200, 27500, 27800, 28100, 28000, 28200, 28500, 28900, 29100, 28900, 28800, 29000, 29200, 29500],
    'Netherlands': [24500, 25000, 25500, 26200, 27000, 27800, 28400, 29100, 29500, 29200, 29500, 29900, 30200, 30600],
    'France':      [23400, 23600, 23900, 24200, 24500, 24900, 25300, 25800, 26100, 26300, 26600, 26900, 27300, 27800],
    'UK':          [19200, 19600, 20100, 20800, 21600, 22400, 23300, 24400, 25100, 25600, 25900, 26200, 26600, 26800],
    'Ireland':     [13500, 14200, 15100, 16200, 17500, 18800, 20100, 21500, 22200, 22800, 23500, 24400, 25200, 25900],
    'Italy':       [21500, 21800, 22200, 22600, 23100, 23500, 23900, 24300, 24500, 24300, 24200, 24300, 24400, 24300]
}

# 3. Build full DataFrame
full_data = {}
for country in data_2007_onwards.keys():
    full_data[country] = hist_trends[country] + data_2007_onwards[country]

df_raw = pd.DataFrame(full_data, index=years_extended)

# 4. Configure Plot Styling
colors = {
    'USA': '#1f77b4',       # Blue
    'Ireland': '#2ca02c',   # Green
    'Germany': '#d62728',   # Red
    'France': '#ff7f0e',    # Orange
    'Netherlands': '#9467bd',# Purple
    'UK': '#8c564b',        # Brown
    'Italy': '#e377c2'      # Pink
}

styles = {
    'USA': '-', 
    'Ireland': '--', 
    'Germany': '-', 
    'France': '-.', 
    'Netherlands': ':', 
    'UK': '-', 
    'Italy': '-'
}

# 5. Generate four vertically stacked plots, each normalized to its start year
start_years = [1999, 2008, 2016, 2020]

fig, axes = plt.subplots(len(start_years), 1, figsize=(12, 20), sharex=False)

for ax, start in zip(axes, start_years):
    df = df_raw.loc[start:]
    df_norm = df.div(df.iloc[0]) * 100

    for country in df_norm.columns:
        ax.plot(
            df_norm.index,
            df_norm[country],
            label=country,
            color=colors[country],
            linestyle=styles[country],
            linewidth=2.5
        )

    # Titles and axis labels
    ax.set_title(
        f'Normalized to {start} = 100',
        fontsize=13, fontweight='bold', pad=10
    )
    ax.set_ylabel(f'Index ({start} = 100)', fontsize=11)

    # X-axis intervals every 3 years from the start year
    ax.set_xticks(np.arange(start, 2027, 3))

    # Grid and baseline marker
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.axhline(100, color='black', linewidth=0.8, linestyle='--')

    # Legend on each subplot
    ax.legend(loc='upper left', frameon=True, facecolor='white', edgecolor='none')

# Shared X-axis label on the bottom subplot
axes[-1].set_xlabel('Year', fontsize=12)

# Overall figure title
fig.suptitle(
    'Evolution of Real Median Household Disposable Income',
    fontsize=16, fontweight='bold'
)

# Adjust layout padding and save output image
fig.tight_layout(rect=[0, 0, 1, 0.99])
plt.savefig('disposable_income_normalized_panels.png', dpi=300)
plt.show()