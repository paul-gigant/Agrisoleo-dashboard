#######################################################################
#######################################################################
# DASH BOARD VIZUALISATION
#######################################################################
####################################################################### 
# Run this app with `python app_v2.py` and
# visit http://127.0.0.1:8051/ in your web browser.


from dash import Dash, html, dcc, Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd
import pickle
import base64
import datetime
from dash import dash_table
from analyse_v8 import data_analysis
from pickle import *
import os

app = Dash(__name__)

server = app.server

def format_meta_data():
    if os.path.isfile('sauvegarde') == True:
        # Open and clean data : 
        f = open('sauvegarde','rb')
        meta_data = pickle.load(f)
        print('sauvegarde file exists')

    else:
        meta_data = [[0]*44] * 44
        print('there is no sauvegarde file in working directory')

    # Add column names to all colums of the dataset meta_analysis
    df_meta_data = pd.DataFrame(meta_data, columns= ['lattitude',
                                                    'longitude',
                                                    'start_date',
                                                    'end_date',
                                                    'xsize_field',
                                                    'ysize_field',
                                                    'azimut',
                                                    'xsize_module',
                                                    'ysize_module',
                                                    'xgap_module',
                                                    'ygap_module',
                                                    'nb_module_x',
                                                    'nb_module_y',
                                                    'offset_SaaS',
                                                    'yoffset_SaaS',
                                                    'hauteur',
                                                    'opacite',
                                                    'tracker',
                                                    'orientation_static',
                                                    'orientation_maximale',
                                                    'backtracking',
                                                    'resolution',
                                                    'frequence',
                                                    'zt', 
                                                    'zt_fraction',
                                                    'zt_par',
                                                    'zt_parperday',
                                                    'zsp', 
                                                    'zsp_fraction', 
                                                    'zsp_par', 
                                                    'zsp_parperday',
                                                    'zir', 
                                                    'zir_fraction', 
                                                    'zir_par', 
                                                    'zir_parperday',
                                                    'zaPV', 
                                                    'zaPV_fraction', 
                                                    'zaPV_par', 
                                                    'zaPV_parperday',            
                                                    'heterogeneity',
                                                    'name_png_config',
                                                    'name_png_heatmap',
                                                    'name_png_heatmap_PAR',
                                                    'name_png_heatmap_Fraction'
                                ])
    return df_meta_data

df_meta_data = format_meta_data()

# list of used functions 
def generate_table(dataframe):
    return dash_table.DataTable(
            data = dataframe.to_dict('records'), 
            columns = [{'id': c, 'name': c} for c in dataframe.columns]
            )

def display_png_image(image_filename):
    encoded_image = [base64.b64encode(open(i, 'rb').read()) for i in image_filename]
    return [html.Img(src='data:image/png;base64,{}'.format(encoded_image[i].decode())) for i in range(len(image_filename))]

def find_parameter_of_interest_in_batch(df):
    # filter only configuration parameters 
    parameters = df.iloc[:,0:22]

    list_columns_of_interest = []
    for i in parameters.columns.tolist():
        if len(parameters[i].unique())>1:
            list_columns_of_interest.append(i)
    # In case there is no data yet
    if list_columns_of_interest == []:
        list_columns_of_interest = ['azimut']

    return list_columns_of_interest


