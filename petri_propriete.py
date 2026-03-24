# petri_propriete.py

# on a besoin de la classe du reseau pour les types
from reseau_de_petri import ReseauPetri

# on essaye d'importer la librairie de dessin graphviz
from graphviz import Digraph


# classe pour analyser les propriétés mathematiques du reseau
class PetriPropriete:
    # le constructeur qui prend le reseau a etudier
    def __init__(self, reseau_petri):
        # on stocke le reseau dans l'instance
        self.reseau = reseau_petri        

    # fonction pour voir si une transition passe avec un etat fictif
    def verifier_transition_virtuelle(self, etat_courant, nom_transition):
        # on recupere les arcs entrants pour cette transition
        requis = self.reseau.arcs_entrants.get(nom_transition, {})
        
        # si ya pas d'arcs entrants c gratuit
        if not requis:
            # on retourne vrai direct
            return True

        # on boucle sur les places requises
        for nom_place, couleurs in requis.items():
            # on recupere les jetons qu'on a virtuellement
            jetons_dispos = etat_courant.get(nom_place, [])
            
            # on regarde pour chaque couleur demandée
            for couleur, qte in couleurs.items():
                # compteur temporaire pour verifier la quantité
                nb = 0
                # on compte combien on a de jetons de cette couleur
                for j in jetons_dispos:
                    # si le jeton correspond a la couleur
                    if j == couleur:
                        # on incremente le compteur
                        nb += 1
                
                # si on en a pas assez sa passe pas
                if nb < qte:
                    # on retourne faux car bloqué
                    return False
        # si on a tout verifié et que c bon
        return True
    
    # calcul le futur etat sans toucher au vrai reseau
    def simuler_tir(self, etat_courant, nom_transition):
        # on prepare le dictionnaire du futur etat
        etat_suivant = {}
        # on fait une copie profonde manuelle pour pas avoir de bugs
        for p, j in etat_courant.items():
            # on copie la liste des jetons
            etat_suivant[p] = list(j) 
        
        # on recupere ce qu'il faut consommer
        conso = self.reseau.arcs_entrants.get(nom_transition, {})
        # pour chaque place concernée par la consommation
        for place, couleurs in conso.items():
            # si la place existe bien dans l'etat
            if place in etat_suivant:
                # on prend la liste modifiable
                liste = etat_suivant[place]
                # pour chaque couleur a enlever
                for coul, nb in couleurs.items():
                    # on boucle le nombre de fois necessaire
                    for k in range(nb):
                        # si le jeton est la on l'enleve
                        if coul in liste:
                            # suppression de la liste
                            liste.remove(coul)

        # maintenant on regarde la production
        prod = self.reseau.arcs_sortants.get(nom_transition, {})
        # pour chaque place qui recoit des jetons
        for place, couleurs in prod.items():
            # si la place existe pas encore on la cree vide
            if place not in etat_suivant:
                # creation de la liste vide
                etat_suivant[place] = []
            # on recupere la reference vers la liste
            liste = etat_suivant[place]
            # pour chaque couleur a ajouter
            for coul, nb in couleurs.items():
                # on ajoute autant de jetons que prevu
                for k in range(nb):
                    # ajout a la fin de la liste
                    liste.append(coul)
        
        # on renvoi le nouvel etat calculé
        return etat_suivant
    
    # algorithme pour generer tout le graphe de marquage
    def analyser_espace_etats(self, mode='profondeur'):
        # dictionnaire pour stocker les etats uniques trouvés
        etats_connus = {}
        # dictionnaire d'adjacence pour le graphe
        structure_graphe = {}
        
        # on demare avec le marquage actuel du vrai reseau
        depart = self.reseau.marquage.copy()
        # on genere la clé unique pour cet etat
        cle_depart = self.reseau.cle_marquage(depart)
        
        # on enregistre l'etat initial
        etats_connus[cle_depart] = depart
        # on initialise sa liste de voisins
        structure_graphe[cle_depart] = []
        
        # liste des etats qu'il reste a explorer
        a_visiter = [cle_depart]
    
        

        # tant qu'il y a des etats dans la liste
        while len(a_visiter) > 0 : 
            # on choisi le prochain selon le mode choisi
            if mode == 'profondeur':
                # mode pile (LIFO) pour exploration en profondeur
                cle_actuelle = a_visiter.pop()
            else:
                # mode file (FIFO) pour exploration en largeur
                # c'est un peu lent mais sa marche
                cle_actuelle = a_visiter.pop(0)

            # on retrouve le detail du marquage via la clé
            marquage_actuel = etats_connus[cle_actuelle]
            
            # on test toutes les transitions possibles
            for trans in self.reseau.transitions : 
                # on verifi si la transition est activable virtuellement
                if self.verifier_transition_virtuelle(marquage_actuel, trans) : 
                    # on calcul le resultat du tir
                    nouveau = self.simuler_tir(marquage_actuel, trans)
                    # on genere la clé du nouvel etat
                    nouvelle_cle = self.reseau.cle_marquage(nouveau)

                    # si c'est un etat qu'on a jamais vu
                    if nouvelle_cle not in etats_connus : 
                        # on le stocke dans le dictionnaire
                        etats_connus[nouvelle_cle] = nouveau
                        # on prepare ses futurs voisins
                        structure_graphe[nouvelle_cle] = []
                        # on l'ajoute a la liste a traiter
                        a_visiter.append(nouvelle_cle)

                    # maintenant on doit ajouter l'arc dans le graphe
                    # on verifi d'abord si l'arc existe pas deja pour eviter doublons
                    existe = False
                    # on parcoure les arcs sortant de l'etat actuel
                    for arc in structure_graphe[cle_actuelle]:
                        # si on trouve la meme transition vers la meme destination
                        if arc[0] == trans and arc[1] == nouvelle_cle:
                            # on note que sa existe
                            existe = True
                            # on sort de la boucle
                            break
                    
                    # si l'arc n'existe pas encore
                    if not existe:
                        # on l'ajoute au graphe
                        structure_graphe[cle_actuelle].append((trans, nouvelle_cle))
        
        # on retourne les etats et la structure du graphe
        return etats_connus, structure_graphe

    # exporte le graphe de marquage en image png
    def exporter_graphe_png(self, nom_fichier, mode='largeur'):
        # on suppose graphviz présent, sinon l'import lèvera une erreur

        # on essaye de generer l'image
        try:
            # on calcul d'abord tout le graphe d'etats
            etats, graphe = self.analyser_espace_etats(mode=mode)
            
            # on initialise l'objet de dessin
            dessin = Digraph(comment="Graphe d'états", format='png')
            # on veut que le dessin aille de gauche a droite
            dessin.attr(rankdir='LR') 
            
            # dico pour mapé les clés complexes vers des IDs courts
            dico_id = {}
            
            # etape 1 : creation des noeuds visuels
            i = 0
            # pour chaque etat unique trouvé
            for cle_etat, marquage in etats.items():
                # on cree un identifiant court genre S0, S1
                id_noeud = f"S{i}"
                # on memorise la correspondance
                dico_id[cle_etat] = id_noeud
                
                # on construit le texte a afficher dans la bulle
                texte = f"Etat {i}"
                # on ajoute le detail des jetons par place
                for p, j in marquage.items():
                    # on affiche que si y a des jetons
                    if len(j) > 0:
                        # ajout de la ligne avec le compte
                        texte = texte + f"\n{p}: {len(j)}"
                
                # on ajoute le noeud au dessin
                dessin.node(id_noeud, texte, shape='ellipse')
                # on incremente le compteur
                i = i + 1
                
            # etape 2 : creation des fleches
            for source, liaisons in graphe.items():
                # on recupere l'id court de la source
                id_src = dico_id.get(source)
                # si on l'a trouvé (normalement oui)
                if id_src:
                    # pour chaque transition sortante
                    for nom_trans, dest in liaisons:
                        # on recupere l'id de la destination
                        id_dest = dico_id.get(dest)
                        # verif de securité
                        if id_dest:
                            # on trace la fleche avec le nom de la transition
                            dessin.edge(id_src, id_dest, label=nom_trans)
            
            # etape 3 : ecriture du fichier sur le disque
            # on nettoie l'extension si l'utilisateur l'a mise
            # etape 3 : ecriture du fichier sur le disque
            import os
             # enlève png si présent
            base, _ = os.path.splitext(nom_fichier)
            # dossier cible   # enlève png si présent
            dossier = os.path.dirname(base)
            # nom sans extension
            fichier = os.path.basename(base)

            chemin = dessin.render(
                filename=fichier,
                directory=dossier,
                cleanup=True
            )

            return True, chemin

            
        # si sa plante on capture l'exception
        except Exception as e:
            # on retourne le message d'erreur
            return False, str(e)
    
    

    # algo de tarjan pour trouver les composantes fortement connexes
    def executer_tarjan(self, noeuds, adjacence):
        # compteur global pour numérotation
        compteur = [0] 
        # pile pour stocker le chemin en cours
        pile = []
        # dictionnaire des index de decouverte
        indices = {}   
        # dictionnaire du lien le plus bas accessible (lowlink)
        lien_bas = {}  
        # liste pour savoir vite fait qui est dans la pile
        dans_pile = [] 
        # liste finale des groupes trouvés
        resultat = []       

        # fonction interne recursive pour le parcours
        def visite(v):
            # on donne un numero au noeud
            indices[v] = compteur[0]
            # au debut le lien bas est lui meme
            lien_bas[v] = compteur[0]
            # on incremente le compteur global
            compteur[0] += 1
            # on empile le noeud
            pile.append(v)
            # on note qu'il est dans la pile
            dans_pile.append(v)
            
            # on regarde tout les voisins
            voisins = adjacence.get(v, [])
            # la structure est (transition, destination) donc on prend w
            for trans, w in voisins:
                # si le voisin a pas ete visité
                if w not in indices:
                    # on le visite recursivement
                    visite(w)
                    # on met a jour le lien bas avec celui du voisin
                    lien_bas[v] = min(lien_bas[v], lien_bas[w])
                # si le voisin est deja dans la pile (c'est une boucle)
                elif w in dans_pile:
                    # on met a jour avec l'index du voisin
                    lien_bas[v] = min(lien_bas[v], indices[w])
            
            # si on est a la racine d'une composante connexe
            if lien_bas[v] == indices[v]:
                # on prepare le groupe
                composante = []
                # on depile tant qu'on est pas revenu a v
                while True:
                    # on sort le dernier element
                    w = pile.pop()
                    # on l'enleve du suivi de pile
                    dans_pile.remove(w) 
                    # on l'ajoute au groupe actuel
                    composante.append(w)
                    # si c'est v on s'arrete
                    if w == v: break
                # on stocke le groupe trouvé
                resultat.append(composante)

        # on lance la visite sur chaque noeud pas encore vu
        for v in noeuds:
            # si pas d'index c'est qu'il est nouveau
            if v not in indices:
                # appel recursif
                visite(v)

        # on retourne la liste des groupes
        return resultat
    
    # fonction principale pour verifier la vivacité du reseau
    def vivacite(self):
        # on genere d'abord tout le graphe d'etats
        etats, graphe = self.analyser_espace_etats(mode='largeur')
        # on recupere juste la liste des clés des etats
        liste_noeuds = list(etats.keys())

        # on utilise tarjan pour trouver les cycles et groupes fermés
        cfc = self.executer_tarjan(liste_noeuds, graphe)
        
        # on converti la liste des transitions en set pour comparer vite
        toutes_trans = set(self.reseau.transitions) 
        # on part du principe que c'est vivant jusqu'a preuve du contraire
        est_vivant = True

        # on analyse chaque composante fortement connexe
        for comp in cfc:
            # on verifi si c'est une composante terminale
            est_terminale = True
            # on met le groupe dans un set pour la recherche
            set_comp = set(comp) 

            # pour chaque etat dans ce groupe
            for etat in comp:
                # on regarde ou on peut aller
                suivants = graphe.get(etat, [])
                # pour chaque destination possible
                for tr, dest in suivants:
                    # si la destination sort du groupe
                    if dest not in set_comp:
                        # alors c pas une composante terminale
                        est_terminale = False
                        # pas la peine de continuer
                        break
                # si on sait deja que c pas terminal on stop
                if est_terminale == False: break
            
            # si c pas terminal on s'en fiche (on peut encore sortir)
            if not est_terminale: continue
            
            # ici on est coincé dans ce groupe d'etats
            # on regarde quelles transitions on peut encore tirer
            trans_possibles = set()
            # on parcours les arcs internes du groupe
            for etat in comp:
                # recuperation des voisins
                suivants = graphe.get(etat, [])
                # pour chaque transition sortante
                for tr, dest in suivants:
                    # comme c terminal dest est forcement dans le set_comp
                    if dest in set_comp: 
                        # on ajoute la transition a la liste des possibles
                        trans_possibles.add(tr)
            
            # vivacité : il faut qu'on puisse tirer TOUTES les transitions infiniment
            # si il en manque une dans cette composante finale c mort
            if trans_possibles != toutes_trans:
                # le reseau n'est pas vivant
                est_vivant = False

        # on retourne le verdict final
        return est_vivant
