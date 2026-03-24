# json_sauv_import.py

# il faut importer le module pour jérer le format json
import json
# on recupere la classe du reseau de petri depuis l'autre fichié
from reseau_de_petri import ReseauPetri

# cette fonction va servir a ecrir l'état du reseau sur le disque
def enregistrer_reseau_petri(reseau, nom_fichier):
    # on initialise un dictionaire vide pour y mettre les capacités modifiées
    capacites_sauv = {}
    # on doit parcourir chaque capacité pour verifier si c'est l'infini
    for p, c in reseau.capacites.items():
        # json ne gere pas bien le concept mathématique d'infini alors on verifi
        if c == float('inf'):
            # on remplace la valeur infini par une chaine de caractere explicite
            capacites_sauv[p] = "inf"
        # sinon on garde la valeur numerique telle qu'elle est
        else:
            # on stoke la capacité normale dans le dictionnaire temporaire
            capacites_sauv[p] = c

    # on construit l'objet complet qui contiendra toutes les donées a sauvegarder
    donnees = {
        # on sauvegarde la liste des places du reseau
        "places": reseau.places,
        # on ajoute aussi la liste des transitions pour pas les perdes
        "transitions": reseau.transitions,
        # il faut memoriser les arcs qui entrent dans les noeuds
        "arcs_entrants": reseau.arcs_entrants,
        # de meme on sauvegarde les arcs qui sortent des noeuds
        "arcs_sortants": reseau.arcs_sortants,
        # on garde l'etat actuel des jetons dans le marquage
        "marquage": reseau.marquage,
        # on utilise le dictionnaire de capacités qu'on a netoyé juste avant
        "capacites": capacites_sauv
    }

    # on tente d'ouvrir le fichier pour ecrire dedans
    try:
        # l'ouverture se fait en mode ecriture avec l'encodage standard
        with open(nom_fichier, 'w', encoding='utf-8') as fichier:
            # on transforme le dictionnaire en texte formaté avec une indentation
            json.dump(donnees, fichier, indent=4)
        # si tout s'est bien passé on previen l'utilisateur
        print("Sauvegarde reussie.")
        # on renvoi vrai pour dire que la fonction a reussi
        return True
    # si jamais il y a un probleme pendant l'ecriture du fichié
    except Exception as e:
        # on affiche le message d'erreur pour comprendre ce qui a foiré
        print(f"Erreur sauvegarde : {e}")
        # on renvoi faux pour signaler l'echec de l'operation
        return False

# cette fonction permet de relire un reseau depuis un fichier existant
def charger_reseau_petri(nom_fichier):
    # on essaye d'acceder au fichier en mode lecture
    try:
        # on ouvre le fichier en specifiant le bon encodage de caracteres
        with open(nom_fichier, 'r', encoding='utf-8') as fichier:
            # on charge le contenu du json dans une variable python
            donnees = json.load(fichier)
            
        # on extrait la liste des places depuis les données chargés
        places = donnees.get("places", [])
        # on recupere la liste des transitions du reseau
        transitions = donnees.get("transitions", [])
        # on reprend la structure des arcs entrants s'ils existent
        arcs_entrants = donnees.get("arcs_entrants", {})
        # on fait la meme chose pour les arcs sortants
        arcs_sortants = donnees.get("arcs_sortants", {})
        # on recupere la configuration des jetons dans le marquage
        marquage = donnees.get("marquage", {})
        
        # on recupere les capacités brutes qui contiennent peut-etre des chaines
        capacites_brutes = donnees.get("capacites", {})
        # on prepare un nouveau dictionnaire pour les capacités converties
        capacites = {}
        # on boucle sur les items pour retablir les valeurs speciales
        for p, c in capacites_brutes.items():
            # on regarde si la valeur est la chaine representant l'infini
            if c == "inf":
                # on remet le vrai objet float infini de python
                capacites[p] = float('inf')
            # si c'est pas infini c'est un nombre normal
            else:
                # on assigne simplement la valeur tel quel
                capacites[p] = c

        # on instancie un nouvel objet reseau avec tout les elements reconstruits
        nouv_reseau = ReseauPetri(places, transitions, arcs_entrants, arcs_sortants, marquage, capacites)
        # on signale que le chargement s'est bien terminé
        print("Chargement reussi.")
        # on retourne l'objet reseau fraichement crée
        return nouv_reseau
        
    # on attrape les erreurs si le fichier existe pas ou est corompu
    except Exception as e:
        # on imprime la cause du probleme pour le debugage
        print(f"Erreur chargement : {e}")
        # on renvoi rien car on a pas pu creer le reseau
        return None
