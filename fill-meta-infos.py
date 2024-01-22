import os
import requests
import xml.etree.ElementTree as ET
from zipfile import ZipFile
import patoolib
import sys
from xml.dom import minidom

from config import CLE_API_COMICVINE

def interroger_api(nom_serie):
    url = "https://comicvine.gamespot.com/api/search/"
    params = {
        "api_key": CLE_API_COMICVINE,
        "format": "json",
        "query": nom_serie,
        "resources": "volume"
    }

    headers = {
        "User-Agent": "MonScriptComicInfo/1.0"  # Remplacez cela par le nom de votre script ou application
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data.get("results"):
            # Récupérer les informations du premier résultat
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
        print(f"Erreur lors de la requête à l'API ComicVine: {response.text}")
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

    # Utiliser minidom pour l'indentation
    dom = minidom.parseString(tree_str)
    tree_str_indente = dom.toprettyxml(indent="  ")

    chemin_fichier = os.path.join(nom_dossier, nom_fichier)
    
    # Ajouter le ComicInfo.xml à une nouvelle archive cbr ou cbz
    if nom_fichier.lower().endswith(('.cbz', '.cbr')):
        # Extraire l'archive
        extraction_dossier = os.path.join(nom_dossier, "temp_extraction")
        patoolib.extract_archive(chemin_fichier, outdir=extraction_dossier)

        # Ajouter le fichier ComicInfo.xml
        fichier_nouveau = os.path.join(extraction_dossier, "ComicInfo.xml")
        with open(fichier_nouveau, 'w', encoding='utf-8') as f:
            f.write(tree_str_indente)

        # Recréer l'archive
        nouvelle_archive = os.path.join(nom_dossier, f"nouveau_{nom_fichier}")
        patoolib.create_archive(nouvelle_archive, [extraction_dossier])

        # Remplacer l'ancien fichier par le nouveau
        os.remove(chemin_fichier)
        os.rename(nouvelle_archive, chemin_fichier)

        # Nettoyer le dossier temporaire
        os.rmdir(extraction_dossier)

        print(f"ComicInfo.xml ajouté à {nom_fichier}")
    else:
        print(f"Le fichier {nom_fichier} n'est pas un fichier .cbz ou .cbr et sera ignoré.")


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