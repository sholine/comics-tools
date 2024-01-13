#!/bin/bash

# Options par défaut
verbose=false
path="."

# Gestion des options en ligne de commande
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            verbose=true
            shift
            ;;
        -p|--path)
            path="$2"
            shift 2
            ;;
        *)
            echo "Option non reconnue : $1"
            exit 1
            ;;
    esac
done

# Vérifier si le chemin spécifié existe
if [ ! -d "$path" ]; then
    echo "Le chemin spécifié n'existe pas : $path"
    exit 1
fi

# Fonction pour afficher un message en mode verbose
afficher_verbose() {
    if [ "$verbose" = true ]; then
        echo "$1"
    fi
}

# Se déplacer vers le répertoire spécifié
cd "$path" || exit 1

# Trouver les fichiers cbz/cbr dans le dossier spécifié et ses sous-dossiers
IFS=$'\n'  # Définir le séparateur d'entrée sur le saut de ligne
liste_fichiers=($(find . -type f \( -iname "*.cbz" -o -iname "*.cbr" \)))

# Vérifier si la liste des fichiers est vide
if [ ${#liste_fichiers[@]} -eq 0 ]; then
    echo "Aucun fichier cbz/cbr trouvé dans le dossier courant et ses sous-dossiers."
    exit 0
fi

# Compteur total de fichiers
total_fichiers=${#liste_fichiers[@]}
compteur=0

# Parcourir chaque fichier trouvé
for fichier in "${liste_fichiers[@]}"; do
    ((compteur++))

    # Extraire le nom du dossier sans l'extension
    my_folder=$(basename "$fichier" | awk -F '.' '{print $1}')
    destination="$my_folder"

    afficher_verbose "($compteur/$total_fichiers) Création du dossier : $destination"

    # Créer le dossier s'il n'existe pas déjà
    mkdir -p "$destination"

    afficher_verbose "($compteur/$total_fichiers) Déplacement du fichier : $fichier -> $destination"

    # Déplacer le fichier dans le dossier créé
    mv "$fichier" "$destination"
    echo "($compteur/$total_fichiers) Le fichier $fichier a été déplacé vers $destination"
done

echo "Le traitement est terminé."
