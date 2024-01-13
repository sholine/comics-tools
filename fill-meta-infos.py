import os
import requests
import xml.etree.ElementTree as ET
from zipfile import ZipFile
try:
    from rarfile import RarFile
except ImportError:
    raise ImportError("La bibliothèque 'rarfile' n'est pas installée. Veuillez exécuter 'pip install -r requirements.txt' pour installer les dépendances.")
import sys

from config import CLE_API_COMICVINE

def interroger_api(nom_serie):
    url = "https://comicvine.gamespot.com/api/search/"
    params = {
        "api_key": CLE_API_COMICVINE,
        "format": "json",
        "query": nom_serie,
        "resources": "volume"
    }

    response = requests.get(url, params=params)
    print (response);

    if response.status_code == 200:
        data = response.json()
        if data.get("results"):
            result = data["results"][0]
            return {
                "nom_serie": result.get("name"),
                "auteurs": [creator["name"] for creator in result.get("creators", [])],
                "serie_terminee": result.get("count_of_issues") == result.get("issues"),
                "nombre_volumes": result.get("count_of_issues", 0)
            }
        else:
            print(f"Aucune série trouvée pour le nom : {nom_serie}")
            return None
    else:
        print("Erreur lors de la requête à l'API ComicVine.")
        return None

def obtenir_informations():
    nom_serie = os.path.basename(os.path.abspath(".")).split(" - ")[0]
    data = interroger_api(nom_serie)

    if data:
        print("Informations récupérées depuis l'API:")
        print(f"Nom de la série: {data.get('nom_serie')}")
        print(f"Auteur(s): {', '.join(data.get('auteurs', []))}")
        print(f"Série terminée: {data.get('serie_terminee')}")
        print(f"Nombre total de volumes: {data.get('nombre_volumes')}")

        confirmation = input("Les informations sont-elles correctes ? (o/n): ").lower()

        if confirmation == 'o':
            return data
        else:
            # Demander à l'utilisateur de corriger les informations une par une
            data["nom_serie"] = input(f"Nom de la série ({data['nom_serie']}): ") or data["nom_serie"]
            data["auteurs"] = input(f"Auteur(s) ({', '.join(data['auteurs'])}): ").split(',') or data["auteurs"]
            data["serie_terminee"] = input(f"La série est-elle terminée ? (o/n) ({'o' if data['serie_terminee'] else 'n'}): ").lower() == 'o'
            data["nombre_volumes"] = int(input(f"Nombre total de volumes ({data['nombre_volumes']}): ")) or data["nombre_volumes"]
            return data
    else:
        return None

def creer_comicinfo_xml(nom_fichier, informations):
    root = ET.Element("ComicInfo")

    ET.SubElement(root, "Title").text = informations["nom_serie"]
    ET.SubElement(root, "Writer").text = ', '.join(informations["auteurs"])
    ET.SubElement(root, "Series").text = informations["nom_serie"]
    ET.SubElement(root, "Volume").text = str(int(nom_fichier.split(" - ")[-1].split(".")[0]))

    if informations["serie_terminee"]:
        ET.SubElement(root, "StoryArc").text = "Terminé"

    tree = ET.ElementTree(root)
    tree_str = ET.tostring(root, encoding="utf-8", method="xml").decode("utf-8")
    
    # Ajouter le ComicInfo.xml à l'archive cbr ou cbz
    chemin_fichier = os.path.join(nom_dossier, nom_fichier)
    if nom_fichier.lower().endswith('.cbz'):
        with ZipFile(chemin_fichier, 'a') as archive:
            archive.writestr("ComicInfo.xml", tree_str)
    elif nom_fichier.lower().endswith('.cbr'):
        with RarFile(chemin_fichier, 'a') as archive:
            archive.writestr("ComicInfo.xml", tree_str)
    
    print(f"ComicInfo.xml ajouté à {nom_fichier}")

def main(nom_dossier):
    informations = obtenir_informations()

    if informations:
        fichiers = [f for f in os.listdir(nom_dossier) if f.lower().endswith(('.cbr', '.cbz'))]

        for fichier in fichiers:
            creer_comicinfo_xml(fichier, informations)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_principal.py <nom_dossier>")
        sys.exit(1)

    nom_dossier = sys.argv[1]
    main(nom_dossier)