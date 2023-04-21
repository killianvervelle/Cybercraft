### WebminingCraft
Contexte:
Il existe à ce jour plusieurs sites de configuration sur mesure d'ordinateurs et de benchmark de leurs composants. Les données sur lesquelles reposent ces services ne sont pas toujours mises à jour en temps réel ce qui va à l'encontre même de la pertinance de leurs recommendations aux utilisateurs. Notre API permettra de répondre aux mêmes besoins utilisateur de manière centralisée et au travers d'une interface utilisateur simplifiée, tout en garantissant l'exactitude et l'exaustivité des données renvoyées à l'utilisateur (compatiblité technique, prix actuels...). 

A faire:
- Optimisation des contraintes par simplexe linéaire optimisisées (prix, performance (FPS). Utiliser les .csv de userbenchmark.com
- Vérification compatibilié technique à l’aide de règles (sous-ensembles de composants, par ex: carte mère/processeur)
- Scraping des composants chez différents fournisseurs  (TopReise) : prix, fournisseur
- Réponse à l’utilisateur (configuration sélectionnée, prix, URL vers fournisseurs..)
- scrapper user benchmark
- revoir les coefficiants d'attribution des budgets
- refaire scrap des casing

Contraintes:
- disponibilité continues des données
- données en temps réél

Done:
- Sélection contraintes pre-processing(IU) : res, prix, performance (FPS)
- Scraping de configurations (composants, prix…). (Scrapy + squedualer)
- Sélection d’une configuration selon contraintes

Decision:
- filtrer les composants des listes de benchmark des 4 dernières générations
- retirer la notion de résolution et chercher à optimiser la performance théorique en fonction du coût. 
- ne pas utiliser la loi Amdahl car ne permet pas de trouver la meilleur combinaison CPU GPU, seulement le meilleur GPU pour un CPU donné
- pas réussi à scrapper les données du benchmark Heaven de Urigine
- utiliser python-Levenshtein pour merger les csv de produits et leur caractéristiques

Table des compatibilité:
- mb/boitier (dim)
- gpu/boitier (dim)
- ram/mb (type)
- alim/gpu (puissance)
- mb/cpu
- venti/boitier (dim et water)

Caractéristiques écartées:
- type de PIN du PSU
- consommation exacte totale du build
- nombre de slot sur carte mère pour RAM
- capacité du SSD, pris du standard > 500 go