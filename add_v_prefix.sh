#!/bin/bash

# Définir le dossier par défaut
folder=${1:-"."}

# Vérifier si le dossier spécifié existe
if [ ! -d "$folder" ]; then
  echo "Le dossier spécifié n'existe pas."
  exit 1
fi

# Rechercher tous les fichiers CBR et CBZ dans le dossier et ses sous-dossiers
find "$folder" -type f \( -iname "*.cbz" -o -iname "*.cbr" \) | while read -r file; do
  # Extraire le numéro de volume à partir du nom du fichier
  volume_number=$(echo "$file" | grep -o -E ' - [0-9]{2,3}' | sed 's/ - //')

  # Vérifier s'il y a un numéro de volume
  if [ -n "$volume_number" ] && ! echo "$file" | grep -q -E "/V$volume_number/"; then
    # Renommer le fichier en ajoutant "V" devant le numéro de volume
    new_name=$(echo "$file" | sed "s/ - $volume_number/ - V$volume_number/")
    mv "$file" "$new_name"
    echo "Renommé : $file -> $new_name"
  fi
done

echo "Traitement terminé."
