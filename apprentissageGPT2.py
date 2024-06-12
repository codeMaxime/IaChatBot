import os
import random
import threading
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import yaml
import subprocess

# Demander à l'utilisateur le nombre de phrases que l'IA doit apprendre
phrases_to_learn = int(input("Entrez le nombre de phrases que l'IA doit apprendre: "))

# Configuration des variables
gpt2_model_name = "gpt2"
unknown_phrases_file = "unknown_phrases.txt"
nlu_file = "data/nlu.yml"
stories_file = "data/stories.yml"
domain_file = "domain.yml"
model_output_dir = "models/"
sexually_trigger_ratio = 10  # Une phrase sexuelle sur 10
offensive_trigger_ratio = 10  # Une phrase offensante sur 10
examples_per_intent = 2  # Nombre minimum d'exemples par intent

# Déterminer le nombre de threads en fonction des cœurs CPU disponibles
num_threads = os.cpu_count()

# Charger le modèle et le tokenizer GPT-2, utiliser le GPU si disponible
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = GPT2Tokenizer.from_pretrained(gpt2_model_name)
model = GPT2LMHeadModel.from_pretrained(gpt2_model_name).to(device)

# Générer une phrase à partir de GPT-2
def generate_gpt2_phrase(prompt, max_length=50):
    inputs = tokenizer.encode(prompt, return_tensors="pt").to(device)
    outputs = model.generate(inputs, max_length=max_length, num_return_sequences=1, do_sample=True, top_k=50, top_p=0.95)
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return text

# Vérifier la cohérence de la phrase
def check_phrase_coherence(phrase):
    inputs = tokenizer.encode(phrase, return_tensors="pt").to(device)
    outputs = model.generate(inputs, max_length=50, num_return_sequences=1, do_sample=True, top_k=50, top_p=0.95)
    generated_phrase = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return generated_phrase != phrase

# Charger les phrases inconnues
with open(unknown_phrases_file, "r", encoding="utf-8") as file:
    unknown_phrases = [line.strip() for line in file if line.strip()]

# Générer de nouvelles phrases
new_phrases = []

def generate_phrases(start, end):
    for i in range(start, end):
        if i >= len(unknown_phrases):
            break
        phrase = unknown_phrases[i]

        examples = []
        for _ in range(examples_per_intent):
            if (i + 1) % sexually_trigger_ratio == 0:
                prompt = "Génère une phrase sexuelle :"
            elif (i + 1) % offensive_trigger_ratio == 0:
                prompt = "Génère une phrase offensante :"
            else:
                prompt = phrase

            new_phrase = generate_gpt2_phrase(prompt)
            
            while not check_phrase_coherence(new_phrase):
                new_phrase = generate_gpt2_phrase(prompt)
            
            examples.append(new_phrase)

            # Afficher la phrase générée pour vérification
            print(f"Prompt: {prompt}\nGenerated: {new_phrase}\n")
        
        intent_name = f"intent_{i+1}"
        new_phrases.append({
            "intent": intent_name,
            "examples": examples,
            "response": examples[0]  # Choisir le premier exemple comme réponse pour simplifier
        })

# Diviser le travail en threads pour accélérer la génération de phrases
thread_list = []
chunk_size = len(unknown_phrases) // num_threads

for i in range(num_threads):
    start = i * chunk_size
    end = start + chunk_size if i < num_threads - 1 else len(unknown_phrases)
    thread = threading.Thread(target=generate_phrases, args=(start, end))
    thread_list.append(thread)
    thread.start()

for thread in thread_list:
    thread.join()

# Charger les fichiers YAML en mémoire une seule fois
with open(domain_file, "r", encoding="utf-8") as file:
    domain_content = yaml.safe_load(file)

with open(stories_file, "r", encoding="utf-8") as file:
    stories_content = yaml.safe_load(file)

with open(nlu_file, "r", encoding="utf-8") as file:
    nlu_content = yaml.safe_load(file)

# Mise à jour des fichiers en mémoire
if "intents" not in domain_content:
    domain_content["intents"] = []
if "responses" not in domain_content:
    domain_content["responses"] = {}

if "stories" not in stories_content:
    stories_content["stories"] = []

if "nlu" not in nlu_content:
    nlu_content["nlu"] = []

for new_phrase in new_phrases:
    domain_content["intents"].append(new_phrase["intent"])
    domain_content["responses"][f"utter_{new_phrase['intent']}"] = [{"text": new_phrase["response"]}]
    
    story = {
        "story": f"Story for {new_phrase['intent']}",
        "steps": [
            {"intent": new_phrase['intent']},
            {"action": "utter_" + new_phrase['intent']}
        ]
    }
    stories_content["stories"].append(story)

    examples = "\n".join([f"- {example}" for example in new_phrase["examples"]])
    nlu_content["nlu"].append({
        "intent": new_phrase["intent"],
        "examples": examples
    })

# Sauvegarder les fichiers mis à jour
with open(domain_file, "w", encoding="utf-8") as file:
    yaml.safe_dump(domain_content, file, allow_unicode=True, default_flow_style=False)

with open(stories_file, "w", encoding="utf-8") as file:
    yaml.safe_dump(stories_content, file, allow_unicode=True, default_flow_style=False)

with open(nlu_file, "w", encoding="utf-8") as file:
    yaml.safe_dump(nlu_content, file, allow_unicode=True, default_flow_style=False)

# Entraîner le modèle Rasa
subprocess.run(["rasa", "train"], check=True)

# Nettoyer le fichier des phrases inconnues
with open(unknown_phrases_file, "w", encoding="utf-8") as file:
    file.write("")

print("Script d'apprentissage exécuté avec succès.")