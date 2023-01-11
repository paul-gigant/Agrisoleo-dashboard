######################################################################################
# This program is the list of functions used to extract and compute the data for one simulation.
# anaylse_v9 do the exact same thing as anylse_v8 but convert xlsx files to csv before
# Last update : 11/01/2023 
######################################################################################

# List of python librairies : 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
import seaborn as sns
import scipy
import matplotlib
from xlsx2csv import Xlsx2csv




# To use the function as a backend code, i.e : don't open the matplotlib GUI interface
matplotlib.use('Agg')

# Class Table and Field definition that contains the (x,y) coordinate of the left corner of a table  
class Table:
    def __init__(self, coordinate):
        self.coordinate = coordinate
class Field:
    def __init__(self, coordinate):
        self.coordinate = coordinate

# List of functions used in data_analysis function :

def convert_xlsx_to_csv(filename,i):
    Xlsx2csv(filename,outputencoding="utf-8",).convert(filename+ str(i) +'.csv',sheetid=i)

def read_excel(filename):
    '''Read Agrisoleo output .xlsx files
     return sheet1, sheet3 '''
    #input = pd.read_excel(filename,sheet_name=0,header = None)
    #field_data = pd.read_excel(filename,sheet_name=2,header = None)
    
    convert_xlsx_to_csv(filename,1)
    convert_xlsx_to_csv(filename,3)

    input = pd.read_csv(filename +'1.csv',header=None)
    field_data = pd.read_csv(filename+'3.csv',header=None)
    return input, field_data

def plot_to_heatmap_coordinate(x,y,size_heatmap):
        '''Convert plot coordinate into seaborn heatmap coordinate
        In practice : x-axis is the same and y-axis is inverted'''
        return (x,size_heatmap-y)

def extraction_of_configuration(input_file, xshape_field_data ,yshape_field_data):
    ''' Read input sheet of xlsx file from Agrisoleo SaaS 
    and extract configuration informations :
    Return : size_field (tuple), offset_field (tuple,) size_module (tuple), number_module (tuple), gap_module (tuple),
     resolution (int),azimut (int), start_date (date), end_date (date), nb_days (int), 
     tracker (bool), backtracking (bool), calibration (tuple) '''
    
    size_field = (float(input_file.iloc[2,1]),float(input_file.iloc[2,2]))
    size_module = (float(input_file.iloc[8,1]),float(input_file.iloc[8,2]))
    number_module = (int(input_file.iloc[10,1]),int(input_file.iloc[10,2]))
    gap_module = (float(input_file.iloc[11,1]),float(input_file.iloc[11,2]))
    resolution = float(input_file.iloc[25,1])
    azimut = float(input_file.iloc[5,1])
    start_date = input_file.iloc[26,1]
    end_date = input_file.iloc[27,1]

    #nb_days_temp = end_date-start_date
    #nb_days = nb_days_temp.total_seconds()/(3600*24)
    nb_days = 23
    
    if input_file.loc[16,1] =='OUI':
        tracker = True
    elif input_file.loc[16,1] =='NON':
        tracker = False
    if input_file.loc[19,1] =='OUI':
        backtracking = True
    elif input_file.loc[19,1] =='NON':
        backtracking = False
    
    # offset_field correspond to the offset of the field regarding the entire image. 
    # the field is always places in the middle of the image
    offset_field = ( (xshape_field_data-size_field[0]*resolution)/2 , (yshape_field_data-size_field[1]*resolution)/2 )

    offset_SaaS = (float(input_file.iloc[9,1]),float(input_file.iloc[9,2])) #data from SaaS corresponding to the middle of the module 
    offset = (offset_SaaS[0]-size_module[0]/2 , offset_SaaS[1]-size_module[1]/2)
    calibration = (offset[0]*resolution+offset_field[0] , offset[1]*resolution+offset_field[1]) #calibration par rapport au décalage du champs dans la fenetre

    coordonne_site = (float(input_file.iloc[4,1]),float(input_file.iloc[4,2]))
    hauteur = float(input_file.iloc[12,1])
    opacite = float(input_file.iloc[13,1])
    orientation_static = float(input_file.iloc[17,1])
    orientation_maximale = float(input_file.iloc[18,1])
    frequence = input_file.iloc[28,1]

    return [size_field, offset_field, size_module, number_module, gap_module, resolution, azimut, start_date, end_date, 
            nb_days, tracker, backtracking, calibration,
            coordonne_site, hauteur, opacite, orientation_static,orientation_maximale, frequence,offset_SaaS]

