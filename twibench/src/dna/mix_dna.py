import pandas as pd
import os
import sys

# Récupération du fichier de configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

def dna_dictionnary(path):
    # Créer un dictionnaire associant un numéro d'id commençant à 0 à un nom de fichier
    dna_dictionnary = {}
    for i, file in enumerate(os.listdir(path)):
        dna_dictionnary[i] = file
    return dna_dictionnary

def name_output_file():
    print("Entrez le nom du fichier de sortie : ", end="")
    user_input = input()
    while not user_input.isalnum() and "-" not in user_input and "_" not in user_input:
        print("ERREUR: Le nom du fichier de sortie ne doit contenir que des lettres, des chiffres, des tirets ou des underscores.")
        print("Entrez le nom du fichier de sortie : ", end="")
        user_input = input()
    return user_input

def pick_remaining_dataset(dna_dict):
    print("--- DATASETS RESTANT ---")
    for i, file_name in dna_dict.items():
        print(f"[{i}] - {file_name}")
    print(" ")
    print("Entrez le numéro du fichier à ajouter au mélange : ", end="")
    user_input = int(input())
    while user_input not in dna_dict:
        print("ERREUR: Le numéro entré n'est pas valide.")
        print("Entrez le numéro du fichier à ajouter au mélange : ", end="")
        user_input = int(input())
    return user_input

def pick_sample_size(max_size):
    print(f"Entrez la taille de l'échantillon (entre 1 et {max_size}) : ", end="")
    user_input = int(input())
    while user_input < 1 or user_input > max_size:
        print(f"ERREUR: La taille de l'échantillon doit être supérieure à 0 et inférieure à {max_size}.")
        print(f"Entrez la taille de l'échantillon (entre 1 et {max_size}) : ", end="")
        user_input = int(input())
    return user_input

def exit_choice():
    print("Voulez-vous ajouter un autre fichier au mélange ? (o/n) ", end="")
    user_input = input().lower()
    while user_input not in ["o", "n"]:
        print("ERREUR: La réponse entrée n'est pas valide.")
        print("Voulez-vous ajouter un autre fichier au mélange ? (o/n) ", end="")
        user_input = input().lower()
    if user_input == "n":
        return True
    return False

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_statistics(output_dataframe):
    print("--- STATISTIQUES ---")
    print("Taille du fichier final :", len(output_dataframe), "lignes")
    nb_bots = output_dataframe[output_dataframe["label"] == "BOT"].shape[0]
    nb_humans = output_dataframe[output_dataframe["label"] == "HUMAN"].shape[0]
    print("Nombre de bots :", nb_bots)
    print("Nombre d'humains :", nb_humans)

if __name__ == '__main__':
    dna_path = os.path.join(Config().getFormattedDatasetsPath(), "dna")
    dna_dictionnary = dna_dictionnary(dna_path)

    exit_app = False

    # Le dataframe final contient deux colonnes : user_id et DNA
    output_dataframe = pd.DataFrame(columns=["user_id", "DNA", "label"])

    while not exit_app:
        clear_screen()
        
        user_input = pick_remaining_dataset(dna_dictionnary)
        file_path = os.path.join(dna_path, dna_dictionnary[user_input])
        # Vérifier si le fichier existe
        if not os.path.exists(file_path):
            print("ERREUR: Le fichier", dna_dictionnary[user_input], "n'existe pas.")
            continue

        print(f"Ajout du fichier {file_path} au mélange.")

        # Ajouter le fichier au dataframe (colonnes user_id et DNA)
        dna_dataframe = pd.read_csv(file_path)

        # Taille échantillon
        sample_size = pick_sample_size(dna_dataframe.shape[0])
        dna_dataframe = dna_dataframe.sample(sample_size)

        output_dataframe = pd.concat([output_dataframe, dna_dataframe], ignore_index=True)
        
        del dna_dictionnary[user_input]

        exit_app = exit_choice()
    
    # Enregistrement
    mixed_names_path = os.path.join(Config().getFormattedDatasetsPath(), "mixed_dna")
    if not os.path.exists(mixed_names_path):
        os.makedirs(mixed_names_path)

    output_file = name_output_file()
    output_path = os.path.join(mixed_names_path, output_file + ".csv")

    print(f"Enregistrement du mélange d'ADN dans le fichier {output_path}")
    output_dataframe.to_csv(output_path, index=False, header=True)
    print("Enregistrement terminé.")

    # Afficher les statistiques
    clear_screen()
    print_statistics(output_dataframe)
