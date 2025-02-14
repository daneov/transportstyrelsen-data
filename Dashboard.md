---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.16.6
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Data Insights

See the [README](README.md) on why, what and how.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-input]
---
import pandas as pd

def read_data():
    return pd.read_csv("transportstyrelsen_data.csv")

def sanitize(df):
    df['Date'] = pd.to_datetime(df['Date'], format='ISO8601')
    df['Evaluating cases'] = pd.to_datetime(df['Evaluating cases'])

    return df

df = sanitize(read_data())
df['Progressed cases'] = df['Evaluating cases'].diff().dt.days
df['ISO_WEEK'] = df['Date'].dt.strftime('%G-%V')
grouped_by_week = df.sort_values(by=['Date']).groupby('ISO_WEEK', as_index=True)
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-input]
---
current_date = df.iloc[-1]['Evaluating cases'].strftime('%Y-%m-%d')
print(f"Currently processing: {current_date}")
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

## Case handling duration

We define the processing time as the difference between the date on Transportstyrelsen.se and the date of the scrape.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

### Processing time evolution per week

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-input]
---
import plotly.graph_objects as go
from plotly.subplots import make_subplots

processing_time_per_week = grouped_by_week['Processing time'].agg(['mean']).round({'mean': 2}).reset_index()
max_processing_time = processing_time_per_week['mean'].max()

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=processing_time_per_week['ISO_WEEK'],
        y=processing_time_per_week['mean'],
        mode='lines+markers',
        name='Mean Processing Time',
        line=dict(width=2),
        marker=dict(
            size=8,
            color='red',
            opacity=0.5
        ),
        hovertemplate='Week: %{x}<br>Processing Time: %{y:.2f}<extra></extra>'
    )
)

# Update layout
fig.update_layout(
    title='Mean Processing Time Per Week',
    xaxis=dict(type='category'),
    xaxis_title='ISO_WEEK',
    yaxis_title='Mean Processing Time',
    yaxis_range=[0, processing_time_per_week['mean'].max() + 1],
    showlegend=True,
    template='plotly_white'
)

# Make the plot responsive
fig.update_layout(
    autosize=True,
)

# Display the figure
fig.show(config={
    'responsive': True
})
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-input]
---
# Calculate mean, least and most processing time fluctuations in a week
# grouped_by_week['Processing time'].agg(['mean']).round({'mean': 2})

weekly_processing = grouped_by_week['Processing time'].agg(['mean']).round({'mean': 2}).reset_index()

# Create a heatmap/block chart
fig = go.Figure(
    go.Heatmap(
        x=weekly_processing['ISO_WEEK'],
        y=['Processing Time'],  # Single row
        z=[weekly_processing['mean']],  # Needs to be 2D array
        text=[[f'{val:.2f}' for val in weekly_processing['mean']]],  # Display values
        texttemplate='%{text}',
        textfont={"size": 14},
        colorscale='Blues',
        showscale=True,
        colorbar_title='Days',
        hoverongaps=False,
        hovertemplate='Week: %{x}<br>Processing Time: %{z:.2f} days<extra></extra>'
    )
)

# Update layout
fig.update_layout(
    title='Mean Processing Time Per Week',
    xaxis=dict(type='category'),
    xaxis_title='ISO_WEEK',
    yaxis_title='',
    template='plotly_white',
    height=300,  # Reduced height since it's a single row
    yaxis={'showgrid': False},  # Remove y-axis grid
)

# Display the figure with responsive configuration
fig.show(config={
    'responsive': True
})
```

### Dates handled

```{code-cell} ipython3
---
tags: [remove-input]
---
weekly_processed = grouped_by_week['Progressed cases'].agg(['sum']).rename(columns={"sum": "Processed cases"})
weekly_processed = weekly_processed.reset_index()

fig = go.Figure(
    go.Bar(
        x=weekly_processed['ISO_WEEK'],
        y=weekly_processed['Processed cases'],
        marker_color='rgb(55, 83, 109)',
        hovertemplate='Week: %{x}<br>Processed Cases: %{y:,.0f}<extra></extra>'
    )
)

# Update layout
fig.update_layout(
    title='Weekly Processed Cases',
    xaxis_title='ISO_WEEK',
    yaxis_title='Number of Processed Cases',
    template='plotly_white',
    height=400,  # Only set height, let width be responsive
    bargap=0.2,
    showlegend=False
)

# Add y-axis thousands separator
fig.update_yaxes(separatethousands=True)

# Display the figure - setting config for better responsiveness
fig.show(config={
    'responsive': True
})
```