def create_field(xcoordinate, ycoordinate):
    ''' Create Field object from Field class that will contains field coordinate'''
    return Field((xcoordinate, ycoordinate))

def create_table_list(number_module, gap_module, calibration, resolution):
    ''' Put all table object in a list : 
    'list_table is a x-list that contains the y-list of all table'''

    list_table = [] 
    nb_x = number_module[0]
    nb_y = number_module[1]
    xoffset_first_module = calibration[0]
    yoffset_first_module = calibration[1]
    xgap_module = gap_module[0]*resolution
    ygap_module = gap_module[1]*resolution

    def generateur_xrow(n,x,y):
        ''' Create table object from Table class for the x-direction'''
        for i in range(n):
            yield Table((x+i*xgap_module,y))
            
    def generateur_yrow(n,x,y):
        ''' Create table object from Table class for the y-direction'''
        for i in range(n):
            if i !=0:
                yield Table((x,y+i*ygap_module))

    for i in generateur_xrow(nb_x,xoffset_first_module,yoffset_first_module):
        list_table.append([i])

    for i in range(len(list_table)): 
        x = list_table[i][0].coordinate[0]
        y = list_table[i][0].coordinate[1]
        list_table[i].extend(generateur_yrow(nb_y,x,y))

    return list_table

def create_AgriPV_zone(number_module, list_table, size_module, resolution,tracker):
    '''Dimensioning of the zone of interest AgriPV for a calculation of results without edge effects.
    The area of interest will be by default the half of the middle table taken in its center.
    Warning : Depending of the tracking configuration, the studied area does not have the same definition'''

    # Identification de la table d'interet :
    pos_table_x = math.ceil((number_module[0]-1)/2)
    pos_table_y = math.ceil((number_module[1]-1)/2)

    # Création du tuple "studied_area" qui est les coordonnées (x,y) du point bas-gauche de la zone AgriPV  étudiée :
    studied_table = list_table[pos_table_x][pos_table_y]

    # Depending of the tracking configuration, the studied area does not have the same definition
    if tracker == False:
        studied_area = (studied_table.coordinate[0] + (1/4)*(size_module[0]*resolution) , studied_table.coordinate[1])
    else:
        studied_area = (studied_table.coordinate[0] , studied_table.coordinate[1]+ (1/4)*(size_module[1]*resolution) )

    return studied_area

def plot_configuration(field_data, configuration, field, list_table, studied_area):
    ''' Plot of the configuration image with field, tables, and zone AgriPV
    Warning : for the AgriPV zone --> Orientation NORD-SUD = FIXE // orientation EST-OUEST = with TRACKER'''

    size_field = configuration[0]
    size_module = configuration[2]
    number_module = configuration[3] 
    nb_x = number_module[0]
    nb_y = number_module[1]
    gap_module = configuration[4]
    resolution = configuration[5] 
    xgap_module = gap_module[0]*resolution
    ygap_module = gap_module[1]*resolution
    azimut = configuration[6]
    tracker = configuration[10]

    # Creation of the canvas :
    fig = plt.figure(figsize=(5, 5)).add_subplot()
    fig.set_xlim([0,field_data.shape[0]])
    fig.set_ylim([0,field_data.shape[1]])
    fig.set(title='Display of the studied field')
    fig.set_axis_off()
    secxaxis = fig.secondary_xaxis('bottom',functions=(lambda x: 1/resolution * x, lambda x: 1/resolution * x))
    secxaxis.set_xlabel('X-size (m)')
    secyaxis = fig.secondary_yaxis('left',functions=(lambda x: 1/resolution * x, lambda x: 1/resolution * x))
    secyaxis.set_ylabel('Y-size (m)')

    # Adding field perimeter : 
    fig.add_patch(
        patches.Rectangle(
            field.coordinate,
            size_field[0]*resolution,
            size_field[1]*resolution,
            angle = azimut,
            rotation_point='center',
            edgecolor='black',
            fill=False,
            lw=2
        ) )

    # Adding tables : 
    for i in range(nb_x):
        for j in range(nb_y):
            fig.add_patch(
            patches.Rectangle(
                list_table[i][j].coordinate,
                size_module[0]*resolution,
                size_module[1]*resolution,
                angle = azimut,
                # Tables must rotate around the same point as the field, i.e: center of the field
                rotation_point=(field.coordinate[0]+(size_field[0]*resolution)/2, field.coordinate[1]+(size_field[1]*resolution)/2), 
                edgecolor='grey',
                facecolor = 'grey',
                fill=False,
                lw=1
            ) )

    # Plot of the studied area AgriPV :
    # Orientation NORD-SUD = FIXE // orientation EST-OUEST = with TRACKER
    if tracker == False:
        fig.add_patch(
            patches.Rectangle(
                studied_area,
                (1/2)*size_module[0]*resolution,
                ygap_module,
                angle = azimut,
                rotation_point=(field.coordinate[0]+(size_field[0]*resolution)/2, field.coordinate[1]+(size_field[1]*resolution)/2), #effectue la rotation autour du même point que le champs, i.e: le centre du champs
                fill=True,
                fc = 'red',
                lw=2        
            ) )
    else: 
        fig.add_patch(
            patches.Rectangle(
                studied_area,
                xgap_module,
                (1/2)*size_module[1]*resolution,
                angle = azimut,
                rotation_point=(field.coordinate[0]+(size_field[0]*resolution)/2, field.coordinate[1]+(size_field[1]*resolution)/2), #effectue la rotation autour du même point que le champs, i.e: le centre du champs
                fill=True,
                fc = 'red',
                lw=2        
            ) )
    return (fig)

