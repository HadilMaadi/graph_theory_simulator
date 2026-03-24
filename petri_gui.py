# petri_gui_complexe.py
# on a bessoin de math pour les calculs de trigo
import math
# on importe la bibliotheque graphique standard
import tkinter as tk
# on recupere les widgets un peu plus jolis et les boites de dialogue
from tkinter import ttk, messagebox, simpledialog, filedialog
# on a besoin de la classe du reseau quon a fait avant
from reseau_de_petri import ReseauPetri

# on essaye de charger le module d'analyse
# si il est pas la on fait comme si de rien n'etait
try:
    from petri_propriete import PetriPropriete 
# si l'import plante on definit la variable a rien
except ImportError:
    PetriPropriete = None

# on tente d'importer la fonction de sauvegarde json
# c'est mieux si elle existe mais pas obligatoire
try:
    from json_sauv_import import enregistrer_reseau_petri 
# en cas d'erreur on met la fonction a none
except Exception:
    enregistrer_reseau_petri = None

# on defini le rayon des cercles pour les places
RAYON_PLACE = 30
# on defini la demi largeur des rectangles de transition
LARGEUR_TRANS = 12
# on defini la demi hauteur des transitions
HAUTEUR_TRANS = 28
# on limite le nombre de points a afficher pour pas faire lagger
MAX_JETONS_VISUELS = 28

# un dictionnaire pour mapé les noms francais vers l'anglais de tk
COULEURS = {
    "rouge": "red", "bleu": "blue", "vert": "green", "jaune": "gold", "noir": "black",
    "blanc": "white", "orange": "orange", "rose": "hot pink", "violet": "purple",
    "gris": "gray", "marron": "saddle brown", "turquoise": "turquoise", "cyan": "cyan",
}

# cette fonction sert a nettoyer le nom de la couleur entré
def normaliser_couleur(s):
    # si la chaine est vide on renvoi rien du tout
    if not s: return ""
    # on enleve les espaces inutiles autour
    s = s.strip()
    # on met tout en minuscule pour comparer facilement
    minuscule = s.lower()
    # si sa commence par un diese c'est surement du hexa
    if minuscule.startswith("#") and len(minuscule) in (4, 7):
        # on retourne le code hexa tel quel
        return minuscule
    # sinon on regarde si on connait le nom dans notre dico
    return COULEURS.get(minuscule, s)

# on analyse la chaine de caractere pour trouver les poids des arcs
def analyser_poids_arc(s):
    # on converti en string et on nettoie
    s = str(s).strip()
    # si y a rien on renvoi un dico vide
    if not s: return {}
    # si c'est juste un nombre on considere que c'est des jetons noirs
    if s.isdigit():
        # on transforme le texte en entier
        n = int(s)
        # on renvoi le dico avec la couleur par defaut
        return {"noir": n} if n > 0 else {}
    
    # on prepare le resultat final
    resultat = {}
    # on decoupe la chaine par les virgules pour avoir chaque couleur
    parties = s.split(",")
    # on boucle sur chaque partie trouvée
    for p in parties:
        # on nettoie la partie
        p = p.strip()
        # si la partie n'est pas vide on traite
        if p:
            # il faut qu'il y ait deux points pour separer couleur et nombre
            if ":" not in p:
                # on leve une erreur pour prevenir l'utilisateur
                raise ValueError("faut mettre couleur:quantité")
            # on separe la chaine en deux morceaux max
            morceaux = p.split(":", 1)
            # le premier morceau c'est la couleur
            c = morceaux[0].strip()
            # le deuxieme morceau c'est la quantité
            q = morceaux[1].strip()
            
            # on essaye de convertir la quantité en entier
            try:
                val_q = int(q)
            # si sa marche pas on met une valeur negative pour declencher l'erreur
            except:
                val_q = -1
                
            # on verifie que la quantité est positive
            if val_q <= 0:
                # sinon on rale parce que c pas possible
                raise ValueError("quantité invalide")
            
            # on stocke le resultat en minuscule
            resultat[c.lower()] = val_q
    # on retourne le dictionnaire completé
    return resultat

# fonction pour transformer le dico de poids en texte affichable
def etiquette_poids(dico):
    # on prepare une liste pour stocker les morceaux de texte
    liste = []
    # on parcoure le dictionnaire
    for c, n in dico.items():
        # on formate joliment couleur:nombre
        liste.append(f"{c}:{n}")
    # on relie tout avec des virgules
    return ",".join(liste)

