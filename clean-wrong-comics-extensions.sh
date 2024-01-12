#!/bin/bash

# Options par défaut
verbose=false
path="."  # Chemin par défaut

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

# Trouver les fichiers cbz/cbr dans le dossier spécifié et ses sous-dossiers
IFS=$'\n'  # Définir le séparateur d'entrée sur le saut de ligne
liste_fichiers=($(find "$path" -type f \( -iname "*.cbz" -o -iname "*.cbr" \)))

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

    # Utiliser la commande "file" pour déterminer le type de fichier
    type_fichier=$(file -b "$fichier")

    afficher_verbose "($compteur/$total_fichiers) Test du fichier : $fichier"

    # Extraire l'extension du fichier en minuscules
    extension=$(echo "$fichier" | rev | cut -d. -f1 | rev | tr '[:upper:]' '[:lower:]')

    # Vérifier si le fichier est un fichier RAR (cbz) ou Zip (cbr)
    if [[ "$type_fichier" == *RAR* && "$extension" != "cbr" ]]; then
        # Remplacer l'extension "cbz" par "cbr"
        nouveau_nom="${fichier/%.cbz/.cbr}"
    elif [[ "$type_fichier" == *Zip* && "$extension" != "cbz" ]]; then
        # Remplacer l'extension "cbr" par "cbz"
        nouveau_nom="${fichier/%.cbr/.cbz}"
    else
        # Ne rien faire si l'extension correspond déjà au type de fichier
        continue
    fi

    afficher_verbose "($compteur/$total_fichiers) Renommage du fichier : $fichier -> $nouveau_nom"

    # Renommer le fichier
    mv -n "$fichier" "$nouveau_nom"
    echo "($compteur/$total_fichiers) Le fichier $fichier a été renommé en $nouveau_nom"
done