def plot_heatmap_with_config(field_data, configuration, field, list_table, studied_area, scale_max, scale_min,title):
    
    '''Plot of the radiation image with the configuration of field, tables, and zone AgriPV
    Warning : for the AgriPV zone --> Orientation NORD-SUD = FIXE // orientation EST-OUEST = with TRACKER
    Warning : dataset 'field_data' is not in the same coordinate system as Patches thus the need to
    use 'plot_to_heatmap_coordinate' function and use the invert value of the azimut.  '''
    
    ysize_field = field_data.shape[1] 

    size_field = configuration[0]
    size_module = configuration[2]
    number_module = configuration[3] 
    nb_x = number_module[0]
    nb_y = number_module[1]
    gap_module = configuration[4]
    resolution = configuration[5] 
    xgap_module = gap_module[0]*resolution
    ygap_module = gap_module[1]*resolution
    azimut = configuration[6]
    tracker = configuration[10]

    # Creation of the canvas :
    heat_map = plt.figure(figsize=(6.5, 5)).add_subplot()
    heat_map = sns.heatmap(field_data,vmax=scale_max,vmin=scale_min, xticklabels=100, yticklabels = 100)
    heat_map.set(title=title)
    heat_map.set_axis_off()
    secxaxis = heat_map.secondary_xaxis('bottom',functions=(lambda x: 1/resolution * x, lambda x: 1/resolution * x))
    secxaxis.set_xlabel('X-size (m)')
    secyaxis = heat_map.secondary_yaxis('left',functions=(lambda x: (1/resolution * x), lambda x: 1/resolution * x))
    secyaxis.set_ylabel('Y-size (m)')

    # Plot field perimeter
    heat_map.add_patch(
        patches.Rectangle(
            plot_to_heatmap_coordinate(field.coordinate[0],field.coordinate[1],ysize_field),
            size_field[0]*resolution,
            -size_field[1]*resolution,
            angle = -azimut,
            rotation_point='center',
            edgecolor='red',
            fill=False,
            lw=2
        ) )

    # Plot tables :
    for i in range(nb_x):
        for j in range(nb_y):
            heat_map.add_patch(
            patches.Rectangle(            
                plot_to_heatmap_coordinate(list_table[i][j].coordinate[0],list_table[i][j].coordinate[1],ysize_field),
                size_module[0]*resolution,
                -size_module[1]*resolution,
                angle = -azimut,
                rotation_point=(field.coordinate[0]+(size_field[0]*resolution)/2, field.coordinate[1]+(size_field[1]*resolution)/2), #effectue la rotation autour du même point que le champs, i.e: le centre du champs
                edgecolor='black',
                fill=False,
                lw=1
            ) )

    # Plot of the studied area AgriPV :
    # Orientation NORD-SUD = FIXE // orientation EST-OUEST = with TRACKER
    if tracker == False:
        heat_map.add_patch(
            patches.Rectangle(
                plot_to_heatmap_coordinate(studied_area[0],studied_area[1],ysize_field),
                (1/2)*size_module[0]*resolution,
                -ygap_module,
                angle = -azimut,
                rotation_point=(field.coordinate[0]+(size_field[0]*resolution)/2, field.coordinate[1]+(size_field[1]*resolution)/2), #effectue la rotation autour du même point que le champs, i.e: le centre du champs
                fill=True,
                fc = 'red',
                lw=2        
            ) )
    else: 
        heat_map.add_patch(
            patches.Rectangle(
                plot_to_heatmap_coordinate(studied_area[0],studied_area[1],ysize_field),
                xgap_module,
                -(1/2)*size_module[1]*resolution,
                angle = -azimut,
                rotation_point=(field.coordinate[0]+(size_field[0]*resolution)/2, field.coordinate[1]+(size_field[1]*resolution)/2), #effectue la rotation autour du même point que le champs, i.e: le centre du champs
                fill=True,
                fc = 'red',
                lw=2        
            ) )
    return (heat_map)

