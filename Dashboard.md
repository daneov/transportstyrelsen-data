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
df['Week'] = df['Date'].dt.strftime('%Y-%U')
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
from bokeh.plotting import figure, show, output_notebook
from bokeh.models import HoverTool
from bokeh.models import DatetimeTickFormatter
# Enable the output to be displayed in the notebook 
output_notebook(hide_banner=True)

processing_time_per_week = grouped_by_week['Processing time'].agg(['mean']).round({'mean': 2}).reset_index()
max_processing_time = processing_time_per_week['mean'].max()

p = figure(title="Mean Processing Time Per Week",
           x_axis_label='Week',
           y_axis_label='Mean Processing Time',
           x_range=processing_time_per_week['Week'].tolist(),
           y_range=(0, max_processing_time + 1),
           width=800, 
           height=400,
           sizing_mode='scale_both'
)

p.line(processing_time_per_week['Week'], processing_time_per_week['mean'], legend_label='Mean Processing Time', line_width=2)
p.scatter(processing_time_per_week['Week'], processing_time_per_week['mean'], size=8, color='red', alpha=0.5)

show(p, notebook_handle=True)
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
