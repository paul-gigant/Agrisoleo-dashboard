#######################################################################
#######################################################################
# DASH BOARD VIZUALISATION
#######################################################################
####################################################################### 
# Run this app with `python app_v2.py` and
# visit http://127.0.0.1:8051/ in your web browser.


from dash import Dash, html, dcc, Input, Output, State
from dash.exceptions import PreventUpdate
from dash.long_callback import DiskcacheLongCallbackManager
import dash_bootstrap_components as dbc
import diskcache
import plotly.express as px
import pandas as pd
import pickle
import base64
from dash import dash_table
import os
import datetime
import shutil
import time
from run_meta_analyse_V3 import run_meta_analyse

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)
app = Dash(__name__,external_stylesheets=external_stylesheets,title='Agrisoleo : SaaS dashboard',long_callback_manager=long_callback_manager)
server = app.server

def format_meta_data():
    global df_meta_data
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

global df_meta_data
df_meta_data = format_meta_data()

# list of used functions 
def generate_table(dataframe):
    return dash_table.DataTable(
            data = dataframe.to_dict('records'), 
            columns = [{'id': c, 'name': c} for c in dataframe.columns]
            )

def display_png_image(image_filename):
    if image_filename[0] == 0:
        i= 'Draft_img/draft_img.png'
        encoded_image = [base64.b64encode(open(i, 'rb').read())]
        displayed_images=[html.Img(src='data:image/png;base64,{}'.format(encoded_image[0].decode()))]
    else:
        encoded_image = [base64.b64encode(open(i, 'rb').read()) for i in image_filename]
        displayed_images=[html.Img(src='data:image/png;base64,{}'.format(encoded_image[i].decode())) for i in range(len(image_filename))]
    
    return displayed_images

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

def save_file(name, content):
    """Save a file uploaded in the Dash component"""
    data = content.encode("utf8").split(b";base64,")[1]
    with open(name, "wb") as fp:
        fp.write(base64.decodebytes(data))

def set_layout_options(df_meta_data):
    ''' Layout in order : "dropdown_periode","parameter_choice", dropdown_pilotage,dropdown_azimut
    dropdown_ecart,dropdown_ecarty,hauteur,tracker,units_choice 
    type : component_id'''

    dropdown_periode_option=[{'label':i, 'value':i} for i in df_meta_data.iloc[:,2].astype(str).unique()]
    parameter_choice_option=[{'label':i, 'value':i} for i in find_parameter_of_interest_in_batch(df_meta_data)]
    dropdown_pilotage_option=[{'label':str(i), 'value': i} for i in df_meta_data.iloc[:,20].unique()]              
    dropdown_azimut_option=[{'label':str(i), 'value':i} for i in df_meta_data.iloc[:,6].unique()]
    dropdown_ecart_option=[{'label':str(i), 'value':i} for i in df_meta_data.iloc[:,9].unique()]
    dropdown_ecarty_option=[{'label':str(i), 'value':i} for i in df_meta_data.iloc[:,10].unique()]
    hauteur_option=[{'label':str(i), 'value':i} for i in df_meta_data.iloc[:,15].unique()]
    tracker_option=[{'label':str(i), 'value':i} for i in df_meta_data.iloc[:,17].unique()]
    unit_choice_option=[{'label':'Fraction (%)','value': 'Fraction'},{'label':'Irradiance (W/m2)','value': 'Irradiance'},{'label':'PAR (W/m2)','value': 'PAR'},{'label':'PAR journalier(W/m2/day)','value': 'PARjour'}]
                
    return [dropdown_periode_option, parameter_choice_option, dropdown_pilotage_option,dropdown_azimut_option,dropdown_ecart_option,dropdown_ecarty_option,hauteur_option,tracker_option,unit_choice_option]