def save_image(name,count):
    name_png = name+ str(count)
    plt.savefig(name_png)
    return name_png

def get_coordinate_of_new_area_AgriPV(lum_data_rotation, configuration, field, studied_area):
    '''Return coordinate of new_Area which is the AgriPV zone in for the rotated matrix.
    Alternatively, plot the 'new' heatmap after rotation for control purpose (desactivate in production) '''
    
    size_field = configuration[0]
    size_module = configuration[2]
    gap_module = configuration[4]
    resolution = configuration[5] 
    xgap_module = gap_module[0]*resolution
    ygap_module = gap_module[1]*resolution
    azimut = configuration[6]
    tracker = configuration[10]

    # Because coordinate system of array is different than plot coordinate system : 
    angle = -azimut
    ysize_field = lum_data_rotation.shape[1]


    # Vizualisation of the 'new' heatmap for control :
    plot = sns.heatmap(lum_data_rotation, xticklabels=100, yticklabels = 100)
    plot.set(title=('Display de l\'image retournée pour vérification'))
    plot.set_axis_off()
    secxaxis = plot.secondary_xaxis('bottom',functions=(lambda x: 1/resolution * x, lambda x: 1/resolution * x))
    secxaxis.set_xlabel('X-size (m)')
    secyaxis = plot.secondary_yaxis('left',functions=(lambda x: (1/resolution * x), lambda x: 1/resolution * x))
    secyaxis.set_ylabel('Y-size (m)')

    # Field perimeter vizualisation for control : 
    plot.add_patch(
        patches.Rectangle(
            plot_to_heatmap_coordinate(field.coordinate[0],field.coordinate[1],ysize_field),
            size_field[0]*resolution,
            -size_field[1]*resolution,
            angle = angle + azimut,
            rotation_point='center',
            edgecolor='black',
            fill=False,
            lw=2
        ) )

    # AgriPV zone vizualisation for control :  
    if tracker == False:
        zoneAgriPv = plot.add_patch(
            patches.Rectangle(
                plot_to_heatmap_coordinate(studied_area[0],studied_area[1],ysize_field),
                (1/2)*size_module[0]*resolution,
                -ygap_module,
                angle = angle + azimut,
                rotation_point=(field.coordinate[0]+(size_field[0]*resolution)/2, field.coordinate[1]+(size_field[1]*resolution)/2), #effectue la rotation autour du même point que le champs, i.e: le centre du champs
                fill=True,
                fc = 'red',
                lw=2        
            ) )
    else: 
        zoneAgriPv = plot.add_patch(
            patches.Rectangle(
                plot_to_heatmap_coordinate(studied_area[0],studied_area[1],ysize_field),
                xgap_module,
                -(1/2)*size_module[1]*resolution,
                angle = angle +azimut,
                rotation_point=(field.coordinate[0]+(size_field[0]*resolution)/2, field.coordinate[1]+(size_field[1]*resolution)/2), #effectue la rotation autour du même point que le champs, i.e: le centre du champs
                fill=True,
                fc = 'red',
                lw=2        
            ) )

    # Plot de la zone AgriPV avec les coordonnées qui vont permettre de récuperer les valeurs des zone AgriPV :
    if tracker == False:
        new_area = plot.add_patch(
            patches.Rectangle(
                (zoneAgriPv.get_bbox().x0,zoneAgriPv.get_bbox().y0),
                (1/2)*size_module[0]*resolution,
                -ygap_module,
                edgecolor='blue',
                fill=False,
                lw=2        
            ) )
    else: 
        new_area = plot.add_patch(
            patches.Rectangle(
                (zoneAgriPv.get_bbox().x0,zoneAgriPv.get_bbox().y0),
                xgap_module,
                -(1/2)*size_module[1]*resolution,
                edgecolor='blue',
                fill=False,
                lw=2        
            ) )
    return new_area

