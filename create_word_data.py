import random
import requests
from collections import Counter
import json

def is_common(word_info):
    return float(word_info.get('tags', ['f:0'])[0].split(":")[1]) > 2

def has_definition(word_info):
    return 'defs' in word_info and word_info['defs']

def good_word(word_info):
    return is_common(word_info) and \
        has_definition(word_info) and \
        ' ' not in word_info['word']

def generate_word_data(N=1000):
    datamuse_url = "https://api.datamuse.com/words"
    word_list = []

    params = {"sp": "??????", "max": 100000, "md": "df"}  # Pattern for six-letter words
    response = requests.get(datamuse_url, params=params)

    if response.status_code != 200:
        print("Failed to fetch words from Datamuse API")
        return

    word_infos = filter(good_word, random.sample(response.json(), k=N))

    if not word_infos:
        print("No six-letter words found")
        return

    for main_word_info in word_infos:
        main_word = main_word_info['word']
        # Step 4: Find subwords using Datamuse API to search for valid real words only
        subword_params = {
            "sp": f"*+{main_word}",  # Pattern to find words made up of letters from chosen_word
            "max": 100000,
            "md": "df",  # Include definitions to filter valid words
        }
        subword_response = requests.get(datamuse_url, params=subword_params)

        if subword_response.status_code != 200:
            print("Failed to fetch words from Datamuse API")
            continue

        def valid_subword(word_info):
            word = word_info['word']
            return 3 <= len(word) <= len(main_word) and \
                not (Counter(word) - Counter(main_word)) and \
                good_word(word_info)

        subwords = filter(valid_subword, subword_response.json())
        subwords = [(info["word"], info["defs"][0]) for info in subwords]

        # Create the word data dictionary
        word_data = {
            "chosen_word": main_word,
            "subwords": subwords
        }

        # Add the word data to the list
        word_list.append(word_data)
        print(f"Added word data for: {main_word}: {subwords}")

    # Write the full list to a JSON file
    with open('word_data.json', 'w') as json_file:
        json.dump(word_list, json_file, indent=4)

    print("word_data.json file with 1000 entries created successfully.")

if __name__ == "__main__":
    generate_word_data()
