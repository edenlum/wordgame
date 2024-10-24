import random
import requests
from collections import Counter
import json

def is_valid_subword(word, base_word):
    return not (Counter(word) - Counter(base_word))

def is_common(word_info):
    return float(word_info.get('tags', ['f:0'])[0].split(":")[1]) > 2

def generate_word_data():
    datamuse_url = "https://api.datamuse.com/words"
    word_list = []

    for _ in range(3):
        params = {"sp": "??????", "max": 100000}  # Pattern for six-letter words
        response = requests.get(datamuse_url, params=params)

        if response.status_code == 200:
            six_letter_words = [word_info['word'] for word_info in response.json()]
            if not six_letter_words:
                print("No six-letter words found")
                continue
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
                            if (3 <= len(subword) <= len(chosen_word) and
                                    'defs' in word_info and
                                    is_common(word_info) and
                                    is_valid_subword(subword, chosen_word)):
                                subwords.append((subword, word_info['defs'][0]))

                        # Create the word data dictionary
                        word_data = {
                            "chosen_word": chosen_word,
                            "subwords": subwords
                        }

                        # Add the word data to the list
                        word_list.append(word_data)
                        print(f"Added word data for: {chosen_word}")
                    else:
                        print("Failed to fetch subwords from Datamuse API.")
                else:
                    print(f"Word: {chosen_word}\nDefinition not found.")
        else:
            print("Failed to fetch words from Datamuse API")

    # Write the full list to a JSON file
    with open('word_data.json', 'w') as json_file:
        json.dump(word_list, json_file, indent=4)

    print("word_data.json file with 1000 entries created successfully.")

if __name__ == "__main__":
    generate_word_data()
