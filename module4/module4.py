import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

soql_url = ('https://data.cityofnewyork.us/resource/uvpi-gqnh.json?$select=distinct spc_common&$order=spc_common').replace(' ','%20')
soql_trees = pd.read_json(soql_url).dropna()

soql_url = ('https://data.cityofnewyork.us/resource/uvpi-gqnh.json?$select=distinct%20boroname&$order=boroname').replace(' ', '%20')
soql_boros = pd.read_json(soql_url).dropna()

app.layout = html.Div([
    html.Label('Tree Species'),
    dcc.Dropdown(
        id='spc',
        options=[
            {'label': s, 'value': s} for s in soql_trees['spc_common']
        ]
    ),
    html.Label('Borough'),
    dcc.Dropdown(
        id='bor',
        options=[
            {'label': s, 'value': s} for s in soql_boros['boroname']
        ]
    ),
    html.Div(id='my-div'),
    dcc.Checklist(
        id='stw',
        options=[{'label': 'Steward', 'value': 'Y'}]
    ),
    dcc.Graph(id='graph-1')
])


@app.callback(
    Output(component_id='my-div', component_property='children'),
    [Input(component_id='spc', component_property='value'),
     Input(component_id='bor', component_property='value')]
)
def update_output_div(tree_spc, boroname):
    if (tree_spc and boroname):
        return 'You\'ve selected "{}" in {}'.format(tree_spc, boroname)
    else:
        return 'Please complete selection'

@app.callback(
    Output(component_id='graph-1', component_property='figure'),
    [Input(component_id='spc', component_property='value'),
     Input(component_id='bor', component_property='value'),
     Input(component_id='stw', component_property='value')]
)
def update_output_graph_1(tree_spc, boroname, steward):
    if (tree_spc and boroname and steward):
        return get_figure_by_steward_graph_1(tree_spc, boroname)
    elif (tree_spc and boroname):
        soql_url = ("https://data.cityofnewyork.us/resource/uvpi-gqnh.json?" +\
            "$select=health,count(spc_common)&" +\
            "$where=health is not null and spc_common='{0}' and boroname='{1}'&" +\
            "$group=health").format(tree_spc, boroname).replace(' ', '%20')
        df = pd.read_json(soql_url)
        sum_spc = sum(df['count_spc_common'])
        return {
            'data': [
                {'x': df['health'], 'y': df['count_spc_common'], 'type': 'bar', 'name': 'None'},
            ],
            'layout': {
                'title': 'Proportions by Health of %d "%s" Trees in %s' % (sum_spc, tree_spc, boroname)
            }
        }
    else:
        raise PreventUpdate
        
def get_figure_by_steward_graph_1(tree_spc, boroname):
    soql_url = ("https://data.cityofnewyork.us/resource/uvpi-gqnh.json?" +\
            "$select=steward,health,count(steward)&" +\
            "$where=health is not null and steward is not null and spc_common='{0}' and boroname='{1}'&" +\
            "$group=steward,health").format(tree_spc, boroname).replace(' ', '%20')
    df = pd.read_json(soql_url)
    sum_spc = sum(df['count_steward'])
    lst = list()
    for s in df['steward'].unique():
        lst.append({'x': df[df['steward'] == s]['health'], 'y': df[df['steward'] == s]['count_steward'], 'type': 'bar', 'name': 'Steward: %s' % s})
    return {
            'data': lst,
            'layout': {
                'barmode': 'stack',
                'title': 'Proportions by Health of %d "%s" Trees in %s' % (sum_spc, tree_spc, boroname)
            }
        }

if __name__ == '__main__':
    app.run_server(debug=True)