def set_layout_values(df_meta_data):
    ''' Layout in order : "dropdown_periode","parameter_choice", dropdown_pilotage,dropdown_azimut
    dropdown_ecart,dropdown_ecarty,hauteur,tracker,units_choice 
    type : value'''

    dropdown_periode_value = df_meta_data.iloc[0,2]
    parameter_choice_value = find_parameter_of_interest_in_batch(df_meta_data)[0]
    dropdown_pilotage_value = df_meta_data.iloc[0,20]
    dropdown_azimut_value=df_meta_data.iloc[0,6]
    dropdown_ecart_value=df_meta_data.iloc[0,9]
    dropdown_ecarty_value=df_meta_data.iloc[0,10]
    hauteur_value=df_meta_data.iloc[0,15]
    tracker_value=df_meta_data.iloc[0,17]
    units_choice_value = 'Fraction'
                        
    return [dropdown_periode_value, parameter_choice_value,dropdown_pilotage_value,dropdown_azimut_value,dropdown_ecart_value,dropdown_ecarty_value,hauteur_value,tracker_value,units_choice_value]

# Creation of the layout
def create_layout(df_meta_data):
    return html.Div(children=[ 
        html.Img(src='https://www.agrisoleo.fr/images/logo.gif'),
        html.Div(children=[
            html.H1('AGRISOLEO : Data Vizualisation Tool', style={'textAlign': 'center'}),
        ],
        style={'width':'100%','display': 'inline-block'}
        ),
    
        dcc.Upload(
            id = 'dataload',children=[
            'Drag and Drop or ', html.A('Select files')
            ], 
            style={'width': '30%','height': '60px','lineHeight': '60px','borderWidth': '1px','borderStyle': 'dashed','borderRadius': '5px',
            'textAlign': 'center','margin-left': 'auto', 'margin-right': 'auto'},
            multiple=True,
        ),
        html.Div(id='hidden-div-upload', style={'display':'none'}),

        html.Div([
            dcc.ConfirmDialog(
                id='confirm-upload',
                message='Les données excel ont été correctement importées.',
            ),
        ]),

        html.Div(children=[
            html.Div(children=[
                html.Button("Process data", id="runsript"),
                html.Button("Reset data", id="reset"),
            ],
            style={'display': 'inline-block'}
            ),
            html.Div(id='hidden-div', style={'display':'none'}),
            html.Div(id='hidden-div2', style={'display':'none'}),  
        ]),
        html.Progress(id="progress_bar"),
        html.Br(),
        html.Div([
                html.Button("Download metadata", id="btn_xlsx"),
                dcc.Download(
                    id="download-dataframe-xlsx",
                )   
            ]),
        html.Div(children= [
            html.Div(children=[
                html.H4('Selection de la période étudiée :'),
                dcc.Dropdown(
                    id="dropdown_periode",
                    #options=[{'label':i, 'value':i} for i in df_meta_data.iloc[:,2].astype(str).unique()], 
                    #value = df_meta_data.iloc[0,2],
                    options = set_layout_options(df_meta_data)[0],
                    value = set_layout_values(df_meta_data)[0],
                    clearable=False,
                    style={}
                ),
                html.H4('Choix du paramètre d\'interet :'),
                dcc.RadioItems(
                    id = "parameter_choice",
                    #options=[{'label':i, 'value':i} for i in find_parameter_of_interest_in_batch(df_meta_data)],
                    #value = find_parameter_of_interest_in_batch(df_meta_data)[0],
                    options = set_layout_options(df_meta_data)[1],
                    value = set_layout_values(df_meta_data)[1],
                    inline=True,
                    ),
            ]),
        
            html.H4('Choix des paramètres de comparaison :'),

            html.Div(children=[
                html.Div(children=[
                    html.P('Pilotage solaire :'),
                    dcc.Dropdown(
                        id="dropdown_pilotage",
                        #options=[{'label':str(i), 'value': i} for i in df_meta_data.iloc[:,20].unique()], 
                        #value=df_meta_data.iloc[0,20],
                        options = set_layout_options(df_meta_data)[2],
                        value = set_layout_values(df_meta_data)[2],
                        clearable=False,
                        ),
                ],
                style={'width':'30%','display': 'inline-block'},
                ),

                html.Div(children=[
                    html.P('Azimut :'),
                    dcc.Dropdown(
                        id="dropdown_azimut",
                        #options=[{'label':str(i), 'value':i} for i in df_meta_data.iloc[:,6].unique()],
                        #value=df_meta_data.iloc[0,6],
                        options = set_layout_options(df_meta_data)[3],
                        value = set_layout_values(df_meta_data)[3],
                        clearable=False,
                    ),
                ],
                style={'width':'30%','display': 'inline-block'},
                ),

                html.Div(children=[
                    html.P('Ecart inter-rang (x-direction) :'),
                    dcc.Dropdown(
                        id="dropdown_ecart",
                        #options=[{'label':str(i), 'value':i} for i in df_meta_data.iloc[:,9].unique()],
                        #value=df_meta_data.iloc[0,9],
                        options = set_layout_options(df_meta_data)[4],
                        value = set_layout_values(df_meta_data)[4],
                        clearable=False,
                    ),
                ],
                style={'width':'30%','display': 'inline-block'},
                ),

                html.Div(children=[
                    html.P('Ecart inter-rang (y-direction) :'),
                    dcc.Dropdown(
                        id="dropdown_ecarty",
                        #options=[{'label':str(i), 'value':i} for i in df_meta_data.iloc[:,10].unique()],
                        #value=df_meta_data.iloc[0,10],
                        options = set_layout_options(df_meta_data)[5],
                        value = set_layout_values(df_meta_data)[5],
                        clearable=False,
                    ),
                ],
                style={'width':'30%','display': 'inline-block'},
                ),

                html.Div(children=[
                    html.P('Hauteur tables'),
                    dcc.Dropdown(
                        id="hauteur",
                        #options=[{'label':str(i), 'value':i} for i in df_meta_data.iloc[:,15].unique()],
                        #value=df_meta_data.iloc[0,15],
                        options = set_layout_options(df_meta_data)[6],
                        value = set_layout_values(df_meta_data)[6],
                        clearable=False,
                    ),
                ],
                style={'width':'30%','display': 'inline-block'},
                ),

                html.Div(children=[
                    html.P('Tracker/fixe'),
                    dcc.Dropdown(
                        id="tracker",
                        #options=[{'label':str(i), 'value':i} for i in df_meta_data.iloc[:,17].unique()],
                        #value=df_meta_data.iloc[0,17],
                        options = set_layout_options(df_meta_data)[7],
                        value = set_layout_values(df_meta_data)[7],
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
                #options=[{'label':'Fraction (%)','value': 'Fraction'},{'label':'Irradiance (W/m2)','value': 'Irradiance'},{'label':'PAR (W/m2)','value': 'PAR'},{'label':'PAR journalier(W/m2/day)','value': 'PARjour'}],
                #value = 'Fraction',
                options = set_layout_options(df_meta_data)[8],
                value = set_layout_values(df_meta_data)[8],
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
            html.H4('Affichage des cartes d\'irradiances cumulées correspondantes :'),
            html.Div(
                id='img_heatmap',
                style={'width':'150%','display': 'inline-block'}
            )
        ],
        style={'width':'100%','display': 'inline-block'}
        ),
    ])

app.layout= create_layout(df_meta_data)

# Take all the .xlsx files in the uploader folder and place them in the working directory
@app.callback(
    Output('hidden-div-upload','children'),
    Output('confirm-upload', 'displayed'),
    Input('dataload','filename'),
    Input('dataload','contents'),
    prevent_initial_call=True,
)
def put_upload_content_in_workingdirectory(uploaded_filenames, uploaded_file_contents):
    """Save uploaded files and move them to the current directory"""
        
    for name, data in zip(uploaded_filenames, uploaded_file_contents):
        save_file(name, data)
    
    return html.Div(), True
        
# Run meta_analyse_v3.py
@app.long_callback(
    Output('hidden-div2', 'children'),
    
    Output(component_id="dropdown_periode", component_property="options"),
    Output(component_id="parameter_choice", component_property="options"),
    Output(component_id="dropdown_pilotage", component_property="options"),
    Output(component_id="dropdown_azimut", component_property="options"),
    Output(component_id="dropdown_ecart", component_property="options"),
    Output(component_id="dropdown_ecarty", component_property="options"),
    Output(component_id="hauteur", component_property="options"),
    Output(component_id="tracker", component_property="options"),
    Output(component_id="units_choice", component_property="options"),
    Output(component_id="dropdown_periode", component_property="value"),
    Output(component_id="parameter_choice", component_property="value"),
    Output(component_id="dropdown_pilotage", component_property="value"),
    Output(component_id="dropdown_azimut", component_property="value"),
    Output(component_id="dropdown_ecart", component_property="value"),
    Output(component_id="dropdown_ecarty", component_property="value"),
    Output(component_id="hauteur", component_property="value"),
    Output(component_id="tracker", component_property="value"),
    Output(component_id="units_choice", component_property="value"),
    
    Input("runsript", "n_clicks"),

    running=[
        (Output("runsript", "disabled"), True, False),
        (
            Output("progress_bar", "style"),
            {"visibility": "visible"},
            {"visibility": "hidden"},
        ),
    ],
    manager=long_callback_manager,
)
def run_script(n_clicks):
    '''Run function meta_analyse from 'run_meta_analyse.py'
    i.e: process the data when trigger and reload the page for display '''
    
    global df_meta_data
    if not n_clicks:
        raise PreventUpdate
    
    if n_clicks:
        run_meta_analyse()
        df_meta_data = format_meta_data()
    
    options = set_layout_options(df_meta_data)
    values = set_layout_values(df_meta_data)
    
    return  html.Div(), options[0], options[1],options[2],options[3],options[4],options[5],options[6],options[7],options[8],values[0],values[1],values[2],values[3],values[4],values[5],values[6],values[7],values[8]

# Clear data, i.e : delete /img folder and sauvegarde file
@app.callback(
    Output('hidden-div', 'children'),
    Input("reset", "n_clicks"),
    prevent_initial_call=True,
)
def reset(n_clicks):
    '''Reset data stored in working directory and reload page with empty value
    Delete 'sauvegarde', '/img' and all excel files '''

    global df_meta_data
    if not n_clicks:
        raise PreventUpdate

    # Remove /img, sauvegarde and all .xlsx files
    if os.path.exists('img') == True:
        shutil.rmtree('img')
    if os.path.exists('sauvegarde') == True:
        os.remove('sauvegarde')
    for file in os.listdir():
        if file.endswith('.xlsx'):
            os.remove(file)
    
    df_meta_data = format_meta_data()
    set_layout_options(df_meta_data)
    set_layout_options(df_meta_data)
    app.layout = create_layout(df_meta_data)
    
    return html.Meta(httpEquiv="refresh",content="1")

# Callback for display
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
    ''' Process the result of the meta_analyse in order for proper display in the layout '''

    global df_meta_data
    df_meta_data = format_meta_data()
    
    # Filtering for period
    mask_periode = df_meta_data['start_date'] == period
    df_periode = df_meta_data[mask_periode]

    # Filtering for bar graph
    df = df_periode
    
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
    ''' Download the meta data created by 'run_meta_analyse.py' '''
    return dcc.send_data_frame(df_meta_data.to_excel, "metadata.xlsx", sheet_name="Sheet_name_1")

# Download results table
@app.callback(
    Output(component_id="download-result-xlsx", component_property="data"),
    Input(component_id="table_xlsx", component_property="n_clicks"),
    prevent_initial_call=True,
)
def function(n_clicks):
    ''' Download the data contained in the html.Table '''
    return dcc.send_data_frame(dfff.to_excel, "results.xlsx", sheet_name="Sheet_name_1")


# Run the app 
if __name__ == '__main__':
    app.run(debug=True,port = 8052)