def calcul_lum_cumulee_for_each_zone(lum_data_rotation,new_area, tracker, size_module, resolution):
    ''' Calcul of the sum of the luminosity for each zone
    Warning : for the AgriPV zone --> Orientation NORD-SUD = FIXE // orientation EST-OUEST = with TRACKER '''

    if tracker == False:
        # zone AgriPV
        x = new_area.get_bbox().x0
        x1 = new_area.get_bbox().x1
        y = new_area.get_bbox().y1
        y1 = new_area.get_bbox().y0
        studied_lum_AgriPV = lum_data_rotation[int(y):int(y1),int(x):int(x1)]
        print(int(x),int(x1),int(y),int(y1))
        
        # zone sous panneau 
        x = new_area.get_bbox().x0
        x1 = new_area.get_bbox().x1
        y = new_area.get_bbox().y1
        y1 = y + size_module[1]*resolution
        studied_lum_Table = lum_data_rotation[int(y):int(y1),int(x):int(x1)]
        print(int(x),int(x1),int(y),int(y1))

        # zone inter rang
        x = new_area.get_bbox().x0 
        x1 = new_area.get_bbox().x1
        y = new_area.get_bbox().y1 + size_module[1]*resolution
        y1 = new_area.get_bbox().y0
        studied_lum_Rang = lum_data_rotation[int(y):int(y1),int(x):int(x1)]
        print(int(x),int(x1),int(y),int(y1))

    else:
        # zone AgriPV
        x = new_area.get_bbox().x0
        x1 = new_area.get_bbox().x1
        y = new_area.get_bbox().y1
        y1 = new_area.get_bbox().y0
        studied_lum_AgriPV = lum_data_rotation[int(y):int(y1),int(x):int(x1)]
        print(int(x),int(x1),int(y),int(y1))
        
        # zone sous panneau 
        x = new_area.get_bbox().x0
        x1 = x + size_module[0]*resolution
        y = new_area.get_bbox().y1
        y1 = new_area.get_bbox().y0
        studied_lum_Table = lum_data_rotation[int(y):int(y1),int(x):int(x1)]
        print(int(x),int(x1),int(y),int(y1))

        # zone inter rang
        x = new_area.get_bbox().x0 + size_module[0]*resolution
        x1 = new_area.get_bbox().x1
        y = new_area.get_bbox().y1
        y1 = new_area.get_bbox().y0
        studied_lum_Rang = lum_data_rotation[int(y):int(y1),int(x):int(x1)]
        print(int(x),int(x1),int(y),int(y1))


    # zone témoin
    zt = lum_data_rotation.max().max() 

    # Other zones
    zsp = np.array(studied_lum_Table).mean().mean()
    zir = np.array(studied_lum_Rang).mean().mean()
    zaPV = np.array(studied_lum_AgriPV).mean().mean()
    
    return zt, zsp, zir, zaPV

