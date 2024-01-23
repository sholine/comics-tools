#!/bin/bash

# Options par défaut
path="."

# Gestion des options en ligne de commande
while [[ "$#" -gt 0 ]]; do
    case $1 in
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

# Fonction pour afficher un message de log
afficher_log() {
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1"
}

# Fonction pour vérifier si un répertoire ne contient qu'un seul fichier
est_seul() {
    local dossier="$1"
    local nombre_fichiers=$(find "$dossier" -maxdepth 1 -type f | wc -l)
    [ "$nombre_fichiers" -eq 1 ]
}

# Fonction pour renommer le fichier avec le suffixe "[OneShot]"
renommer_oneshot() {
    local fichier="$1"
    local nouveau_nom="${fichier%.*} [OneShot].${fichier##*.}"
    #mv "$fichier" "$nouveau_nom"
    afficher_log "Le fichier $fichier a été renommé en $nouveau_nom"
}

# Se déplacer vers le répertoire spécifié
cd "$path" || exit 1

# Trouver tous les fichiers cbz/cbr du dossier spécifié, y compris les sous-dossiers
IFS=$'\n'  # Définir le séparateur d'entrée sur le saut de ligne
liste_fichiers=($(find . -type f \( -iname "*.cbz" -o -iname "*.cbr" \)))

# Parcourir chaque fichier trouvé
for fichier in "${liste_fichiers[@]}"; do
    # Extraire le nom du répertoire parent
    parent_directory=$(dirname "$fichier")

    # Extraire le nom du fichier sans l'extension
    base_filename=$(basename -- "$fichier")
    filename_without_extension="${base_filename%.*}"

    # Vérifier si le fichier est le seul fichier du répertoire parent
    if est_seul "$parent_directory"; then
        # Vérifier si le nom de fichier contient un numéro à 2 chiffres au milieu
        if echo "$filename_without_extension" | grep -q -E " - (V)?[0-9]{2}"; then
            continue
        fi

        # Vérifier si le fichier contient déjà le suffixe "[OneShot]"
        if [[ "$filename_without_extension" == *"[OneShot]"* ]]; then
            continue
        fi

        # Vérifier si le fichier contient déjà le suffixe "[Special]"
        if [[ "$filename_without_extension" == *"[Special]"* ]]; then
            continue
        fi

        renommer_oneshot "$fichier"
    fi
done

afficher_log "Le traitement est terminé."
