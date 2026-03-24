
Simulation de Réseau de Petri

-------------------------------------------------

Groupe 3 | ID4 | 2025-2026

Théorie des Graphes -- Semestre 1

Prof. Zaouche Djaouida

-------------------------------------------------

Etudiantes :

Hadil Maadi -- maadihadil@cy-tech.fr
Maeva Rechak-Lambert -- rechaklamb@cy-tech.fr
Rafaelle Bueno -- buenorafae@cy-tech.fr
Tiphaine Brun -- bruntiphai@cy-tech.fr
Natasha Litherland -- litherland@cy-tech.fr

-------------------------------------------------

Description du Projet :

L'objectif de ce projet est de simuler un réseau de pétri, dans lequel l'utilisateur peut rajouter et modifier des places, des transitions et des arcs entre eux.

Pour citer l'énoncé de Prof. Zaouche Djaouida,
"Dans ce projet, il vous est demandé de concevoir et implémenter un éditeur et analyseur de
réseaux de Petri, implémenté en Python, avec un rendu documenté en LATEX. Le projet couvre :
• l’édition (graphique ou textuel) de réseaux de Petri classiques ;
• la génération et l’exploration de l’espace d’états (graphe d’états) ;
• la vérification de propriétés classiques (deadlock, vivacité, bornitude, invariants, etc.) ;
• une extension pour réseaux de Petri colorés (CPN) et leur gestion (types, expressions,
couleurs) ;"

Nous avons fait l'interface avec tkinter car nous ne maitrisons pas React et tkinter nous paraissait être la librairie la plus adaptée. Au niveau de l'UI, nous tenions à avoir quelque chose de visuel car on voulait que ce soit bien compréhensible et agréable pour l'utilisateur.

-------------------------------------------------

Comment lancer le Projet :

Il faut run le fichier main.py. Une fenêtre devrait s'ouvrir.

Pour les utilisateurs de Mac, faire attention de ne pas utiliser la version de Python proposée par défaut car elle utilise souvent une ancienne version de tkinter qui pose soucis.

Afin de pouvoir exporter en .png, il faut à tout prix avoir installé graphviz. Cela peut être fait avec la commande "pip install graphviz" dans VScode.