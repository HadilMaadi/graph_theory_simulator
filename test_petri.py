from reseau_de_petri import ReseauPetri
from petri_propriete import PetriPropriete


def marquage_str(net: ReseauPetri) -> str:
    lignes = []
    for p in net.places:
        jetons = net.marquage.get(p, [])
        lignes.append(f"{p} : {jetons} (nb={len(jetons)})")
    return "\n".join(lignes)


# ------------------------------------------------------------------------------------------------------------------------------------------------------

# TEST AVEC COULEURS



print("TEST RÉSEAU DE PÉTRI AVEC COULEURS")

# créations et tir
print("CRÉATION ET TIR")

net = ReseauPetri()

print("\nAjout des places")
print("P1 :", net.ajouter_place("P1", ["rouge", "rouge"]))
print("P2 :", net.ajouter_place("P2", []))
print("P3 :", net.ajouter_place("P3", []))

print("\nAjout de la transition")
print("T1 :", net.ajouter_transition("T1"))

print("\nAjout des arcs")
print("P1 -> T1 :", net.ajouter_arcs_entrants("T1", "P1", {"rouge": 2}))
print("T1 -> P2 :", net.ajouter_arcs_sortants("T1", "P2", {"bleu": 1}))
print("T1 -> P3 :", net.ajouter_arcs_sortants("T1", "P3", {"vert": 1}))

print("\nÉtat initial")
print("Places :", net.places)
print("Transitions :", net.transitions)
print(marquage_str(net))

print("\nT1 activable ?", net.est_tirable("T1"))
print("Transitions possibles :", net.transitions_disponibles())

print("\nTir de T1")
net.appliquer_changement("T1")
print(marquage_str(net))


# modifications
print("\n\nMODIFICATIONS")

print("\nModification de la place P1")
print(net.modifier_place("P1", "P_debut", ["rouge", "bleu", "bleu"]))
print("Places :", net.places)
print(marquage_str(net))

print("\nModification du poids de l’arc T1 -> P2")
print(net.modifier_poids_arc("T1", "P2", "sortant", {"bleu": 2}))
print("Arcs sortants :", net.arcs_sortants)

print("\nRenommage de la transition T1")
print(net.modifier_nom_transition("T1", "T2"))
print("Transitions :", net.transitions)


# suppressions
print("\n\nSUPPRESSIONS")

print("\nSuppression de l’arc T2 -> P3")
print(net.supprimer_arc("T2", "P3", "sortant"))
print("Arcs sortants :", net.arcs_sortants)

print("\nSuppression de la transition T2")
print(net.supprimer_transition("T2"))
print("Transitions :", net.transitions)

print("\nSuppression de la place P2")
print(net.supprimer_place("P2"))
print("Places :", net.places)
print(marquage_str(net))


# invariance par couleur
print("\n\nINVARIANCE PAR COULEUR")

net_inv = ReseauPetri()
net_inv.ajouter_place("P1", ["rouge", "rouge"])
net_inv.ajouter_place("P2", [])
net_inv.ajouter_place("P3", [])
net_inv.ajouter_transition("T1")
net_inv.ajouter_arcs_entrants("T1", "P1", {"rouge": 2})
net_inv.ajouter_arcs_sortants("T1", "P2", {"bleu": 1})
net_inv.ajouter_arcs_sortants("T1", "P3", {"vert": 1})

avant = net_inv.compteur_jeton_par_couleur()
net_inv.appliquer_changement("T1")
apres = net_inv.compteur_jeton_par_couleur()

print("Avant :", avant)
print("Après :", apres)

print("Rouge :", avant.get("rouge", 0), "->", apres.get("rouge", 0))
print("Bleu  :", avant.get("bleu", 0), "->", apres.get("bleu", 0))
print("Vert  :", avant.get("vert", 0), "->", apres.get("vert", 0))


#BFS/DFS/bornitude/blocage
print("\n\nBFS/DFS/BORNITUDE/BLOCAGE")

net_seq = ReseauPetri()
net_seq.ajouter_place("A", ["jaune"])
net_seq.ajouter_place("B", [])
net_seq.ajouter_transition("T_AB")
net_seq.ajouter_transition("T_BA")
net_seq.ajouter_arcs_entrants("T_AB", "A", {"jaune": 1})
net_seq.ajouter_arcs_sortants("T_AB", "B", {"jaune": 1})
net_seq.ajouter_arcs_entrants("T_BA", "B", {"jaune": 1})
net_seq.ajouter_arcs_sortants("T_BA", "A", {"jaune": 1})

analyse = PetriPropriete(net_seq)

etats_bfs, graphe_bfs = analyse.analyser_espace_etats(mode="largeur")
print("\nBFS : nombre d’états =", len(etats_bfs))
print("BFS : nombre de transitions =", sum(len(v) for v in graphe_bfs.values()))

etats_dfs, graphe_dfs = analyse.analyser_espace_etats(mode="profondeur")
print("\nDFS : nombre d’états =", len(etats_dfs))
print("DFS : nombre de transitions =", sum(len(v) for v in graphe_dfs.values()))

max_A = 0
max_B = 0
for cle in etats_bfs:
    marq = etats_bfs[cle]
    if len(marq.get("A", [])) > max_A:
        max_A = len(marq.get("A", []))
    if len(marq.get("B", [])) > max_B:
        max_B = len(marq.get("B", []))

print("\nBornitude observée :")
print("Nombre max de jetons dans A :", max_A)
print("Nombre max de jetons dans B :", max_B)

blocages = 0
for e in graphe_bfs:
    if len(graphe_bfs[e]) == 0:
        blocages += 1