# Main function that will performed all analysis for one case, ie : one excel file : 
def data_analysis(count,filename):
    '''This function will analyze the content of the excel file named by argument 'excel_file_name' 
    and count will count the number of time this function is called by 'meta_analyse.py' to create
    unique image names.'''

    # Import of data file from Agrisoleo SaaS (.xlsx)
    input, field_data = read_excel(filename)

    # Extract configuration from excel file 'input'    
    configuration = extraction_of_configuration(input,field_data.shape[0],field_data.shape[1])
    size_field = configuration[0]
    offset_field = configuration[1]
    size_module = configuration[2]
    number_module = configuration[3] 
    gap_module = configuration[4]
    resolution = configuration[5] 
    azimut = configuration[6]
    start_date = configuration[7]
    end_date = configuration[8]
    nb_days = configuration[9]
    tracker = configuration[10]
    backtracking = configuration[11] 
    calibration = configuration[12]
    coordonne_site = configuration[13]
    hauteur = configuration[14]
    opacite = configuration[15]
    orientation_static = configuration[16]
    orientation_maximale = configuration[17]
    frequence = configuration[18]
    offset_SaaS = configuration[19]

    # Creation of the differents objects : field, tables, AgriPV zone : 
    field = create_field(offset_field[0],offset_field[1])
    list_table = create_table_list(number_module, gap_module, calibration, resolution) 
    studied_area = create_AgriPV_zone(number_module, list_table, size_module, resolution,tracker)

    # Creation and save of the image of the field configuration as .png : 
    plot_configuration(field_data, configuration, field, list_table, studied_area)
    name_png_config = save_image('img/configuration_',count)
    plt.close()

    # Creation and save of the image of the irradiation heat map irradiance units save as .png
    par = 1/2.1
    scale_max = 100000 ;scale_min = 25000
    scale_max_PAR = scale_max*par; scale_min_PAR = scale_min*par 
    scale_max_fraction = 25 ;scale_min_fraction = 100
    title = 'Partage lumineux cumulé (W/m2)'
    titlePAR = 'Partage lumineux cumulé PAR (W/m2)'
    titleFraction = 'Fraction partage lumineux cumulé (%)'
    
    field_data_PAR = field_data*par
    
    lum_max = field_data.max().max()
    field_data_ratio = field_data/lum_max*100
    
    plot_heatmap_with_config(field_data, configuration, field, list_table, studied_area, scale_max, scale_min,title)
    name_png_heatmap = save_image('img/heatmap_',count)
    plt.close()

    plot_heatmap_with_config(field_data_PAR, configuration, field, list_table, studied_area, scale_max_PAR, scale_min_PAR,titlePAR)
    name_png_heatmap_PAR = save_image('img/heatmapPAR_',count)
    plt.close()
    
    plot_heatmap_with_config(field_data_ratio, configuration, field, list_table, studied_area, scale_max_fraction, scale_min_fraction,titleFraction)
    name_png_heatmap_Fraction = save_image('img/heatmapFraction_',count)
    plt.close()

    # Rotation of the raw image in order to get the data associate with the AgriPV zone
    lum_data_array = np.array(field_data)
    lum_data_rotation = scipy.ndimage.rotate(lum_data_array,-azimut,reshape=False)
    
    # Get the coordinate of the AgriPV zone in for the rotated image
    new_area = get_coordinate_of_new_area_AgriPV(lum_data_rotation, configuration, field, studied_area)
    plt.close()

    # Use the new_area coordinate and the new matrix 'lum_data_rotation' to calcul the resultat for each zone :
    # --> inter_rang, sous_panneaux, agriPV
    zt, zsp, zir, zaPV = calcul_lum_cumulee_for_each_zone(lum_data_rotation,new_area, tracker, size_module, resolution)



    # Calculation of the results
    heterogeneity = (abs(zsp -zir)/(2*zaPV)*100).astype(int)
    ecart = gap_module[0]
    par = 1/2.1

    #l4 = [zt/nb_jours, zsp/nb_jours, zir/nb_jours,zaPV/nb_jours]

    print('L\'hétérogénéité est de' , heterogeneity ,'%.')
   
    return [coordonne_site[0], coordonne_site[1],
            start_date, end_date,
            size_field[0], size_field[1],
            azimut,
            size_module[0],size_module[1],
            gap_module[0], gap_module[1], 
            number_module[0],number_module[1],
            offset_SaaS[0], offset_SaaS[1],
            hauteur,
            opacite,
            tracker,
            orientation_static,
            orientation_maximale,
            backtracking,
            resolution,
            frequence,
            zt, zt/zt*100, zt*par, zt*par/nb_days,
            zsp, zsp/zt*100, zsp*par, zsp*par/nb_days,
            zir, zir/zt*100, zir*par, zir*par/nb_days, 
            zaPV, zaPV/zt*100, zaPV*par, zaPV*par/nb_days, 
            heterogeneity,
            name_png_config+'.png',
            name_png_heatmap+'.png',
            name_png_heatmap_PAR+'.png',
            name_png_heatmap_Fraction+'.png'
            ]

