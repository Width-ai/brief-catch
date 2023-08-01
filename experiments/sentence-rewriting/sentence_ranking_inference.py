import json
import requests
import pandas as pd

# read in data
df = pd.read_csv('./data/cleaned_data.csv', index_col=0)

output_data = []
# iterate through and call topic sentence endpoint with all input data
for index, row in df.iterrows():
    input_text = row['input']
    response = requests.post('http://localhost:8001/topic-sentence', data=json.dumps({'input_text': input_text}))
    response_json = response.json()

    # put result in output list
    output_data.append({
        'input_text': input_text, 
        'revised_topic_sentence': response_json.get('revised_topic_sentence'), 
        'analysis': response_json.get('analysis')
    })

# Write results to a csv file
output_df = pd.DataFrame(output_data)
output_df.to_csv('./data/sentence_ranking_output_v2.csv', index=False)