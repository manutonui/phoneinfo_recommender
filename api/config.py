# config.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler as Scaler

# Define your constants here
ENVIRONMENT = 'dev'
# API_KEY = 'your_api_key'
# MAX_RESULTS = 10
DATASET = 'C:/Users/tkton/OneDrive/Desktop/C.S/PROJECT/CODE/datasets/smartphones.csv'

# textual columns include booleans
TEXTUAL_COLUMNS = ['brand_name','5G_or_not','model', 'internal_memory', 'ram_capacity', 'processor_brand','fast_charging_available','extended_memory_available','os']

NUMERICAL_COLUMNS = ['price', 'avg_rating', 'battery_capacity', 'internal_memory', 'ram_capacity', 'screen_size', 'primary_camera_rear', 'primary_camera_front', 'resolution_height', 'resolution_width', 'num_rear_cameras', 'num_cores', 'processor_speed']

avg_ranges = {
    'price': 10000,
    'avg_rating': 1,
    'battery_capacity': 1000,
    'screen_size': 1,
    'primary_camera_rear': 10,
    'primary_camera_front': 5,
    'resolution_height': 200,
    'resolution_width': 150,
}

# Static Helper Functions
def textual_phone_description (row):
    desc = ''
    desc+=str(row['os'])+' '
    desc+=str(row['model'])+' '
    if row['5G_or_not'] == True:
        desc+='5G '
    if row['fast_charging_available'] == True:
        desc+='fast charging '
    if row['extended_memory_available'] == True:
        desc+='external memory '
    desc+=str(row['ram_capacity'])+'gb RAM '
    desc+=str(row['internal_memory'])+'gb internal memory '
    desc = desc.replace(',', ' ')
    return desc.strip()

def scale_data(df):
    scaler = Scaler()
    return pd.DataFrame(scaler.fit_transform(df), columns=df.columns, index=df.index)


def calculate_correlation(data, input_row):
    correlations = data.apply(lambda row: np.corrcoef(input_row, row)[0, 1], axis=1)
    return correlations



