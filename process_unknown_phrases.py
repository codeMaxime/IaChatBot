import os
import yaml
import random

def load_unknown_phrases(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    phrases = [line.strip() for line in lines]
    return phrases

def update_nlu_file(nlu_file, phrases):
    with open(nlu_file, 'r', encoding='utf-8') as file:
        nlu_data = yaml.safe_load(file)

    for phrase in phrases:
        intent = "new_intent_" + str(random.randint(1, 100000))
        new_example = {'intent': intent, 'examples': f"- {phrase}"}
        nlu_data['nlu'].append(new_example)

    with open(nlu_file, 'w', encoding='utf-8') as file:
        yaml.dump(nlu_data, file, allow_unicode=True)

def train_rasa_model():
    os.system('rasa train')

if __name__ == "__main__":
    unknown_phrases_file = 'unknown_phrases.txt'
    nlu_file = 'data/nlu.yml'

    phrases = load_unknown_phrases(unknown_phrases_file)
    if phrases:
        update_nlu_file(nlu_file, phrases)
        train_rasa_model()

        # Clear the unknown phrases file after processing
        open(unknown_phrases_file, 'w').close()

        print("Training completed successfully!")
    else:
        print("No new phrases to process.")