# Creation of the layout
def create_layout():
    return html.Div(children=[
        html.Img(src='https://www.agrisoleo.fr/images/logo.gif'),
        html.Div(children=[
            html.H1('AGRISOLEO : Data Vizualisation Tool', style={'textAlign': 'center'}),
        ],
        style={'width':'100%','display': 'inline-block'}
        ),
        html.Div([
                html.Button("Process data", id="runsript"),
                html.Div(id='output-container-button',
                                children='Hit the button to update.')
        ]),
        html.Br(),
        html.Div([
                html.Button("Download metadata", id="btn_xlsx"),
                dcc.Download(id="download-dataframe-xlsx"),
            ]),
        html.Div(children= [
            html.Div(children=[
                html.H4('Selection de la période étudiée :'),
                dcc.Dropdown(
                    id="dropdown_periode",
                    options=[{'label':i, 'value':i} for i in df_meta_data.iloc[:,2].astype(str).unique()], 
                    value = df_meta_data.iloc[0,2],
                    clearable=False,
                    style={}
                ),
                html.H4('Choix du paramètre d\'interet :'),
                dcc.RadioItems(
                    id = "parameter_choice",
                    options=[{'label':i, 'value':i} for i in find_parameter_of_interest_in_batch(df_meta_data)],
                    value = find_parameter_of_interest_in_batch(df_meta_data)[0],
                    inline=True,
                    ),
            ]),
        
            html.H4('Choix des parametres de comparaison (le parametre d\'interet n\'a pas d\'action) :'),

            html.Div(children=[
                html.Div(children=[
                    html.P('Pilotage solaire :'),
                    dcc.Dropdown(
                        id="dropdown_pilotage",
                        options=[{'label':str(i), 'value': i} for i in df_meta_data.iloc[:,20].unique()], 
                        value=df_meta_data.iloc[0,20],
                        clearable=False,
                        ),
                ],
                style={'width':'30%','display': 'inline-block'},
                ),

                html.Div(children=[
                    html.P('Azimut :'),
                    dcc.Dropdown(
                        id="dropdown_azimut",
                        options=[{'label':str(i), 'value':i} for i in df_meta_data.iloc[:,6].unique()],
                        value=df_meta_data.iloc[0,6],
                        clearable=False,
                    ),
                ],
                style={'width':'30%','display': 'inline-block'},
                ),

                html.Div(children=[
                    html.P('Ecart inter-rang (x-direction) :'),
                    dcc.Dropdown(
                        id="dropdown_ecart",
                        options=[{'label':str(i), 'value':i} for i in df_meta_data.iloc[:,9].unique()],
                        value=df_meta_data.iloc[0,9],
                        clearable=False,
                    ),
                ],
                style={'width':'30%','display': 'inline-block'},
                ),

                html.Div(children=[
                    html.P('Ecart inter-rang (y-direction) :'),
                    dcc.Dropdown(
                        id="dropdown_ecarty",
                        options=[{'label':str(i), 'value':i} for i in df_meta_data.iloc[:,10].unique()],
                        value=df_meta_data.iloc[0,10],
                        clearable=False,
                    ),
                ],
                style={'width':'30%','display': 'inline-block'},
                ),

                html.Div(children=[
                    html.P('Hauteur tables'),
                    dcc.Dropdown(
                        id="hauteur",
                        options=[{'label':str(i), 'value':i} for i in df_meta_data.iloc[:,15].unique()],
                        value=df_meta_data.iloc[0,15],
                        clearable=False,
                    ),
                ],
                style={'width':'30%','display': 'inline-block'},
                ),

                html.Div(children=[
                    html.P('Tracker/fixe'),
                    dcc.Dropdown(
                        id="tracker",
                        options=[{'label':str(i), 'value':i} for i in df_meta_data.iloc[:,17].unique()],
                        value=df_meta_data.iloc[0,17],
                        clearable=False,
                    ),
                ],
                style={'width':'30%','display': 'inline-block'},
                ),
            ]),

            dcc.Graph(
                id="graph",
                style={},
                ),
            html.Br(),
        ],
        style={'width':'49%','display': 'inline-block','vertical-align': 'top'}
        ),
        
        html.Div(children=[
            html.H4('Selection des unités :'),
            dcc.RadioItems(
                id = "units_choice",
                options=[{'label':'Fraction (%)','value': 'Fraction'},{'label':'Irradiance (W/m2)','value': 'Irradiance'},{'label':'PAR (W/m2)','value': 'PAR'},{'label':'PAR journalier(W/m2/day)','value': 'PARjour'}],
                value = 'Fraction',
                inline=True,
                ),
            html.Br(),
            html.Div(
                id = "table",
            ),
            html.Div([
                html.Button("Download", id="table_xlsx"),
                dcc.Download(id="download-result-xlsx"),
    ])
        ],
        style={'width':'40%','display': 'inline-block','vertical-align': 'top','margin-left': '6vw'}
        ),

        html.Div(children=[
            html.Br(),
            html.H4('Affichage des configurations :'),
            html.Div(
                id='img_config'
            ),
        ],
        style={'width':'100%','display': 'inline-block'}
        ),

        html.Div(children=[
            html.Br(),
            html.H4('Affichage des cartes irradiances cumulées correspondantes :'),
            html.Div(
                id='img_heatmap',
                style={'width':'150%','display': 'inline-block'}
            )
        ],
        style={'width':'100%','display': 'inline-block'}
        ),
    ])

app.layout= create_layout()


# Run meta_analyse_v3.py
@app.callback(
    Output('output-container-button', 'children'),
    Input("runsript", "n_clicks"),
    prevent_initial_call=True,
)
def run_script(n_clicks):
    # Don't run unless the button has been pressed...
    if not n_clicks:
        raise PreventUpdate
    
    return exec(open('meta_analyse_v3.py').read())
  

