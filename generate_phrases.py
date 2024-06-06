import openai
import random
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import os

api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print("La clé API a été récupérée avec succès.")
else:
    print("Impossible de trouver la clé API.")
    

# Configuration pour OpenAI GPT-3.5
openai.api_key = api_key

# Chargement de GPT-2 (gratuit)
model_name = 'gpt2'
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)

# Fonction pour générer des phrases avec GPT-2
def generate_gpt2_phrase(prompt):
    input_ids = tokenizer.encode(prompt, return_tensors='pt')
    outputs = model.generate(input_ids, max_length=50, num_return_sequences=1)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Fonction pour générer des phrases avec GPT-3.5
def generate_gpt35_phrase(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=50
    )
    return response.choices[0].text.strip()

# Fonction pour valider les réponses avec GPT-3.5
def validate_response(response):
    prompt = f"Évalue la pertinence et la qualité de cette réponse : {response}"
    evaluation = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=50
    )
    return "pertinente" in evaluation.choices[0].text.lower()

# Fonction pour générer des phrases aléatoires avec une approche hybride
def generate_random_phrase():
    if random.randint(1, 50) == 1:
        # Utiliser GPT-3.5 pour une phrase normale
        return generate_gpt35_phrase("Génère une phrase intéressante :")
    else:
        # Utiliser GPT-2 pour phrases non filtrées
        if random.randint(1, 50) == 1:
            return generate_gpt2_phrase("Génère une phrase offensante ou sexuelle :")
        else:
            gpt2_response = generate_gpt2_phrase("Génère une phrase intéressante :")
            if validate_response(gpt2_response):
                return gpt2_response
            else:
                return generate_gpt35_phrase("Génère une phrase intéressante :")

# Fonction d'apprentissage
def train_model():
    unknown_phrases_file = "path/to/unknown_phrases.txt"
    nlu_file = "path/to/nlu.yml"

    with open(unknown_phrases_file, "a") as f:
        for _ in range(100):  # Générer 100 nouvelles phrases
            f.write(generate_random_phrase() + "\n")
    
    print("Nouvelles phrases ajoutées à unknown_phrases.txt")

    # Continuer avec le reste du processus de formation Rasa...

if __name__ == "__main__":
    train_model()