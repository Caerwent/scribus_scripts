# Collection de scripts Scribus

Scribus ([https://www.scribus.net/](https://www.scribus.net/)) est un logiciel libre de P.A.O (Publication assistée par ordinateur).
Il permet de faire des mises en page complexes avec un rendu professionnel, les possibilités sont nombreuses, du magazine à l'affiche en passant par le flyer.

Scribus offre la possibilité de lancer des scripts écrits en python ce qui permet d'automatiser de nombreuses tâches fastidueuses à faire manuellement.

Cette collection rassemble quelques scripts utilisés pour la réalisation de documents utiles en classe de maternelle et sont adaptés pour gérer la langue bretonne.

Ces scripts sont écrits pour Scribus 1.5 ou 1.6. La version 1.7 à venir devrait offrir plus de possibilités et permettra d'améliorer certains d'entre eux.

 - [Liste d'étiquettes](etiquettes) : création d'une liste d'étiquettes de prénoms en utilisant plusieurs polices pour chaque prénom. Charge un fichier CSV contenant les informations utiles à la création de la liste.
 - [Flash cards](ScribusImagiers) : création d'une liste de flash cards à partir d'un modèle, d'une liste d'images et d'un fichier CSV. Le script permet également de créer un fichier CSV à partir d'un dossier d'image qui restera à compléter manuellement.
 - [Mots fléchés](crosswords) : Générateur de grille de mots fléchés à partir d'une liste de mots au format texte et d'images. Basé sur le travail de David Whitlock [https://github.com/riverrun/genxword](https://github.com/riverrun/genxword).
 - [Activité d'apprentissage de lecture et d'écriture](lettresMobiles) : Ce script utilise une liste de mots et d'images pour générer le matériel d'une activité d'écriture et de découpage de lettres pour former des mots. Il est adapté aux différents niveaux de classes de maternelle. Le script permet de créer le fichier CSV en entrée à partir d'un dossier d'image qui restera à compléter manuellement.
 - [Fiche de suivi d'atelier](fiches_suivi_ateliers) : Génère une fiche de suivi d'atelier à partir d'une liste d'images représentant les différentes activités de l'atelier.
 - Le scritp *SetImagesPaths.py* permet de remplacer le chemin de toutes les images du document ouvert.
 - Le script *center_all_images.py* tente de centrer toutes les images du document ouvert dans leur cadre d'image.