# Callback
@app.callback(
    Output(component_id="graph", component_property="figure"),
    Output(component_id="table", component_property="children"),
    Output(component_id="img_config", component_property="children"), 
    Output(component_id="img_heatmap", component_property="children"), 
    Input(component_id="dropdown_periode", component_property="value"),
    Input(component_id="parameter_choice", component_property="value"),
    Input(component_id="dropdown_pilotage", component_property="value"),
    Input(component_id="dropdown_azimut", component_property="value"),
    Input(component_id="dropdown_ecart", component_property="value"),
    Input(component_id="dropdown_ecarty", component_property="value"),
    Input(component_id="hauteur", component_property="value"),
    Input(component_id="tracker", component_property="value"),
    Input(component_id="units_choice", component_property="value"),
)
def select_data_use_for_display(period,parameter,pilotage,azimut,ecart,ecarty,hauteur,tracker,units):
    # Filtering for period 
    df_meta_data = format_meta_data()

    df_periode = df_meta_data
    mask_periode = df_periode['start_date'] == period
    df_periode2 = df_periode[mask_periode]
    
    # Filtering for bar graph
    df = df_periode2
    if parameter == 'azimut':
        mask = (df['backtracking']==pilotage) &  (df['xgap_module']==ecart) &  (df['ygap_module']==ecarty) &  (df['hauteur']==hauteur) &  (df['tracker']==tracker)
    elif parameter == 'xgap_module':
        mask = (df['backtracking']==pilotage) &  (df['azimut']==azimut) &  (df['ygap_module']==ecarty) &  (df['hauteur']==hauteur) &  (df['tracker']==tracker)
    elif parameter == 'backtracking':
        mask = (df['xgap_module']==ecart) &  (df['azimut']==azimut) &  (df['ygap_module']==ecarty) &  (df['hauteur']==hauteur) &  (df['tracker']==tracker)
    elif parameter == 'ygap_module':
        mask = (df['backtracking']==pilotage) &  (df['xgap_module']==ecart) &  (df['azimut']==azimut) &  (df['hauteur']==hauteur) &  (df['tracker']==tracker)
    elif parameter == 'hauteur':
        mask = (df['backtracking']==pilotage) &  (df['xgap_module']==ecart) &  (df['ygap_module']==ecarty) &  (df['azimut']==azimut) &  (df['tracker']==tracker)
    elif parameter == 'tracker':
        mask = (df['backtracking']==pilotage) &  (df['xgap_module']==ecart) &  (df['ygap_module']==ecarty) &  (df['hauteur']==hauteur) &  (df['azimut']==azimut)

    dff = df[mask]
    
    
    # Filtering for table & bar graph   
    global dfff
    if units == 'Fraction':
        dfff = dff[[parameter, 'zt_fraction','zsp_fraction', 'zir_fraction', 'zaPV_fraction','heterogeneity']].astype(int)
        list_bar = ['zt_fraction','zsp_fraction', 'zir_fraction', 'zaPV_fraction']
        titre_bar = 'Partage lumineux cumulé (%)'
    elif units == 'Irradiance':
        dfff = dff[[parameter,'zt','zsp', 'zir', 'zaPV','heterogeneity']].astype(int)
        list_bar = ['zt','zsp', 'zir', 'zaPV']
        titre_bar = 'Partage lumineux cumulé (W/m2)'
    elif units == 'PAR':
        dfff = dff[[parameter, 'zt_par','zsp_par', 'zir_par', 'zaPV_par','heterogeneity']].astype(int)
        list_bar = ['zt_par','zsp_par', 'zir_par', 'zaPV_par']
        titre_bar = 'Partage lumineux cumulé PAR (W/m2)'
    elif units == 'PARjour':
        dfff = dff[[parameter, 'zt_parperday','zsp_parperday', 'zir_parperday', 'zaPV_parperday','heterogeneity']].astype(int)
        list_bar = ['zt_parperday','zsp_parperday', 'zir_parperday', 'zaPV_parperday']
        titre_bar = 'Partage lumineux cumulé en PAR journalier (W/m2/jour)'
    
    # Filtering for image display
    image_path = dff[['name_png_config','name_png_heatmap','name_png_heatmap_PAR','name_png_heatmap_Fraction']] 
    

    # Create figure from dataframe
    fig_bar = px.bar(dff, x=parameter, y=list_bar, 
            barmode = 'group',
            labels={
                "value": "Luminosité cumulée",
                "variable": ""
                },
            )
    fig_bar.update_layout(
        title={
            'text':titre_bar,
            'x':0.45,
            'xanchor':'center',
            'yanchor':'top',
        },
        font=dict(
            size=14,
        ),
    ),    
    fig_bar.update_xaxes(type='category')

    # Create table from dataframe
    table_content = generate_table(dfff)

    # Create displayed configuration images 
    configuration_images = display_png_image(image_path.iloc[:,0].tolist())

    # Create displayed heatmap images
    if units == 'Fraction':
        heatmap_images = display_png_image(image_path.iloc[:,3].tolist())
    elif units == 'Irradiance':
        heatmap_images = display_png_image(image_path.iloc[:,1].tolist())
    elif units == 'PAR':
        heatmap_images = display_png_image(image_path.iloc[:,2].tolist())
    elif units =='PARjour':
        heatmap_images = display_png_image(image_path.iloc[:,2].tolist())

    return fig_bar, table_content, configuration_images, heatmap_images 

# Download meta data 
@app.callback(
    Output("download-dataframe-xlsx", "data"),
    Input("btn_xlsx", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_data_frame(df_meta_data.to_excel, "metadata.xlsx", sheet_name="Sheet_name_1")

# Download results table
@app.callback(
    Output(component_id="download-result-xlsx", component_property="data"),
    Input(component_id="table_xlsx", component_property="n_clicks"),
    prevent_initial_call=True,
)
def function(n_clicks):
    return dcc.send_data_frame(dfff.to_excel, "results.xlsx", sheet_name="Sheet_name_1")


# Run the app 
if __name__ == '__main__':
    app.run_server(debug=True,port = 8051)
