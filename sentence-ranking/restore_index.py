import pandas as pd

df = pd.read_csv('data/rerun_output_data.csv')
df.set_index('Unnamed: 0').sort_index().to_csv('data/restored_index.csv')