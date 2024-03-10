import os
import sys
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression,SGDClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score, roc_auc_score
from sklearn.preprocessing import StandardScaler

from tqdm import tqdm

import random_usernames
import features_process
import gridsearch


# Retrieving config file
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
import csv
datasets_path, datasets_list, formatted_datasets_path = Config().getDatasetsConfig()
formatted_datasets_path = os.path.join(formatted_datasets_path, "nameclass")



# ARGUMENT PARSING. 
def parse_args():
    parser = argparse.ArgumentParser(description='Utilise un modèle d\'apprentissage automatique pour classifier les bots et les humains en fonction de leurs noms')
    show_or_train = parser.add_mutually_exclusive_group(required=True)
    show_or_train.add_argument('--show', action='store_true', help='Affiche les ensembles de données disponibles.')
    show_or_train.add_argument('--dataset',type=str, help='Nom de l\'ensemble de données à utiliser pour entraîner le modèle sans l\'extension.')
    parser.add_argument('--random', action='store_true', help='Remplace les bots dans les ensembles de données par des chaînes aléatoires de 15 caractères.')
    parser.add_argument('--grid', action='store_true', help='Lance la gridsearch pour trouver les meilleurs paramètres.')
    args = parser.parse_args()

    if args.show:
        print_datasets()
        sys.exit(0)
    else:
        dataset_path = os.path.join(formatted_datasets_path, args.dataset + ".csv")
        if not os.path.exists(dataset_path):
            print("Error: The dataset", args.dataset, "does not exist.")
            print_datasets()
            sys.exit(1)
        print("Valeur de l'argument --random:", args.random)
        return args

def print_datasets():
    print("Available datasets:")
    for dataset in Path(formatted_datasets_path).iterdir():
        print("  -", dataset.name.split(".")[0])


def load_dataset(dataset_path,is_bots_random=False):
    csv_path = os.path.join(formatted_datasets_path, dataset_path + ".csv")
    df = pd.read_csv(csv_path, header=None, names=["screen_name", "label"])

    if is_bots_random:
        nb_humans = df.shape[0]
        list_bot_names = [random_usernames.generate_random_name(15) for i in range(nb_humans)]
        df_bots = pd.DataFrame({"screen_name": list_bot_names, "label": "BOT"})
        df = df[df['label'] == "HUMAN"]
        df = pd.concat([df, df_bots])

    df['label'] = df['label'].map({'HUMAN': 0, 'BOT': 1})
    return df

def gather_features(names_df):
    screen_names = names_df['screen_name'].tolist()
    features = features_process.tfidf(screen_names)

    for i in range(len(screen_names)):
        features[i].append(float(features_process.shannon_entropy(screen_names[i])))
        features[i].append(float(features_process.upper_count(screen_names[i])))
        features[i].append(float(features_process.lower_count(screen_names[i])))
    return features

def split(features, df_name):
    X_train, X_test, y_train, y_test = train_test_split(features, df_name['label'], test_size=0.2, stratify=df_name['label'])
    return X_train, X_test, y_train, y_test

def train_LR(X_train, y_train, X_test, y_test, grid=False):
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    if grid:
        grid_search = gridsearch.gridsearch_LR(X_train, X_test, y_train, y_test)
        best_model = grid_search.best_estimator_
        y_pred = best_model.predict(X_test)
    else:
        model = LogisticRegression(C=0.1, max_iter=100, solver='saga', tol=0.001, verbose=0)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)


    print("Confusion matrix: ")
    print(pd.crosstab(y_test, y_pred, rownames=['Actual'], colnames=['Predicted']))
    print("-------------------")
    print("Accuracy: ", accuracy_score(y_test, y_pred))
    print("F1 score: ", f1_score(y_test, y_pred))
    print("Recall: ", recall_score(y_test, y_pred))
    print("Precision: ", precision_score(y_test, y_pred))
    print("ROC AUC: ", roc_auc_score(y_test, y_pred))


if __name__ == "__main__":
    args = parse_args()

    print("LOADING DATASET: ", args.dataset)
    load_dataset(args.dataset, args.random)

    names_df = load_dataset(args.dataset, args.random)
    features = gather_features(names_df)

    X_train, X_test, y_train, y_test = split(features, names_df)
    train_LR(X_train, y_train, X_test, y_test, grid=args.grid)