print("\nNombre d’états bloqués :", blocages)


# vivacité
print("\n\nVIVACITÉ")
print("Réseau vivant :", analyse.vivacite())

print("\nFIN DES TESTS\n")




# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# TEST SANS COULEURS






print("TEST RÉSEAU DE PÉTRI (SANS COULEURS):")

print("CRÉATION ET TIR ")

net = ReseauPetri()

print("\nAjout des places")
print("P1 :", net.ajouter_place("P1", ["noir", "noir"]))
print("P2 :", net.ajouter_place("P2", []))
print("P3 :", net.ajouter_place("P3", []))

print("\nAjout de la transition")
print("T1 :", net.ajouter_transition("T1"))

print("\nAjout des arcs")
print("P1 -> T1 :", net.ajouter_arcs_entrants("T1", "P1", {"noir": 2}))
print("T1 -> P2 :", net.ajouter_arcs_sortants("T1", "P2", {"noir": 1}))
print("T1 -> P3 :", net.ajouter_arcs_sortants("T1", "P3", {"noir": 1}))

print("\nÉtat initial")
print("Places :", net.places)
print("Transitions :", net.transitions)
print(marquage_str(net))

print("\nT1 activable ?", net.est_tirable("T1"))
print("Transitions possibles :", net.transitions_disponibles())

print("\nTir de T1")
net.appliquer_changement("T1")
print(marquage_str(net))


# modifications
print("\n\nMODIFICATIONS")

print("\nModification de la place P1")
print(net.modifier_place("P1", "P_debut", ["noir", "noir", "noir"]))
print("Places :", net.places)
print(marquage_str(net))

print("\nModification du poids de l’arc T1 -> P2")
print(net.modifier_poids_arc("T1", "P2", "sortant", {"noir": 2}))
print("Arcs sortants :", net.arcs_sortants)

print("\nRenommage de la transition T1")
print(net.modifier_nom_transition("T1", "T2"))
print("Transitions :", net.transitions)


#suppressions
print("\n\nSUPPRESSIONS")

print("\nSuppression de l’arc T2 -> P3")
print(net.supprimer_arc("T2", "P3", "sortant"))
print("Arcs sortants :", net.arcs_sortants)

print("\nSuppression de la transition T2")
print(net.supprimer_transition("T2"))
print("Transitions :", net.transitions)

print("\nSuppression de la place P2")
print(net.supprimer_place("P2"))
print("Places :", net.places)
print(marquage_str(net))


# invariance
print("\n\nINVARIANCE (TOTAL JETONS)")

net_inv = ReseauPetri()
net_inv.ajouter_place("P1", ["noir", "noir"])
net_inv.ajouter_place("P2", [])
net_inv.ajouter_place("P3", [])
net_inv.ajouter_transition("T1")
net_inv.ajouter_arcs_entrants("T1", "P1", {"noir": 2})
net_inv.ajouter_arcs_sortants("T1", "P2", {"noir": 1})
net_inv.ajouter_arcs_sortants("T1", "P3", {"noir": 1})

total_avant = 0
total_avant = total_avant + len(net_inv.marquage.get("P1", []))
total_avant = total_avant + len(net_inv.marquage.get("P2", []))
total_avant = total_avant + len(net_inv.marquage.get("P3", []))

net_inv.appliquer_changement("T1")

total_apres = 0
total_apres = total_apres + len(net_inv.marquage.get("P1", []))
total_apres = total_apres + len(net_inv.marquage.get("P2", []))
total_apres = total_apres + len(net_inv.marquage.get("P3", []))

print("Total avant :", total_avant)
print("Total après :", total_apres)
print("Invariant total ?", (total_avant == total_apres))


# BFS/DFS/bornitude/blocage 
print("\n\nBFS/DFS/BORNITUDE/BLOCAGE")

net_seq = ReseauPetri()
net_seq.ajouter_place("A", ["noir"])
net_seq.ajouter_place("B", [])
net_seq.ajouter_transition("T_AB")
net_seq.ajouter_transition("T_BA")
net_seq.ajouter_arcs_entrants("T_AB", "A", {"noir": 1})
net_seq.ajouter_arcs_sortants("T_AB", "B", {"noir": 1})
net_seq.ajouter_arcs_entrants("T_BA", "B", {"noir": 1})
net_seq.ajouter_arcs_sortants("T_BA", "A", {"noir": 1})

analyse = PetriPropriete(net_seq)

etats_bfs, graphe_bfs = analyse.analyser_espace_etats(mode="largeur")
print("\nBFS : nombre d’états =", len(etats_bfs))
print("BFS : nombre de transitions =", sum(len(v) for v in graphe_bfs.values()))

etats_dfs, graphe_dfs = analyse.analyser_espace_etats(mode="profondeur")
print("\nDFS : nombre d’états =", len(etats_dfs))
print("DFS : nombre de transitions =", sum(len(v) for v in graphe_dfs.values()))

max_A = 0
max_B = 0
for cle in etats_bfs:
    marq = etats_bfs[cle]
    if len(marq.get("A", [])) > max_A:
        max_A = len(marq.get("A", []))
    if len(marq.get("B", [])) > max_B:
        max_B = len(marq.get("B", []))

print("\nBornitude observée :")
print("Nombre max de jetons dans A :", max_A)
print("Nombre max de jetons dans B :", max_B)

blocages = 0
for e in graphe_bfs:
    if len(graphe_bfs[e]) == 0:
        blocages += 1

print("\nNombre d’états bloqués :", blocages)


# vivacité
print("\n\nVIVACITÉ")
print("Réseau vivant :", analyse.vivacite())

print("\nFIN DES TESTS\n")
