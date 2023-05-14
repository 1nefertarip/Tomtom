import re
import pandas as pd
import os

def merge_total_available (filename,df2):
    df = pd.read_csv(filename)

    total_cols = [col for col in df.columns if col.startswith('Total_')]
    df_total = df[['Total_occupied'] + ['chargingAvailability']]

    time = re.search(r'\d{4}-\d{2}-\d{2}_\d{2}:\d{2}', filename).group()
    df_total = df_total.rename(columns={'Total_occupied': f'{time}'})

    joined_df = pd.merge(df2, df_total, on='chargingAvailability')
    return joined_df

df = pd.read_csv('CP_Tomtom_NL.csv')
df = df[['name', 'lat','lon','chargingAvailability']]

# Get a list of all CSV files in the current directory that begin with "CP_Availability"

csv_files = [f for f in os.listdir('.') if f.startswith('CP_Availability') and f.endswith('.csv')]
for filename in csv_files:
    df = merge_total_available(filename,df)

# Make a long table
col_remove = ['name','lat','lon','chargingAvailability']
col_list = [col for col in df.columns if col not in col_remove]
df2 = pd.melt(df, id_vars='chargingAvailability', value_vars=col_list, var_name='variable', value_name='value')

df_base = pd.read_csv('CP_Tomtom_NL.csv')
df_base = df_base[['name', 'lat','lon','chargingAvailability']]

df2 = pd.merge(df2, df_base, on='chargingAvailability')
df2['variable']= pd.to_datetime(df2['variable'], format='%Y-%m-%d_%H:%M')

df.to_csv('output.csv')
df2.to_csv('output_long.csv')