# reseau_de_petri.py

# definition de la classe principale qui gere toute la logique
class ReseauPetri:
    # c'est le constructeur qui s'execute quand on cree un objet
    # on permet de passer des listes ou rien du tout
    def __init__(self, places=None, transitions=None, arcs_entrants=None, arcs_sortants=None, marquage=None, capacites=None):
        
        # on regarde si on a recu une liste de places
        if places is None:
            # si non on initialise une liste vide pour eviter les bugs
            self.places = []
        # si on a recu quelque chose
        else:
            # on l'enregistre dans l'attribut de l'objet
            self.places = places

        # on fait pareil pour la liste des transitions
        if transitions is None:
            # une liste vide pour commencer proprement
            self.transitions = []
        # si l'utilisateur a donné des transitions
        else:
            # on les stocke dans la variable de classe
            self.transitions = transitions
        
        # dictionnaire pour les arcs qui vont des places vers les transitions
        if arcs_entrants is None:
            # un dico vide si rien n'est fourni
            self.arcs_entrants = {}
        # sinon on prend ce qu'on nous donne
        else:
            # on sauvegarde la structure des arcs entrants
            self.arcs_entrants = arcs_entrants

        # dictionnaire pour les arcs qui partent des transitions
        if arcs_sortants is None:
            # on initialise le dictionnaire vide
            self.arcs_sortants = {}
        # si on a recu des donnees
        else:
            # on les assigne a l'attribut correspondant
            self.arcs_sortants = arcs_sortants
        
        # dictionnaire qui contient l'etat actuel des jetons
        if marquage is None:
            # vide par defaut car au debut y a rien
            self.marquage = {}
        # si on veut demarrer avec un etat precis
        else:
            # on enregistre le marquage initial
            self.marquage = marquage

        # dictionnaire pour limiter le nombre de jetons par place
        if capacites is None:
            # par defaut y a pas de limites
            self.capacites = {}
        # si des capacites sont specifiees
        else:
            # on les mémorise pour les verifications futures
            self.capacites = capacites

    # methodes utilitaires

    # cette fonction sert a avoir une version texte de l'etat
    def obtenir_texte_marquage(self):
        # on prepare une chaine vide pour construire le resultat
        texte = ""
        # on boucle sur chaque place et ses jetons
        for place, jetons in self.marquage.items():
            # on concatene le nom et la liste des jetons
            texte = texte + place + ": " + str(jetons) + " | "
        # on renvoi le texte complet a la fin
        return texte

    # on a besoin de transformer le marquage en truc immuable pour les sets
    def cle_marquage(self, marquage):
        # on prepare une liste temporaire
        liste = []
        # on parcoure le dictionnaire de marquage
        for p, j in marquage.items():
            # on trie les jetons pour que l'ordre change rien
            tuple_jetons = tuple(sorted(j))
            # on ajoute le couple place/jetons a la liste
            liste.append((p, tuple_jetons))
        # on retourne un tuple trié qui servira de clé unique
        return tuple(sorted(liste))

    # fonction pour savoir combien y a de jetons par couleur au total
    def compteur_jeton_par_couleur(self):
        # on initialise un compteur vide
        compteur = {}
        # on regarde les jetons de toutes les places
        for jetons in self.marquage.values():
            # pour chaque couleur de jeton dans la liste
            for c in jetons:
                # si on connait deja cette couleur
                if c in compteur:
                    # on ajoute un au total
                    compteur[c] += 1
                # si c'est la premiere fois qu'on voit cette couleur
                else:
                    # on initialise le compte a un
                    compteur[c] = 1
        # on renvoi le dictionnaire avec les totaux
        return compteur

    # logique du reseau

    # cette methode verifi si on a le droit de tirer une transition
    def est_tirable(self, nom_transition):
        # securité pour pas planter si la transition existe pas
        if nom_transition not in self.transitions:
            # c'est impossible de tirer un truc qui n'existe pas
            return False

        # etape 1 : on verifi qu'on a assez de jetons en entree
        arcs_requis = self.arcs_entrants.get(nom_transition, {})
        
        # on verifi pour chaque place connectée en entree
        for nom_place, couleurs_requises in arcs_requis.items():
            # on recupere les jetons qu'il y a vraiment dans la place
            jetons_actuels = self.marquage.get(nom_place, [])
            
            # on verifi couleur par couleur
            for couleur, quantite in couleurs_requises.items():
                # on compte combien on a de jetons de cette couleur
                nb = jetons_actuels.count(couleur)
                # si on en a moins que ce qu'il faut
                if nb < quantite:
                    # la transition est bloquee
                    return False
        
        # etape 2 : on verifi qu'il y a de la place en sortie
        arcs_produits = self.arcs_sortants.get(nom_transition, {})
        # on regarde chaque place de destination
        for nom_place, couleurs_produites in arcs_produits.items():
            # on recupere la capacite max de la place (infini par defaut)
            limite = self.capacites.get(nom_place, float('inf'))
            
            # on calcul combien de jetons on va rajouter
            nb_a_ajouter = 0
            # on somme toutes les couleurs produites
            for q in couleurs_produites.values():
                # ajout au total temporaire
                nb_a_ajouter += q
                
            # on regarde combien y a deja de jetons
            nb_actuel = len(self.marquage.get(nom_place, []))
            
            # si le total depasse la limite autorisee
            if (nb_actuel + nb_a_ajouter) > limite:
                # on a pas le droit de tirer a cause de la capacite
                return False
            
        # si on arrive la c'est que tout est bon
        return True

    # cette methode fait le vrai changement d'etat
    def appliquer_changement(self, nom_transition):
        # on verifi d'abord si c'est possible
        if not self.est_tirable(nom_transition):
            # si non on fait rien et on le dit
            return False
        
        # partie consommation : on enleve les jetons
        consommation = self.arcs_entrants.get(nom_transition, {})
        # parcours des places sources
        for nom_place, couleurs in consommation.items():
            # parcours des couleurs a enlever
            for couleur, nb in couleurs.items():
                # on boucle le nombre de fois necessaire
                for i in range(nb):
                    # on verifi que la couleur est la par securite
                    if couleur in self.marquage[nom_place]:
                        # on supprime le jeton de la liste
                        self.marquage[nom_place].remove(couleur)

        # partie production : on ajoute les nouveaux jetons
        production = self.arcs_sortants.get(nom_transition, {})
        # parcours des places destinations
        for nom_place, couleurs in production.items():
            # parcours des couleurs a ajouter
            for couleur, nb in couleurs.items():
                # on boucle pour ajouter le bon nombre
                for i in range(nb):
                    # on ajoute le jeton dans la liste de la place
                    self.marquage[nom_place].append(couleur)
        
        # l'operation s'est bien passée
        return True

    # renvoi la liste de toutes les transitions actives
    def transitions_disponibles(self):
        # liste vide pour stocker les resultats
        liste = []
        # on test toutes les transitions du reseau
        for t in self.transitions:
            # si la transition est tirable
            if self.est_tirable(t):
                # on l'ajoute a notre liste
                liste.append(t)
        # on retourne la liste complete
        return liste

    # ajout, modification et suppression 

    # permet de creer une nouvelle place dynamiquement
    def ajouter_place(self, nom, jetons_initiaux=None, capacite=float('inf')):
        # on verifi que le nom existe pas deja
        if nom in self.places:
            # echec si doublon
            return False
        
        # si pas de jetons specifiés on met vide
        if jetons_initiaux is None:
            # liste vide par defaut
            jetons_initiaux = []
            
        # on ajoute le nom a la liste des places
        self.places.append(nom)
        # on initialise le marquage pour cette place
        self.marquage[nom] = list(jetons_initiaux)
        # on regle la capacité
        self.capacites[nom] = capacite
        # tout est ok
        return True

    # permet d'ajouter une transition au reseau
    def ajouter_transition(self, nom):
        # verification des doublons
        if nom in self.transitions:
            # echec si le nom est pris
            return False
        # ajout a la liste officielle
        self.transitions.append(nom)
        # reussite
        return True

    # creer un lien d'une place vers une transition
    def ajouter_arcs_entrants(self, nom_trans, nom_place, poid):
        # on initialise le sous-dict pour cette transition si besoin
        if nom_trans not in self.arcs_entrants:
            # creation du dico vide
            self.arcs_entrants[nom_trans] = {}
        
        # on enregistre le poids de l'arc
        self.arcs_entrants[nom_trans][nom_place] = poid.copy()
        # sa a marché
        return True

    # creer un lien d'une transition vers une place
    def ajouter_arcs_sortants(self, nom_trans, nom_place, poid):
        # verif si la transition a deja des sorties
        if nom_trans not in self.arcs_sortants:
            # si non on cree le dictionnaire
            self.arcs_sortants[nom_trans] = {}
            
        # on stocke le poids pour cette destination
        self.arcs_sortants[nom_trans][nom_place] = poid.copy()
        # retour positif
        return True

    # modifier les proprietes d'une place existante
    def modifier_place(self, nom, nouveau_nom, nouveaux_jetons):
        # on verifi que la place existe bien
        if nom in self.places:
            # si on veut changer le nom
            if nouveau_nom and nouveau_nom != nom:
                # IMPORTANT : on verifi que le nouveau nom est pas deja pris
                if nouveau_nom in self.places:
                    # si le nom existe deja on annule tout
                    return False
                    
                # on trouve sa position dans la liste
                idx = self.places.index(nom)
                # on met a jour le nom dans la liste
                self.places[idx] = nouveau_nom
                # on deplace les jetons vers la nouvelle clé
                self.marquage[nouveau_nom] = self.marquage.pop(nom)
                
                # il faut aussi mettre a jour les arcs entrants qui pointent dessus
                for t in self.arcs_entrants:
                    # si l'ancien nom est dans les sources
                    if nom in self.arcs_entrants[t]:
                        # on recupere la valeur et on supprime l'ancienne cle
                        data = self.arcs_entrants[t].pop(nom)
                        # on remet avec le nouveau nom
                        self.arcs_entrants[t][nouveau_nom] = data

                # pareil pour les arcs sortants qui pointent dessus
                for t in self.arcs_sortants:
                    # si l'ancien nom est dans les destinations
                    if nom in self.arcs_sortants[t]:
                        # on echange les clés
                        data = self.arcs_sortants[t].pop(nom)
                        # nouveau nom assigné
                        self.arcs_sortants[t][nouveau_nom] = data

                # on met a jour la variable nom pour la suite
                nom = nouveau_nom
                
            # si on veut changer les jetons
            if nouveaux_jetons is not None:
                # on ecrase l'ancien marquage
                self.marquage[nom] = nouveaux_jetons
            # operation reussie
            return True
        # la place n'existait pas
        return False

    # changer le nom d'une transition
    def modifier_nom_transition(self, ancien, nouveau):
        # on verifi que l'ancien existe et le nouveau est libre
        if ancien in self.transitions and nouveau not in self.transitions:
            # on recupere l'index
            idx = self.transitions.index(ancien)
            # on change le nom dans la liste
            self.transitions[idx] = nouveau
            
            # on deplace les arcs entrants vers la nouvelle clé
            if ancien in self.arcs_entrants:
                # pop et assignation directe
                self.arcs_entrants[nouveau] = self.arcs_entrants.pop(ancien)
            # pareil pour les arcs sortants
            if ancien in self.arcs_sortants:
                # transfert des données
                self.arcs_sortants[nouveau] = self.arcs_sortants.pop(ancien)
            # tout est bon
            return True
        # echec de la modification
        return False
        
    # supprimer definitivement une place
    def supprimer_place(self, nom):
        # verif presence
        if nom in self.places:
            # suppression de la liste
            self.places.remove(nom)
            # suppression des jetons associes
            del self.marquage[nom]
            
            # nettoyage des arcs entrants orphelins
            for t in self.arcs_entrants:
                # si la place etait une source
                if nom in self.arcs_entrants[t]:
                    # on supprime l'entrée
                    del self.arcs_entrants[t][nom]

            # nettoyage des arcs sortants orphelins
            for t in self.arcs_sortants:
                # si la place etait une destination
                if nom in self.arcs_sortants[t]:
                    # on la supprime
                    del self.arcs_sortants[t][nom]

            # suppression terminee
            return True
        # la place etait pas la
        return False

    # supprimer une transition
    def supprimer_transition(self, nom):
        # on regarde si elle est la
        if nom in self.transitions:
            # on l'enleve de la liste
            self.transitions.remove(nom)
            # on supprime ses arcs entrants si y en a
            if nom in self.arcs_entrants: del self.arcs_entrants[nom]
            # on supprime ses arcs sortants aussi
            if nom in self.arcs_sortants: del self.arcs_sortants[nom]
            # succes
            return True
        # pas trouvé
        return False
            
    # supprimer un arc specifique entre deux noeuds
    def supprimer_arc(self, t, p, type_arc):
        # si c'est un arc entrant (place vers transition)
        if type_arc == 'entrant':
            # on verifi que le lien existe
            if t in self.arcs_entrants and p in self.arcs_entrants[t]:
                # on le supprime du dictionnaire
                del self.arcs_entrants[t][p]
                # c'est fait
                return True
        # sinon c'est un arc sortant (transition vers place)
        else:
            # verif existence
            if t in self.arcs_sortants and p in self.arcs_sortants[t]:
                # suppression
                del self.arcs_sortants[t][p]
                # ok
                return True
        # echec on a rien trouvé
        return False
        
    # changer le poids d'un arc existant
    def modifier_poids_arc(self, t, p, type_arc, poids):
        # si c'est un arc entrant
        if type_arc == 'entrant':
            # on utilise la fonction d'ajout qui ecrase la valeur
            return self.ajouter_arcs_entrants(t, p, poids)
        # sinon arc sortant
        else:
            # pareil on ecrase avec le nouveau poids
            return self.ajouter_arcs_sortants(t, p, poids)
