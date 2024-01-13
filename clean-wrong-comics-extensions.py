import os
import argparse
import subprocess

def afficher_verbose(message):
    if args.verbose:
        print(message)

def renommer_fichiers(path):
    liste_fichiers = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.lower().endswith(('.cbz', '.cbr')):
                liste_fichiers.append(os.path.join(root, file))
    
    total_fichiers = len(liste_fichiers)
    compteur = 0

    for fichier in liste_fichiers:
        compteur += 1

        afficher_verbose(f"({compteur}/{total_fichiers}) Test du fichier : {fichier}")

        # Utiliser la commande "file" pour déterminer le type de fichier
        type_fichier = subprocess.check_output(["file", "-b", fichier], text=True).strip()

        # Extraire l'extension du fichier en minuscules
        extension = os.path.splitext(fichier)[1].lower()

        # Vérifier si le fichier est un fichier RAR (cbz) ou Zip (cbr)
        if "RAR" in type_fichier and extension != ".cbr":
            # Remplacer l'extension "cbz" par "cbr"
            nouveau_nom = fichier.rsplit('.', 1)[0] + ".cbr"
        elif "Zip" in type_fichier and extension != ".cbz":
            # Remplacer l'extension "cbr" par "cbz"
            nouveau_nom = fichier.rsplit('.', 1)[0] + ".cbz"
        else:
            # Ne rien faire si l'extension correspond déjà au type de fichier
            continue

        afficher_verbose(f"({compteur}/{total_fichiers}) Renommage du fichier : {fichier} -> {nouveau_nom}")

        # Renommer le fichier
        os.rename(fichier, nouveau_nom)
        print(f"({compteur}/{total_fichiers}) Le fichier {fichier} a été renommé en {nouveau_nom}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script de renommage des fichiers cbz/cbr.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Activer le mode verbeux")
    parser.add_argument("-p", "--path", default=".", help="Chemin du dossier à traiter")
    args = parser.parse_args()

    if not os.path.exists(args.path):
        print(f"Le chemin spécifié n'existe pas : {args.path}")
        exit(1)

    renommer_fichiers(args.path)
