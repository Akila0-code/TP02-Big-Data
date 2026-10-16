TP02 – Traitement des Big Data avec Pandas et Dask

 Présentation du projet

Ce TP a pour objectif d'étudier différentes méthodes de traitement d'un grand volume de données à l'aide de Python, Pandas et Dask.

Le projet utilise un fichier CSV synthétique d'environ 6 Go contenant 49 300 000 lignes.

 Objectifs

Tester la lecture classique d'un grand fichier CSV avec Pandas.

Étudier le traitement par blocs avec Pandas Chunking.

Utiliser Dask pour le traitement de données volumineuses.

Comparer le temps d'exécution et la consommation mémoire des méthodes.

 Environnement de travail

Langage : Python

Bibliothèques : Pandas, Dask, psutil, Matplotlib

Format des données : CSV

Système d'exploitation : Windows

 Structure du projet

task1_oom_challenge.py : test de lecture classique et surveillance de la mémoire.

task2_chunking.py : traitement des données par blocs.

task3_dask.py : traitement avec Dask.

compare_results.py : comparaison des performances et génération des graphiques.

results/ : tableaux, rapports et graphiques des résultats.

Résultats expérimentaux

Le fichier traité contient 49 300 000 lignes et sa taille est d'environ 6,009 Go.

Méthode

Statut

Temps (s)

Mémoire maximale (MB)

Pandas classique

Non démarré : mémoire disponible insuffisante

N/A

N/A

Pandas Chunking

Terminé

115,41

78,28

Dask

Terminé

111,53

327,02

La lecture classique avec Pandas n'a pas été lancée, car les conditions de sécurité liées à la mémoire disponible n'étaient pas satisfaites.

Dask a terminé le traitement environ 3,88 secondes plus rapidement que Pandas Chunking. Cependant, sa consommation mémoire mesurée était plus élevée.

Pandas Chunking présente une consommation mémoire plus faible dans cette expérience.

 Graphiques

Les graphiques de comparaison sont disponibles dans le dossier results/ :

performance_time.png : comparaison du temps d'exécution.

performance_ram.png : comparaison de la consommation mémoire.

 Installation des dépendances

Installer les bibliothèques nécessaires avec la commande suivante :

pip install pandas "dask[dataframe]" psutil matplotlib

 Conclusion

Ce TP montre que le traitement par blocs avec Pandas et l'utilisation de Dask permettent de traiter un grand fichier CSV sans charger nécessairement l'ensemble des données en mémoire.

Dans cette expérience, Dask a obtenu le temps d'exécution le plus faible, tandis que Pandas Chunking a consommé moins de mémoire.

Le choix de la méthode dépend donc des ressources matérielles disponibles et des besoins du traitement.