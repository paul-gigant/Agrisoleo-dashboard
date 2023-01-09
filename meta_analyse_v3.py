# This program is the core of the dashboard analysis used by Agrisoleo.
# It is used to create overview for batch analysis for field radiation. 
# Last update : 23.12.2022 

# List of python librairies : 
import os
import shutil
from analyse_v8 import data_analysis
from pickle import *

# List .xlsx files in the working directory 
path = os.getcwd()
files = os.listdir(path)
files_xlsx = [f for f in files if f[-4:] == 'xlsx']

# Create /img directory to save all .png 
if os.path.exists('img') == True:
    # remove /img directory and its content
    shutil.rmtree('img')
    # create new /img directory 
    os.mkdir('img')
else:
    os.mkdir('img')

# Extract all important data :
meta_data = [data_analysis(i,j) for (i,j) in enumerate(files_xlsx)]
print('fin de la fonction extraction meta_data')

#sauvegarder meta_data pour test dash sans reload exel files
file_path = os.path.join(os.getcwd(), 'sauvegarde')

with open(file_path, 'wb') as f:
    dump (meta_data, f)