import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, dash_table
from dash.dependencies import Input, Output

df = pd.read_csv('data/commodity_trade_statistics_data.csv')

# TABLE
table_header = [
    html.Thead(
        html.Tr([
            html.Th("Category"), 
            html.Th("Description")]), className='th-header')
]

row1 = html.Tr([
    html.Td("1"), 
    html.Td("Live animals")])
row2 = html.Tr([
    html.Td("2"), 
    html.Td("Meat and edible meat")])
row3 = html.Tr([
    html.Td("3"), 
    html.Td("Fish, crustaceans, molluscs and aquatic invertebrates")])
row4 = html.Tr([
    html.Td("4"), 
    html.Td("Dairy products: eggs, honey and edible animal")])
row5 = html.Tr([
    html.Td("5"), 
    html.Td("Products of animal origin")])
row6 = html.Tr([
    html.Td("6"), 
    html.Td("Live trees, plants, bulbs, roots, flowers, etc")])
row7 = html.Tr([
    html.Td("7"), 
    html.Td("Edible vegetables and certain roots and tubers")])

table_body = [html.Tbody([row1, row2, row3, row4, row5, row6, row7], className= 'table-body')]

def clean_df(df):
    # Drop duplicates
    df = df.drop_duplicates()
    # Drop Nan
    df = df.dropna()
    # Clean categories column, category 7 is repeated
    df.category = df.category.apply(
        lambda x: '07_edible_vegetables_and_certain_roots_and_tubers' \
            if x == '07_edible_vegetables_and_certain_roots_and_tu' else x)
    # Create an extra column with the number of the category
    df['category_num'] = df.category.apply(
        lambda x: int(x[1])
    )
    return df

df = clean_df(df)


# Dropdown values
years = list(df.year.drop_duplicates())
years.sort()
categories_num = list(df['category_num'].drop_duplicates())
categories_num.sort()

def dash_app_global(flask_app, path):
    app = Dash(
        __name__,
        server = flask_app,
        url_base_pathname=path,
        external_stylesheets = [dbc.themes.BOOTSTRAP]
    )

    app.layout = html.Div([
                    html.H1(
                        className='main-title',
                        children= 'Global trades by Commodities'
                    ),
                    html.Div([
                        html.H3(
                            className='subtitle',
                            children="Total traded by category along the years" 
                        ),
                        html.Div([
                            dcc.Graph(id='graph-evolution-categories'),
                            dbc.Table(
                                table_header + table_body, 
                                bordered=True,
                                hover=True,
                                responsive=True,
                                striped=False)],
                            className='evolution-graph',
                        ),
                        dcc.RangeSlider(
                            id='range-slider',
                            marks=years,
                            step=1,
                            value = [0, 1],
                            # dots=True, 
                            updatemode='mouseup', 
                            vertical= False
                        )
                    ]),
                    html.Div([
                        html.H3(
                            className='subtitle',
                            children="Total traded by commodity" 
                        ),
                        html.Div([
                            dcc.Dropdown(
                                id='years-picker', 
                                options = years,
                                value = years[-1]),
                            dcc.Dropdown(
                                id='categories-picker', 
                                options = categories_num,
                                value = categories_num[0]),
                        ], style={'width': '48%', 'display':'inline-block'}),
                        html.Div([
                            dcc.Graph(id='graph-commodities'),
                        ]),
                ], className= 'page-container')])
    
    @app.callback(
        Output(
            component_id='graph-evolution-categories',
            component_property='figure'),
        [Input(component_id='range-slider', component_property='value')])
    
    def update_bar_plot(years_input):
        years_range = years[years_input[0]:years_input[1]]
        df_short = df[df['year'].isin(years_range)]
        df_short = df_short.groupby(['category_num']).sum().\
            sort_values(by='trade_usd', ascending=False)
        data = go.Bar(
                    x=list(df_short.index),
                    y=list(df_short['trade_usd']),
                    marker=dict(
                    # set color equal to a variable
                    color=[1, 2, 3, 4, 5, 6, 7],
                    # one of plotly colorscales
                    # marker_color='#221f1f',
                    colorscale='teal'),
                    hovertemplate='<br>%{y}<br><extra></extra>')
        layout = go.Layout(
                    margin=dict(l=20, r=20, t=20, b=20),
                    bargap=0.1,
                    width = 650,
                    height = 450, 
                    bargroupgap=0.1,
                    showlegend=False,
                    template = 'plotly_white',
                    yaxis=dict(
                        title='Total traded (USD)',
                        title_standoff = 40,
                        showgrid = False, 
                        side= 'left'),
                    xaxis=dict(
                        title='Category',
                        autorange = True,
                        showgrid = False,
                        type= 'category'))
        fig = go.Figure({'data':data, 'layout':layout})
        return fig
       
    # @app.callback(
    #     Output(component_id='graph-commodities', component_property='figure'),
    #     [
    #     Input(component_id='years-picker', component_property='value'),
    #     Input(component_id='categories-picker', component_property='value')])

    # def update_bubble_plot(selected_year, selected_category):
    #     print(selected_year)
    #     print(selected_category)

    return app.server

def dash_app(flask_app):
    app = Dash(
        __name__,
        server = flask_app,
        external_stylesheets= ['static/css/styles.css'],
        url_base_pathname='/dash/'
    )

    app.layout = html.Div(

    )
    
    return app.server