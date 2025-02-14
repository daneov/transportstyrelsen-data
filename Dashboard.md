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
df['Week'] = df['Date'].dt.strftime('%G-%V')
grouped_by_week = df.groupby('Week', as_index=True)
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
        x=processing_time_per_week['Week'],
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
    xaxis_title='Week',
    yaxis_title='Mean Processing Time',
    yaxis_range=[0, processing_time_per_week['mean'].max() + 1],
    width=800,
    height=400,
    showlegend=True,
    template='plotly_white'
)

# Make the plot responsive
fig.update_layout(
    autosize=True,
)

# Display the figure
fig.show()
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-input]
---
# Calculate mean, least and most processing time fluctuations in a week
grouped_by_week['Processing time'].agg(['mean']).round({'mean': 2})
```

### Dates handled

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-input]
---
# This shows us how many days' worth of cases were handled on a given day.
df['Progressed cases'] = df['Evaluating cases'].diff().dt.days
```

```{code-cell} ipython3
grouped_by_week['Progressed cases'].agg(['sum']).rename(columns={"sum": "Processed dates"})
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
---

```
