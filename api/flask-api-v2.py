from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
# Import constants from config.py
from config import DATASET, TEXTUAL_COLUMNS, NUMERICAL_COLUMNS, textual_phone_description, scale_data, calculate_correlation, avg_ranges

from sklearn.feature_extraction.text import CountVectorizer as Vectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

smartphones = pd.read_csv(DATASET)
textual_df = smartphones[TEXTUAL_COLUMNS].dropna(axis=0)
numerical_df = smartphones[NUMERICAL_COLUMNS].dropna(axis=0)
textual_df['description'] = textual_df.apply(textual_phone_description, axis=1)

vectorizer = Vectorizer(stop_words="english", analyzer='word')

all_brands_list = []
platforms = ['ios', 'android']
brands = list(smartphones['brand_name'].unique())
all_brands_list.extend(platforms)
all_brands_list.extend(brands)

def filter_for_Cosine (input_string):
    listed = textual_df
    filter_words = [word for word in all_brands_list if word in input_string]
    print(filter_words)
    
    for word in filter_words:
        if word in platforms:
            listed = textual_df[textual_df['os'] == word]
        else: # just brand
            listed = textual_df[textual_df['brand_name'] == word]

    return listed
def rank_Cosine_Sim_recommendations(input_string):
    listed = filter_for_Cosine(input_string)
    vector = vectorizer.fit_transform(listed['description'])

    # Transform input string into TF-IDF vector
    input_vector = vectorizer.transform([input_string])

    # Calculate cosine similarity with other documents
    similarities = cosine_similarity(input_vector, vector)

    # Create DataFrame to display results
    result_df = pd.DataFrame({
        'Model': listed['model'],
        'Document': listed['description'],
        'Cosine Similarity': similarities[0]
    }).sort_values(by='Cosine Similarity', ascending=False)
    # return result_df.head(10)
    # Merge DataFrames along their indexes with inner join
    merged_df = pd.merge(smartphones, result_df.head(4), left_index=True, right_index=True, how='inner')
    # Select only columns from the first DataFrame
    merged_df = merged_df[smartphones.columns]
    return merged_df
def rank_Correlation_recommendations(specified_columns):
    df = numerical_df
    # select desired columns in df and compare pearson
    cols_to_compare = list(specified_columns)
    df = df[cols_to_compare]
    target = pd.DataFrame([specified_columns], columns=cols_to_compare)
    input_row = target.iloc[0]

    # scale
    scaled_df = scale_data(df)

    # Calculate correlation coefficients
    correlations = calculate_correlation(scaled_df, input_row)
    smartphones['correlation'] = correlations
    smartphones.sort_values(by='correlation', ascending=False)
    
    flt_df = df

    if 'price' in specified_columns:
        flt_df = flt_df[(flt_df['price'] >= (specified_columns['price']-avg_ranges['price'])) & (flt_df['price'] <= (specified_columns['price']+avg_ranges['price']))]
    if 'battery_capacity' in specified_columns:
        flt_df = flt_df[(flt_df['battery_capacity'] >= (specified_columns['battery_capacity']-avg_ranges['battery_capacity'])) & (flt_df['battery_capacity'] <= (specified_columns['battery_capacity']+avg_ranges['battery_capacity']))]
        
    

    for key, value in specified_columns.items():
        if key in avg_ranges:
            # print('Ranges: '+str(key))
            fltrd_df = flt_df[(flt_df[key] >= (value-avg_ranges[key])) & (df[key] <= (value+avg_ranges[key]))]
            flt_df = pd.concat([flt_df, fltrd_df])
            flt_df = flt_df.drop_duplicates()

    for key, value in specified_columns.items():
        if key not in avg_ranges:
            # print('Exacts: '+str(key))
            flt_df = flt_df[flt_df[key] == value]

    # only retain indices then merge
    flt_df = flt_df.index.to_frame(name='index')
    
    # Merge DataFrames along their indexes with inner join
    merged_df = pd.merge(smartphones, flt_df, left_index=True, right_index=True, how='inner')
    merged_df = merged_df[smartphones.columns]
    res = merged_df.sort_values(by="correlation", ascending=False)
    return res.head(2)

@app.route('/get_cosine_recommendations', methods=['POST'])
def get_cosine_recommendations():
    data = request.json
    user_input = data['input']
    topN = rank_Cosine_Sim_recommendations(user_input).to_json(orient='records')
    return jsonify(topN)

@app.route('/get_pearson_recommendations', methods=['POST'])
def get_pearson_recommendations():
    data = request.json
    prefs = data['prefs']
    topK = []
    if bool(prefs):
        topK = rank_Correlation_recommendations(prefs).to_json(orient='records')
    return jsonify(topK)

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    req_data = request.json
    user_input = req_data['text']
    if user_input == '':
        user_input = req_data['raw_input']
    prefs = req_data['prefs']

    topK = pd.DataFrame()

    if bool(prefs):
        # Convert values to integers
        for key in prefs:
            prefs[key] = int(prefs[key])
        topK = rank_Correlation_recommendations(prefs).to_json(orient='records')
        
    topN = rank_Cosine_Sim_recommendations(user_input)
    topT = pd.concat([topN, topK]).to_json(orient='records')
    return jsonify(topT)


if __name__ == '__main__':
    # Change the port number as needed
    app.run(port=5001, debug=True)