# on analyse la chaine pour creer la liste des jetons initiaux
def analyser_jetons(s):
    # on nettoie l'entree
    s = str(s).strip()
    # si c vide on renvoi une liste vide
    if not s: return []
    # si c juste un chiffre on met autant de jetons noirs
    if s.isdigit():
        # on converti en entier
        nb = int(s)
        # on fait une liste vide
        l = []
        # on boucle le nombre de fois demandé
        for i in range(nb):
            # on ajoute un jeton noir a la liste
            l.append("noir")
        # on retourne la liste remplie
        return l
        
    # si on trouve des deux points on utilise la logique des poids
    if ":" in s:
        # on appel la fonction qu'on a deja ecrite
        poids = analyser_poids_arc(s)
        # on prepare la liste
        l = []
        # pour chaque couleur et sa quantité
        for c, n in poids.items():
            # on ajoute n fois la couleur c
            for k in range(n):
                l.append(c)
        # on retourne la liste
        return l
        
    # sinon on suppose que c une liste separée par virgules genre rouge,bleu
    l = []
    # on coupe la chaine
    parties = s.split(",")
    # on regarde chaque element
    for p in parties:
        # on nettoie
        p = p.strip()
        # si il reste quelque chose
        if p:
            # on l'ajoute en minuscule
            l.append(p.lower())
    # on retourne la liste finale
    return l


