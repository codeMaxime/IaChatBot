import os
import random
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import yaml
import subprocess

# Configuration des variables
gpt2_model_name = "gpt2"
unknown_phrases_file = "unknown_phrases.txt"
nlu_file = "data/nlu.yml"
stories_file = "data/stories.yml"
domain_file = "domain.yml"
model_output_dir = "models/"
sexually_or_offensive_trigger = 20  # Une phrase sexuelle ou offensante sur 20
phrases_to_learn = 50  # Nombre de phrases à apprendre
examples_per_intent = 2  # Nombre minimum d'exemples par intent

# Charger le modèle et le tokenizer GPT-2
tokenizer = GPT2Tokenizer.from_pretrained(gpt2_model_name)
model = GPT2LMHeadModel.from_pretrained(gpt2_model_name)

# Générer une phrase à partir de GPT-2
def generate_gpt2_phrase(prompt, max_length=50):
    inputs = tokenizer.encode(prompt, return_tensors="pt")
    outputs = model.generate(inputs, max_length=max_length, num_return_sequences=1)
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return text

# Vérifier la cohérence de la phrase
def check_phrase_coherence(phrase):
    inputs = tokenizer.encode(phrase, return_tensors="pt")
    outputs = model.generate(inputs, max_length=50, num_return_sequences=1)
    generated_phrase = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return generated_phrase != phrase

# Charger les phrases inconnues
with open(unknown_phrases_file, "r", encoding="utf-8") as file:
    unknown_phrases = [line.strip() for line in file if line.strip()]

# Générer de nouvelles phrases
new_phrases = []
for i, phrase in enumerate(unknown_phrases):
    if i >= phrases_to_learn:
        break

    examples = []
    for _ in range(examples_per_intent):
        if (i + 1) % sexually_or_offensive_trigger == 0:
            prompt = "Génère une phrase sexuelle ou offensante :"
        else:
            prompt = phrase

        new_phrase = generate_gpt2_phrase(prompt)
        
        while not check_phrase_coherence(new_phrase):
            new_phrase = generate_gpt2_phrase(prompt)
        
        examples.append(new_phrase)

    new_phrases.append({"intent": f"new_intent_{i}", "examples": examples, "response": generate_gpt2_phrase(f"Réponds à: {phrase}")})

# Charger et mettre à jour le fichier domain
with open(domain_file, "r", encoding="utf-8") as file:
    domain_content = yaml.safe_load(file)

if "intents" not in domain_content:
    domain_content["intents"] = []

if "responses" not in domain_content:
    domain_content["responses"] = {}

for new_phrase in new_phrases:
    if new_phrase["intent"] not in domain_content["intents"]:
        domain_content["intents"].append(new_phrase["intent"])
    domain_content["responses"][f"utter_{new_phrase['intent']}"] = [{"text": new_phrase["response"]}]

# Sauvegarder le fichier domain mis à jour avec version 3.1
domain_content["version"] = "3.1"
with open(domain_file, "w", encoding="utf-8") as file:
    yaml.safe_dump(domain_content, file, allow_unicode=True, default_flow_style=False)

# Charger et mettre à jour le fichier stories
with open(stories_file, "r", encoding="utf-8") as file:
    stories_content = yaml.safe_load(file)

if "stories" not in stories_content:
    stories_content["stories"] = []

for new_phrase in new_phrases:
    story = {
        "story": f"Story for {new_phrase['intent']}",
        "steps": [
            {"intent": new_phrase['intent']},
            {"action": "utter_" + new_phrase['intent']}
        ]
    }
    stories_content["stories"].append(story)

# Sauvegarder le fichier stories mis à jour avec version 3.1
stories_content["version"] = "3.1"
with open(stories_file, "w", encoding="utf-8") as file:
    yaml.safe_dump(stories_content, file, allow_unicode=True, default_flow_style=False)

# Charger et mettre à jour le fichier nlu
with open(nlu_file, "r", encoding="utf-8") as file:
    nlu_content = yaml.safe_load(file)

if "nlu" not in nlu_content:
    nlu_content["nlu"] = []

for new_phrase in new_phrases:
    examples = "\n".join([f"- {example}" for example in new_phrase["examples"]])
    nlu_content["nlu"].append({
        "intent": new_phrase["intent"],
        "examples": examples
    })

# Sauvegarder le fichier nlu mis à jour avec version 3.1
nlu_content["version"] = "3.1"
with open(nlu_file, "w", encoding="utf-8") as file:
    yaml.safe_dump(nlu_content, file, allow_unicode=True, default_flow_style=False)

# Entraîner le modèle Rasa
subprocess.run(["rasa", "train"], check=True)

# Nettoyer le fichier des phrases inconnues
with open(unknown_phrases_file, "w", encoding="utf-8") as file:
    file.write("")

print("Script d'apprentissage exécuté avec succès.")
