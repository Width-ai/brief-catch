import pandas as pd


df = pd.read_csv('data/sentence_ranking_clean_input_data.csv')
df_no_duplicates = df[~df['sentence #'].duplicated(keep=False)]

def retrieve_text(sentence_num, file_path):
    with open(file_path) as f:
        for line in reversed(f.readlines()):
            if str(sentence_num) in line:
                return line.split('.', 1)[1].strip()



df_no_duplicates['ranking'] = df_no_duplicates['sentence #'].apply(lambda x: retrieve_text(x, 'data/output.txt'))