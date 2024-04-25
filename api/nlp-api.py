# import libraries
from flask import Flask, request, jsonify
import nltk
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import json

# Download NLTK stopwords data
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

app = Flask(__name__)

# Get the list of English stopwords from NLTK
stop_words = set(stopwords.words('english'))

# get numeric part of a string e.g 5000 frm 5000mah, 10 frm 10MP, 8 frm 8gb
def get_numeral(text):
  # Extract numeric part using regular expression
  return re.search(r'\d+(\.\d+)?', text).group()

def remove_stopwords(tuple):
    input_tuple = tuple
    input_list = list(input_tuple)

    filtered_input = [] # after removing stop words
    for part in input_list:
        part = part.strip()
        # Tokenize the input string
        tokens = word_tokenize(part)

        # Remove stopwords from the tokenized list
        filtered_tokens = [word for word in tokens if word.lower() not in stop_words]

        # Reconstruct the string without stop words
        filtered_text = ' '.join(filtered_tokens)
        if filtered_text:
            filtered_input.append(filtered_text)

    return filtered_input
    # Print the string without stop words
    print(filtered_input)


def process_user_input(text):

    delimiters = ',| and '
    parts = re.split(delimiters, text)

    filtered_parts = filter(None, parts)
    flt = tuple(filtered_parts)
    flt = remove_stopwords(flt)
    return flt

# Define regular expressions for each group
storage_regex = re.compile(r"\b(storage|rom|internal memory)\b", re.IGNORECASE)
ram_regex = re.compile(r"\b(ram|main memory)\b", re.IGNORECASE)
display_regex = re.compile(r"\b(resolution|pixels|inch|inches|screen)\b", re.IGNORECASE)
camera_regex = re.compile(r"\b(camera|rear camera|mp)\b", re.IGNORECASE)
battery_regex = re.compile(r"\b(battery|mah)\b", re.IGNORECASE)
price_regex = re.compile(r"\b(ksh|kshs|sh|shs|budget|costs|bob)\b", re.IGNORECASE)

specs_regex = {
    storage_regex: 'internal_memory',
    ram_regex: 'ram_capacity',
    display_regex: 'screen_size',
    camera_regex: 'primary_camera_rear',
    battery_regex: 'battery_capacity',
    price_regex: 'price'
}

# DATASET columns
# ['brand_name', 'model', 'price', 'avg_rating', '5G_or_not', 'processor_brand', 'num_cores', 'processor_speed', 'battery_capacity', 'fast_charging_available', 'fast_charging', 'ram_capacity','internal_memory', 'screen_size', 'refresh_rate', 'num_rear_cameras','os', 'primary_camera_rear', 'primary_camera_front','extended_memory_available', 'resolution_height', 'resolution_width']


# Define a function to match words to their groups using regular expressions
def match_word_to_group(word):
  for feature_regex, feature_grp in specs_regex.items():
    if feature_regex.search(word):
      return feature_grp
  return None  # Return None if word doesn't belong to any group

# Example usage:
# word = '5000mah battery'
# group = match_word_to_group(word)
# print(f"The word '{word}' belongs to the group '{group}'")

def get_preferences_object(input_string):
    processed_input = process_user_input(input_string)

    prefs_obj = {"prefs": {}} # to carry input for pearson correlation
    non_num_prefs = {"text": ''}
#    print(processed_input)
   
    for txt in processed_input:
        group = match_word_to_group(txt)
        
        if group:
            #
            prefs_obj['prefs'][group] = txt
            print(f"The word '{txt}' belongs to the group '{group}'")
            # filtered_input.remove(input)
        elif group == None:
            non_num_prefs['text'] = str(non_num_prefs['text'])+str(str(txt)+str(','))

    
        
    for spec, text in prefs_obj['prefs'].items():
        # Tokenize the input text
        tokens = word_tokenize(text)

        # Perform part-of-speech tagging
        tagged_tokens = nltk.pos_tag(tokens)
        for val, pos in tagged_tokens:
            if pos == 'CD':
                prefs_obj['prefs'][spec] = get_numeral(val)# update prefs obj:

    prefs_obj['text'] = non_num_prefs['text']
    prefs_obj['raw_input'] = ' '.join(processed_input)
    return prefs_obj

@app.route('/parse_preferences', methods=['POST'])
def parse_preferences():
    # print('parsing')
    data = request.json
    # print('data')
    # print(data)
    input_string = data['input']
    return jsonify(get_preferences_object(input_string))


if __name__ == '__main__':
    # Change the port number as needed
    app.run(port=5002, debug=True)