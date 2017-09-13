__author__ = "Siddharth Chandrasekaran"
__license__ = "GPL"
__version__ = "1.0.1"
__email__ = "schandraseka@umass.edu"

import pandas as pd

from bokeh.core.properties import field
from bokeh.io import curdoc
from bokeh.layouts import layout
from bokeh.models import (ColumnDataSource, HoverTool, SingleIntervalTicker, Slider, CategoricalColorMapper, Button,)
from bokeh.palettes import Plasma256
from bokeh.plotting import figure	
from bokeh.io import output_notebook, show
import numpy as np

output_notebook()

def source_update(attrname, old, new):
    year = slider.value
    source.data = info[year]

def slider_update():
    year = slider.value + 1
    #For looping
    if year > years[-1]:
        year = 1950
    slider.value = year

def animation():
    if button.label == 'Play':
        button.label = 'Pause'
        curdoc().add_periodic_callback(slider_update, 100)
    else:
        button.label = 'Play'
        curdoc().remove_periodic_callback(slider_update)

gdp_df = pd.read_excel("gdp.xlsx",index_col=0)
life_expectancy_df = pd.read_excel("life_expectancy.xlsx",index_col=0)
population_df = pd.read_excel("population.xlsx",index_col=0)


#Converting years to integers in all datasets
cols = list(gdp_df.columns)
years = list(range(int(cols[0]), int(cols[-1])))
rename_dict = dict(zip(cols, years))
gdp_df = gdp_df.rename(columns=rename_dict)
life_expectancy_df = life_expectancy_df.rename(columns=rename_dict)
population_df = population_df.rename(columns=rename_dict)

# Common countries across all data. Otherwise the panel operation will fail because of reindexing
gdp_df = gdp_df.drop(gdp_df.index.difference(life_expectancy_df.index))
population_df = population_df.drop(population_df.index.difference(life_expectancy_df.index))

# Population has to converted to viable radius sizes. India and China have huge populations and lot of countries of missing data
# Normalizing population into population_size and adding missing data with least value
scale_quantity = 200
# Achieved this by trial and error
population_size = np.sqrt(population_df/scale_quantity)*10 /scale_quantity
# For values NA 
min_size = 4
population_df = population_size.where(population_size >= min_size).fillna(min_size)
#Normalizing GDP by using sqrt since GDP of Qatar, Macau and Kuwait are really high
gdp_df = np.sqrt(gdp_df)

#Here countries can be accessed using 'index'
panel = pd.Panel({'gdp': gdp_df, 'life': life_expectancy_df, 'population': population_df})

info = {}


# Since data is continuously available only after 1950
for year in years:
    if year >=1950:
    	info[year] = panel.loc[:,:,year].reset_index().to_dict('series')

source = ColumnDataSource(data=info[1950])

plot = figure(x_range=(1, 500), y_range=(20, 100), title='GDP per capita V/S Life Expectancy', plot_height=500, plot_width = 1000)
plot.xaxis.ticker = SingleIntervalTicker(interval=25)
plot.xaxis.axis_label = "Sqrt(GDP per capita) of the Country (in $s)"
plot.yaxis.ticker = SingleIntervalTicker(interval=20)
plot.yaxis.axis_label = "Life expectancy at birth (years)"

# Using plasma256 due to the number of different countries available (261)
color_mapper = CategoricalColorMapper(palette=Plasma256, factors=list(life_expectancy_df.index.unique()))
plot.circle(
    x='gdp',
    y='life',
    size='population',
    source=source,
    fill_color={'field': 'index', 'transform': color_mapper},
)


plot.add_tools(HoverTool(tooltips="@index", show_arrow=False, point_policy='follow_mouse'))
slider = Slider(start=1950, end=years[-1], value=1950, step=1, title="Year")
slider.on_change('value', source_update)
button = Button(label='Play', width=60)
button.on_click(animation)

layout = layout([
    [plot],
    [slider, button],
])
curdoc().add_root(layout)
curdoc().title = "690V Assignment Gapminder Dataset"
show(layout)
