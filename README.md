### WebminingCraft
Contexte:
Il existe à ce jour plusieurs sites de configuration sur mesure d'ordinateurs et de benchmark de leurs composants. Les données sur lesquelles reposent ces services ne sont pas toujours mises à jour en temps réel ce qui va à l'encontre même de la pertinance de leurs recommendations aux utilisateurs. Notre API permettra de répondre aux mêmes besoins utilisateur de manière centralisée et au travers d'une interface utilisateur simplifiée, tout en garantissant l'exactitude et l'exaustivité des données renvoyées à l'utilisateur (compatiblité technique, prix actuels...). 

A faire:
- KVER revoir les coefficiants d'attribution des budgets
- KVER refaire scrap des casing
- ANTO data processing (tokenisation...)
- ANTO optimisation du code
- ANTO méthode de close match
- ANTO optimisation des combinaisons de composants
- KVER option de filtrage sur le frontend (GB de stockage,  marque de composants...)

Contraintes:
- disponibilité continues des données
- données en temps réél

Done:
- Sélection contraintes pre-processing(IU) : res, prix, performance (FPS)
- Scraping de configurations (composants, prix…). (Scrapy + squedualer)
- Sélection d’une configuration selon contraintes
- Vérification compatibilié technique à l’aide de règles (sous-ensembles de composants, par ex: carte mère/processeur)
- Scraping des composants chez différents fournisseurs  (TopReise) : prix, fournisseur
- Réponse à l’utilisateur (configuration sélectionnée, prix, URL vers fournisseurs..)
- scrapper user benchmark
- refactor les csv pour ne garder que les modèles génériques de certains composants tels que les cartes graphiques pour réduire la dimensionnalité
- réadapter les requêtes scrapy en conséquence

Decision:
- filtrer les composants des listes de benchmark des 3 dernières générations
- retirer la notion de résolution et la performance dans les contraintes utilisateurs, trop compliqué à définir
- ne pas utiliser la loi Amdahl car ne permet pas de trouver la meilleur combinaison CPU GPU, seulement le meilleur GPU pour un CPU donné
- pas réussi à scrapper les données du benchmark Heaven de Urigine
- utiliser python-Levenshtein pour merger les csv de produits et leur caractéristiques
- regrouper les cg par modèle car les benchmarks ne diffèrent que peu

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