# la classe principale pour l'interface graphique
class PetriGUI:
    # le constructeur qui initialise tout le bazar
    def __init__(self, fenetre, reseau):
        self.positions = {}
        # on sauvegarde la reference a la fenetre principale
        self.fenetre = fenetre
        # on sauvegarde la reference au reseau de petri
        self.reseau_petri = reseau
        # on change le titre de la fenetre
        self.fenetre.title("Réseau de Pétri – GUI")

        # variable tk pour savoir dans quel mode on est (selection par defaut)
        self.mode = tk.StringVar(value="selection") 
        # variable pour retenir le premier noeud cliqué lors de la creation d'arc
        self.source_arc = None 
        # dictionnaire pour stocker les infos graphiques (coords, id, etc)
        self.noeuds_graphiques = {} 
        # liste pour stocker les arcs graphiques
        self.arcs_graphiques = []
        
        
        # variable pour stocker l'etat de reference des invariants
        self.ref_invariant = None 

        # on lance la construction de l'interface
        self._construire_interface()
        # on dessine le reseau une premiere fois (probablement vide)
        self._dessiner_tout()

    # fonction pour creer tous les widgets
    def _construire_interface(self):
        # on cree un conteneur pour la barre d'outils en haut
        conteneur_barre = ttk.Frame(self.fenetre)
        # on l'affiche en haut et on prend toute la largeur
        conteneur_barre.pack(side=tk.TOP, fill=tk.X)

        # on cree une frame interne pour centrer les boutons
        barre = ttk.Frame(conteneur_barre)
        # on l'affiche au centre avec un peu d'espace vertical
        barre.pack(anchor="center", pady=5)

        # petite fonction interne pour changer le mode et le message d'aide
        def changer_mode(m, txt):
            # on met a jour la variable de mode
            self.mode.set(m)
            # on reset la source de l'arc au cas ou on change d'avis
            self.source_arc = None 
            # on met a jour le texte en bas de la fenetre
            self.status.config(text=txt)

        # bouton pour ajouter une place
        ttk.Button(barre, text="+ Place", command=lambda: changer_mode("place", "Clic pour ajouter.")).pack(side=tk.LEFT, padx=3)
        # bouton pour ajouter une transition
        ttk.Button(barre, text="+ Transition", command=lambda: changer_mode("transition", "Clic pour ajouter.")).pack(side=tk.LEFT, padx=3)
        # bouton pour creer un arc
        ttk.Button(barre, text="+ Arc", command=lambda: changer_mode("arc", "Clic Source puis Destination.")).pack(side=tk.LEFT, padx=3)
        
        # separateur vertical pour faire joli
        ttk.Separator(barre, orient="vertical").pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # bouton pour passer en mode tir de transition
        ttk.Button(barre, text="Tir", command=lambda: changer_mode("tir", "Clic sur transition verte.")).pack(side=tk.LEFT, padx=3)
        # bouton pour modifier les objets existants
        ttk.Button(barre, text="Modifier", command=lambda: changer_mode("edition", "Clic sur objet.")).pack(side=tk.LEFT, padx=3)
        # bouton pour supprimer des trucs
        ttk.Button(barre, text="Supprimer", command=lambda: changer_mode("suppression", "Clic sur objet.")).pack(side=tk.LEFT, padx=3)

        # encore un separateur
        ttk.Separator(barre, orient="vertical").pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # bouton pour verifier ce qui est activable
        ttk.Button(barre, text="Check", command=self.check_activable).pack(side=tk.LEFT, padx=3)
        # bouton pour verifier les invariants de places
        ttk.Button(barre, text="Invariants", command=self.verif_invariant).pack(side=tk.LEFT, padx=3)
        
        # le bouton pour exporter en image png
        ttk.Button(barre, text="Export PNG", command=self.export_png).pack(side=tk.LEFT, padx=3)

        # dernier separateur
        ttk.Separator(barre, orient="vertical").pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # bouton pour tout effacer et recommencer
        ttk.Button(barre, text="Nouveau", command=self.reset_reseau).pack(side=tk.LEFT, padx=3)
        
        # fonction de secours si le module json est pas la
        def pas_de_sauv():
            # on affiche une erreur a l'utilisateur
            messagebox.showerror("Erreur", "Module JSON pas trouvé.")
            
        # on choisi la commande a executer selon si le module existe
        cmd_sauv = self.sauver_json if enregistrer_reseau_petri else pas_de_sauv
        # bouton pour sauvegarder
        ttk.Button(barre, text="Sauver JSON", command=cmd_sauv).pack(side=tk.LEFT, padx=3)

        # on cree le canvas ou on va dessiner
        self.canevas = tk.Canvas(self.fenetre, bg="white", width=1000, height=700)
        # on l'affiche pour qu'il prenne toute la place restante
        self.canevas.pack(fill=tk.BOTH, expand=True)

        # etiquette en bas pour les messages d'etat
        self.status = ttk.Label(self.fenetre, text="Bienvenue.", anchor="w")
        # on la colle tout en bas
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        # on lie le clic gauche de la souris a notre fonction
        self.canevas.bind("<Button-1>", self.clic_gauche)
        # on lie le double clic gauche aussi
        self.canevas.bind("<Double-Button-1>", self.double_clic)

    # fonction utilitaire pour savoir sur quoi on a cliqué
    def trouver_objet_sous_souris(self):
        # on demande au canvas l'objet sous le curseur (tag 'current')
        elt = self.canevas.find_withtag("current")
        # si y a rien on retourne rien
        if not elt: return None, None
        
        # on recupere tous les tags de l'objet trouvé
        tags = self.canevas.gettags(elt[0])
        # on cherche nos tags specifiques
        for t in tags:
            # si c'est une place
            if t.startswith("PLACE:"): return "place", t.split(":", 1)[1]
            # si c'est une transition
            if t.startswith("TRANSITION:"): return "transition", t.split(":", 1)[1]
            # si c'est un arc (on stocke l'index)
            if t.startswith("ARC:"): return "arc", int(t.split(":", 1)[1])
        # si on trouve aucun tag connu
        return None, None

    # c'est ici qu'on gere le clic principal
    def clic_gauche(self, e):
        # on regarde sur quoi on a cliqué
        type_obj, nom_obj = self.trouver_objet_sous_souris()
        # on recupere le mode actuel
        mode = self.mode.get()

        # si on est en selection on fait rien pour l'instant
        if mode == "selection": return
        # si on veut creer une place
        if mode == "place": return self.creer_place(e.x, e.y)
        # si on veut creer une transition
        if mode == "transition": return self.creer_trans(e.x, e.y)
        # si on veut creer un arc
        if mode == "arc":
            # on verifi qu'on a cliqué sur un noeud valide
            if type_obj in ("place", "transition"): self.creer_arc(nom_obj)
            # on sort
            return
        # si on est en mode tir
        if mode == "tir":
            # on verifie que c'est une transition
            if type_obj == "transition": self.tirer(nom_obj)
            # on sort
            return
        # si on est en mode edition
        if mode == "edition":
            # selon le type d'objet on appel la bonne modif
            if type_obj == "place": self.modif_place(nom_obj)
            elif type_obj == "transition": self.modif_trans(nom_obj)
            elif type_obj == "arc": self.modif_arc(nom_obj)
            # on sort
            return
        # si on est en mode suppression
        if mode == "suppression":
            # selon le type on appel la suppression adéquate
            if type_obj == "place": self.supp_place(nom_obj)
            elif type_obj == "transition": self.supp_trans(nom_obj)
            elif type_obj == "arc": self.supp_arc(nom_obj)
            # on sort
            return

    # raccourci pour tirer rapidement
    def double_clic(self, _e):
        # on regarde sur quoi on clic
        type_obj, nom_obj = self.trouver_objet_sous_souris()
        # si c'est une transition on tire direct
        if type_obj == "transition": self.tirer(nom_obj)

    # --- fonctions de creation ---
    # pour creer une place a une position donnée
    def creer_place(self, x, y):
        # on demande le nom a l'utilisateur
        nom = simpledialog.askstring("Ajout", "Nom de la place :")
        # si il annule on arrete
        if not nom: return
        # on demande les jetons initiaux
        txt = simpledialog.askstring("Ajout", "Jetons (ex: rouge:2) :")
        # si il annule on arrete
        if txt is None: return
        # on essaye d'analyser le texte des jetons
        try:
            jetons = analyser_jetons(txt)
        # si y a une erreur on affiche une popup
        except Exception as e:
            return messagebox.showerror("Erreur", str(e))

        # on tente d'ajouter la place dans le modele
        if self.reseau_petri.ajouter_place(nom.strip(), jetons):
            self.positions[nom] = (x, y)
            # si sa marche on la dessine
            self._dessiner_place(nom.strip(), x, y)
            # et on met a jour l'affichage
            self.rafraichir()
        # si le nom existe deja
        else:
            # on rale
            messagebox.showerror("Erreur", "Nom deja pris je crois.")

    # pour creer une transition
    def creer_trans(self, x, y):
        # on demande le nom
        nom = simpledialog.askstring("Ajout", "Nom de la transition :")
        # si vide on quitte
        if not nom: return
        # on essaye de l'ajouter au modele
        if self.reseau_petri.ajouter_transition(nom.strip()):
            self.positions[nom] = (x, y)
            # on la dessine sur le canvas
            self._dessiner_trans(nom.strip(), x, y)
            # on met a jour
            self.rafraichir()
        # si erreur doublon
        else:
            # on previent l'utilisateur
            messagebox.showerror("Erreur", "Nom deja pris.")

    # pour creer un arc entre deux noeuds
    def creer_arc(self, objet_nom):
        # on recupere les infos graphiques de l'objet cliqué
        infos = self.noeuds_graphiques.get(objet_nom)
        # securité si pas trouvé
        if not infos: return
        # on note le type du noeud
        type_noeud = infos.get("type")

        # si c le premier clic (la source)
        if self.source_arc is None:
            # on memorise qui est la source
            self.source_arc = (objet_nom, type_noeud)
            # on change le message d'aide
            self.status.config(text=f"Source: '{objet_nom}'. Clic Destination.")
            # on attend le prochain clic
            return

        # si c le deuxieme clic (la destination)
        source_nom, source_type = self.source_arc
        dest_nom, dest_type = objet_nom, type_noeud
        # on reset la source pour la prochaine fois
        self.source_arc = None 
        # on remet le message normal
        self.status.config(text="Mode Arc.")

        # on interdit de relier un truc a lui meme
        if source_nom == dest_nom:
            # message d'info
            return messagebox.showinfo("Info", "Pas de boucle sur soi meme.")

        # on determine le sens de l'arc
        if source_type == "place" and dest_type == "transition":
            # arc entrant dans la transition
            sens, t_nom, p_nom = "entrant", dest_nom, source_nom
        elif source_type == "transition" and dest_type == "place":
            # arc sortant de la transition
            sens, t_nom, p_nom = "sortant", source_nom, dest_nom
        # si on relie deux trucs pareils c'est interdit
        else:
            # erreur explicite
            return messagebox.showerror("Erreur", "Faut relier Place et Transition.")

        # on demande le poids de l'arc
        txt = simpledialog.askstring("Ajout", "Poids (ex: 1) :")
        # si annulation on quitte
        if txt is None: return
        # on essaye de parser le poids
        try:
            poids = analyser_poids_arc(txt)
        # erreur de syntaxe
        except Exception as e:
            return messagebox.showerror("Erreur", str(e))

        # on ajoute l'arc dans le modele
        if sens == "entrant":
            # appel methode reseau
            ok = self.reseau_petri.ajouter_arcs_entrants(t_nom, p_nom, poids)
        else:
            # appel methode reseau
            ok = self.reseau_petri.ajouter_arcs_sortants(t_nom, p_nom, poids)

        # si l'ajout a marché
        if ok:
            # on dessine l'arc visuellement
            self._dessiner_arc(source_nom, dest_nom, sens, poids)
            # on rafraichit l'ecran
            self.rafraichir()
        # si echec
        else:
            # message d'erreur
            messagebox.showerror("Erreur", "Echec ajout arc.")

    # action de tirer une transition
    def tirer(self, nom):
        # on demande au modele si c'est possible
        if not self.reseau_petri.est_tirable(nom):
            # si non on affiche un warning
            return messagebox.showwarning("Bloqué", "Peut pas tirer.")
        # si oui on applique le changement d'etat
        self.reseau_petri.appliquer_changement(nom)
        # on redessine pour voir les jetons bouger
        self.rafraichir()

    # --- modifs ---
    # modifier une place existante
    def modif_place(self, nom):
        # on demande un nouveau nom
        nouveau = simpledialog.askstring("Modif", f"Nouveau nom pour '{nom}' :")
        # on nettoie la chaine
        if nouveau: nouveau = nouveau.strip()
        # ou on met a none
        else: nouveau = None
        
        # on demande les nouveaux jetons
        txt = simpledialog.askstring("Modif", "Nouveaux jetons (vide = rien changer) :")
        # on prepare la variable
        jetons = None
        # si y a du texte
        if txt and txt.strip():
            # on essaye d'analyser
            try: jetons = analyser_jetons(txt)
            # erreur de format
            except: return messagebox.showerror("Erreur", "Jetons pas bons")

        # on appel la modification dans le modele
        if self.reseau_petri.modifier_place(nom, nouveau, jetons):
            # si on a renomme on transfère la position
            if nouveau and nouveau != nom and nom in self.positions:
                self.positions[nouveau] = self.positions.pop(nom)
            self._dessiner_tout()


    # modifier une transition
    def modif_trans(self, nom):
        # on demande le nouveau nom
        nouveau = simpledialog.askstring("Modif", f"Nouveau nom pour '{nom}' :")
        # si on a un nom valide et que le modele accepte
        if nouveau and self.reseau_petri.modifier_nom_transition(nom, nouveau.strip()):
            new_name = nouveau.strip()
            # si on a renomme on transfère la position
            if new_name != nom and nom in self.positions:
                self.positions[new_name] = self.positions.pop(nom)
            self._dessiner_tout()


    # modifier un arc
    def modif_arc(self, idx):
        # verification de l'index
        if idx >= len(self.arcs_graphiques): return
        # on recupere l'arc visé
        arc = self.arcs_graphiques[idx]
        # on demande le nouveau poids
        txt = simpledialog.askstring("Modif", f"Poids actuel: {etiquette_poids(arc['poids'])}\nNouveau :")
        # si on a une reponse
        if txt:
            # bloc try pour les erreurs
            try:
                # on parse le poids
                p = analyser_poids_arc(txt)
                # on recupere source destination et type depuis l'objet graphique
                src, dst, type_arc = arc['source'], arc['destination'], arc['type_arc']
                
                # il faut remettre dans l'ordre pour le modele
                if type_arc == 'entrant':
                    # pour un arc entrant la destination est la transition
                    t = dst
                    # la source est la place
                    place = src
                else:
                    # pour un sortant c'est l'inverse
                    t = src
                    place = dst
                    
                # on appel la methode de modif du modele
                self.reseau_petri.modifier_poids_arc(t, place, type_arc, p)
                # on redessine tout pour etre sur
                self._dessiner_tout()
            # on gere l'erreur
            except Exception as e:
                # affichage erreur
                messagebox.showerror("Erreur", str(e))

    # --- suppressions ---
    # supprimer une place
    def supp_place(self, nom):
        # on demande confirmation
        if messagebox.askyesno("Supprimer", f"Supprimer '{nom}' ?"):
            # si le modele supprime bien
            if self.reseau_petri.supprimer_place(nom):
                # on redessine
                self._dessiner_tout()

    # supprimer une transition
    def supp_trans(self, nom):
        # confirmation utilisateur
        if messagebox.askyesno("Supprimer", f"Supprimer '{nom}' ?"):
            # action sur le modele
            if self.reseau_petri.supprimer_transition(nom):
                # refresh graphique
                self._dessiner_tout()

    # supprimer un arc
    def supp_arc(self, idx):
        # on verifie l'index et on demande confirmation
        if idx < len(self.arcs_graphiques) and messagebox.askyesno("Supprimer", "Supprimer cet arc ?"):
            # on chope l'arc
            arc = self.arcs_graphiques[idx]
            # on extrait les donnees
            src, dst, type_arc = arc['source'], arc['destination'], arc['type_arc']
            
            # logique pour retrouver qui est transition qui est place
            if type_arc == 'entrant':
                t = dst
                p = src
            else:
                t = src
                p = dst
                
            # appel suppression modele
            if self.reseau_petri.supprimer_arc(t, p, type_arc):
                # refresh total
                self._dessiner_tout()

    # --- checks ---
    # verification des transitions activables
    def check_activable(self):
        # on recupere la liste des transitions pretes
        t = self.reseau_petri.transitions_disponibles()
        # on formate le message
        msg = f"Activables : {', '.join(t)}" if t else "Rien activable."
        # on l'affiche
        messagebox.showinfo("Check", msg)

    # verification des invariants
    def verif_invariant(self):
        # on compte les jetons actuels par couleur
        actuel = self.reseau_petri.compteur_jeton_par_couleur()
        # si on a pas encore de reference
        if self.ref_invariant is None:
            # on defini l'etat actuel comme reference
            self.ref_invariant = actuel
            # on previent l'utilisateur
            messagebox.showinfo("Invariant", "Reference sauvegardee.")
            # et on s'arrete la
            return

        # on initialise le booleen de succes
        ok = True
        # liste pour le rapport
        lignes = []
        # on fusionne les cles des deux dicts pour rien oublier
        toutes_cle = list(self.ref_invariant.keys()) + list(actuel.keys())
        # on trie et on dedoublonne
        toutes_cle = sorted(list(set(toutes_cle)))
        
        # on compare chaque couleur
        for c in toutes_cle:
            # valeur avant
            avant = self.ref_invariant.get(c, 0)
            # valeur apres
            apres = actuel.get(c, 0)
            # si different
            if avant != apres:
                # l'invariant est brisé
                ok = False
                # marqueur textuel
                etat = "CHANGE"
            # si pareil
            else:
                etat = "OK"
            # on ajoute la ligne au rapport
            lignes.append(f"{c}: {avant} -> {apres} ({etat})")
        
        # on construit le message final
        msg = "\n".join(lignes)
        # on adapte le titre et l'icone
        if ok:
            titre = "Respecté"
            icone = "info"
        else:
            titre = "Brisé"
            icone = "warning"
            
        # on affiche le resultat et on propose de mettre a jour la ref
        if messagebox.askyesno(titre, f"{msg}\n\nUpdate reference ?", icon=icone):
            # on met a jour si demandé
            self.ref_invariant = actuel

    # export en image
    def export_png(self):
        # si on a pas pu importer le module au debut
        if PetriPropriete is None:
            # on affiche une erreur
            return messagebox.showerror("Erreur", "petri_propriete.py manquant.")
        
        # on demande ou sauver le fichier
        nom = filedialog.asksaveasfilename(title="Export PNG", defaultextension=".png", filetypes=[("PNG", "*.png")])
        # si annulation
        if not nom: return

        # bloc de sureté
        try:
            # on instancie l'analyseur
            analyseur = PetriPropriete(self.reseau_petri)
            # on lance l'export
            ok, res = analyseur.exporter_graphe_png(nom)
            # si reussite
            if ok:
                # message succes
                messagebox.showinfo("Succès", f"Sauvegardé la:\n{res}")
            # echec interne
            else:
                # message erreur
                messagebox.showerror("Erreur", res)
        # crash imprevu
        except Exception as e:
            # erreur critique
            messagebox.showerror("Erreur critique", str(e))

    def memoriser_positions(self):
        # sauvegarde les positions actuelles (celles visibles à l'écran)
        for nom, d in self.noeuds_graphiques.items():
            if "x" in d and "y" in d:
                self.positions[nom] = (d["x"], d["y"])


    # --- dessin ---
    # fonction pour tout redessiner de zero
    def _dessiner_tout(self):
        self.memoriser_positions()
        # on efface tout le canvas
        self.canevas.delete("all")
        # on vide nos dictionnaires graphiques
        self.noeuds_graphiques = {}
        self.arcs_graphiques = []
        # si le reseau est vide on fait rien
        if not self.reseau_petri.places and not self.reseau_petri.transitions: return

        # coordonnees de depart pour le placement auto
        x0, y0 = 100, 100
        # espacement entre les noeuds
        dx, dy = 130, 100
        
        # compteur pour la grille
        i = 0
        for p in self.reseau_petri.places:
            if p in self.positions:
                x, y = self.positions[p]
            else:
                x, y = x0 + (i%5)*dx, y0 + (i//5)*dy
                self.positions[p] = (x, y)
            self._dessiner_place(p, x, y)
            i += 1

        
        # on decale les transitions vers le bas
        y_t = y0 + 200
        j = 0
        for t in self.reseau_petri.transitions:
            if t in self.positions:
                x, y = self.positions[t]
            else:
                x, y = x0 + (j%5)*dx + 60, y_t + (j//5)*dy
                self.positions[t] = (x, y)
            self._dessiner_trans(t, x, y)
            j += 1


        # on parcoure les arcs entrants du reseau
        for t, srcs in self.reseau_petri.arcs_entrants.items():
            # pour chaque place source
            for p, w in srcs.items():
                # si les deux noeuds existent graphiquement on dessine
                if p in self.noeuds_graphiques and t in self.noeuds_graphiques: self._dessiner_arc(p, t, "entrant", w)
        # on parcoure les arcs sortants
        for t, dsts in self.reseau_petri.arcs_sortants.items():
            # pour chaque place destination
            for p, w in dsts.items():
                # on dessine l'arc
                if p in self.noeuds_graphiques and t in self.noeuds_graphiques: self._dessiner_arc(t, p, "sortant", w)
        
        # une fois tout posé on met a jour les couleurs et textes
        self.rafraichir()

    # dessiner une place specifique
    def _dessiner_place(self, nom, x, y):
        # on cree le tag unique pour tk
        tag = f"PLACE:{nom}"
        # on dessine le cercle
        self.canevas.create_oval(x-RAYON_PLACE, y-RAYON_PLACE, x+RAYON_PLACE, y+RAYON_PLACE, fill="white", outline="black", width=2, tags=(tag,))
        # on ecrit le nom en dessous
        self.canevas.create_text( x, y + RAYON_PLACE + 20, text=nom, font=("Arial", 10, "bold"),tags=(tag,))
        # on prepare le texte du compteur de jetons (vide pour l'instant)
        cpt = self.canevas.create_text(x, y-RAYON_PLACE-12, text="", tags=(tag,))
        # on enregistre les infos dans notre dictionnaire
        self.noeuds_graphiques[nom] = {"type": "place", "x": x, "y": y, "compteur": cpt, "dots": [], "forme": tag}
        # on force l'affichage des jetons
        self._rafraichir_place_visuel(nom)
        self.canevas.create_text(x, y + RAYON_PLACE + 20, text=nom, font=("Arial", 10, "bold"), fill="black",tags=(tag, "LABEL"))

    # dessiner une transition specifique
    def _dessiner_trans(self, nom, x, y):
        # tag unique
        tag = f"TRANSITION:{nom}"
        # on dessine le rectangle
        f = self.canevas.create_rectangle(x-LARGEUR_TRANS, y-HAUTEUR_TRANS, x+LARGEUR_TRANS, y+HAUTEUR_TRANS, fill="light gray", outline="black", width=2, tags=(tag,))
        # on stocke les infos
        self.noeuds_graphiques[nom] = {"type": "transition", "x": x, "y": y, "forme": f}
        # on met le nom en dessous
        self.canevas.create_text(x, y + HAUTEUR_TRANS + 12, text=nom,font=("Arial", 10, "bold"),fill="black",tags=(tag, "LABEL"))
        # force tous les labels au-dessus (noms places + transitions)
        self.canevas.tag_raise("LABEL")



    # dessiner un arc
    def _dessiner_arc(self, src, dst, type_arc, poids):
        # calcul des points d'attache precis
        x1, y1 = self._calcul_ancrage(src, dst)
        x2, y2 = self._calcul_ancrage(dst, src)
        
        # on dessine la ligne flechée
        # on ajoute un tag avec l'index pour retrouver l'arc apres
        idx_tag = f"ARC:{len(self.arcs_graphiques)}"
        self.canevas.create_line(
            x1, y1, x2, y2,
            arrow=tk.LAST,
            width=2,
            fill="black",
            tags=(idx_tag,)
            )

        
        # calcul du milieu pour le texte
        xm, ym = (x1+x2)/2, (y1+y2)/2
        # on affiche le poids en bleu
        t = self.canevas.create_text(xm, ym-10, text=etiquette_poids(poids), fill="blue", tags=(idx_tag,))
        
        # on ajoute a la liste des arcs
        self.arcs_graphiques.append({"source": src, "destination": dst, "type_arc": type_arc, "poids": poids, "etiquette": t})

    # calcule le point d'intersection entre le centre et le bord
    def _calcul_ancrage(self, n1, n2):
        # on recup les infos des deux noeuds
        d1 = self.noeuds_graphiques[n1]
        d2 = self.noeuds_graphiques[n2]
        # vecteur direction
        dx = d2["x"] - d1["x"]
        dy = d2["y"] - d1["y"]
        # distance euclidienne
        dist = math.sqrt(dx*dx + dy*dy)
        # evite la division par zero
        if dist == 0: dist = 1
        # on decale de 20 pixels vers la cible depuis le centre
        return d1["x"] + (dx/dist)*20, d1["y"] + (dy/dist)*20 

    # met a jour l'affichage des points dans une place
    def _rafraichir_place_visuel(self, nom):
        # on recupere les donnees graphiques
        d = self.noeuds_graphiques[nom]
        # on efface les anciens points
        for p in d["dots"]: self.canevas.delete(p)
        # on vide la liste
        d["dots"] = []
        # on recupere les vrais jetons du modele
        jetons = self.reseau_petri.marquage.get(nom, [])
        # on met a jour le compteur textuel
        self.canevas.itemconfig(d["compteur"], text=str(len(jetons)))
        
        # coordonnees du centre
        cx, cy = d["x"], d["y"]
        # on limite le nombre de points affichés
        liste = jetons[:MAX_JETONS_VISUELS]
        
        # boucle pour dessiner chaque jeton
        for i, couleur in enumerate(liste):
            # calcul d'angle en spirale
            angle = i * 2.4 
            # distance du centre qui augmente
            dist = 6 + 5 * math.sqrt(i) 
            
            # on empeche de sortir du cercle
            if dist > RAYON_PLACE - 6: 
                dist = RAYON_PLACE - 6
            
            # conversion polaire vers cartesien
            px = cx + math.cos(angle) * dist
            py = cy + math.sin(angle) * dist
            
            # on recupere la couleur tk
            c_tk = normaliser_couleur(couleur)
            # on cree le petit rond
            dot = self.canevas.create_oval(px-3, py-3, px+3, py+3, fill=c_tk, outline="")
            # on le garde en memoire
            d["dots"].append(dot)

    # met a jour tout l'etat visuel (couleurs transitions, textes)
    def rafraichir(self):
        # on parcoure tous les noeuds
        for nom, d in self.noeuds_graphiques.items():
            # si c une place on met a jour les jetons
            if d["type"] == "place": self._rafraichir_place_visuel(nom)
            # si c une transition on change sa couleur selon si elle est active
            elif d["type"] == "transition":
                # on demande au modele
                if self.reseau_petri.est_tirable(nom):
                    # vert pale si activable
                    c = "pale green"
                else:
                    # gris si inactif
                    c = "light gray"
                # application de la couleur
                self.canevas.itemconfig(d["forme"], fill=c)
        # on met a jour les textes des arcs (au cas ou modif)
        for arc in self.arcs_graphiques:
            self.canevas.itemconfig(arc["etiquette"], text=etiquette_poids(arc["poids"]))

    # pour remettre a zero
    def reset_reseau(self):
        # confirmation
        if messagebox.askyesno("Nouveau", "Effacer ?"):
            # on cree un nouveau reseau vide
            self.reseau_petri = ReseauPetri()
            # on efface le dessin
            self._dessiner_tout()
            # on oublie la reference invariant
            self.ref_invariant = None

    # sauvegarde json
    def sauver_json(self):
        # boite de dialogue pour choisir le fichier
        f = filedialog.asksaveasfilename(defaultextension=".json")
        # si un fichier est choisi on sauvegarde
        if f: enregistrer_reseau_petri(self.reseau_petri, f)
