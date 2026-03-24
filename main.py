# main.py

# on a besoin de tkinter pour afficher la fenetre a l'ecran
import tkinter as tk

# on importe la classe reseau qui est dans le fichié juste a coté
from reseau_de_petri import ReseauPetri

# on recupere l'interface graphique depuis le fichier petri_gui.py
# correction : on importe direct sans mettre le nom du dossier avant sinon sa plante
from petri_gui import PetriGUI

# ce bloc sert a executer le code que si on lance ce fichier la
if __name__ == "__main__":
    
    # on instanci un reseau vide pour commencer proprement
    reseau = ReseauPetri()

    # on cree la fenetre principale qui va contenir notre application
    fenetre = tk.Tk()
    
    # on regle la taille pour que l'utilisateur ai de la place pour dessiner
    fenetre.geometry("1200x800")
    
    # on met un titre explicite en haut de la fenetre
    fenetre.title("Simulateur de Réseau de Pétri")
    
    # on lance la classe d'interface en lui donnant la fenetre et le reseau
    application = PetriGUI(fenetre, reseau)
    
    # on demare la boucle infinie pour que la fenetre reste affichée
    fenetre.mainloop()