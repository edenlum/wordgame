from flask import Flask, jsonify
from flask_cors import CORS
import random
import itertools
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


from collections import Counter

def is_valid_subword(word, base_word):
    return (not (Counter(word) - Counter(base_word)))

def is_common(word_info):
    return float(word_info.get('tags', ['f:0'])[0].split(":")[1]) > 2

@app.route('/get_word_data', methods=['GET'])
def get_word_data():
    # Replace the following block with your existing code to generate chosen_word and subwords
    datamuse_url = "https://api.datamuse.com/words"
    params = {"sp": "??????"}  # Pattern for six-letter words
    response = requests.get(datamuse_url, params=params)

    if response.status_code == 200:
        six_letter_words = [word_info['word'] for word_info in response.json()]
        if not six_letter_words:
            return jsonify({"error": "No six-letter words found"}), 400
        else:
            # Step 2: Randomly choose one word from the list
            chosen_word = random.choice(six_letter_words)

            # Step 3: Get the definition from DictionaryAPI
            dictionary_api_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{chosen_word}"
            definition_response = requests.get(dictionary_api_url)

            if definition_response.status_code == 200:
                definition_data = definition_response.json()
                definition = definition_data[0]["meanings"][0]["definitions"][0]["definition"]
                print(f"Word: {chosen_word}\nDefinition: {definition}")

                # Step 4: Find subwords using Datamuse API to search for valid real words only
                subword_params = {
                    "sp": f"*+{chosen_word}",  # Pattern to find words made up of letters from chosen_word
                    "max": 10000000,
                    "md": "df",  # Include definitions to filter valid words
                }
                subword_response = requests.get(datamuse_url, params=subword_params)

                if subword_response.status_code == 200:
                    subwords = []
                    for word_info in subword_response.json():
                        subword = word_info['word']
                        if 3 <= len(subword) <= len(chosen_word) and \
                            'defs' in word_info and \
                            is_common(word_info) and \
                            is_valid_subword(subword, chosen_word):
                            print(word_info)
                            subwords.append((subword, word_info['defs'][0]))

                else:
                    print("Failed to fetch subwords from Datamuse API.")
            else:
                print(f"Word: {chosen_word}\nDefinition not found.")

            print([w for w,_ in subwords])
            return jsonify({"chosen_word": chosen_word, "subwords": subwords})
    else:
        return jsonify({"error": "Failed to fetch words from Datamuse API"}), 500


if __name__ == '__main__':
    app.run(debug=True)
