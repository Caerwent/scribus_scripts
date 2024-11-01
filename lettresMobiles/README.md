# Activité d'apprentissage de lecture et d'écriture
Ce script utilise une liste de mots et d'images pour générer le matériel d'une activité d'écriture et de découpage de lettres pour former des mots. Il est adapté aux différents niveaux de classes de maternelle.

Le script utilise un fichier de modèle (lettresMobiles.sla), il peut être remplacé mais le script cherche un gabarit nommé ***grille_mots_ecole*** contenant un cadre d'image nommé ***ImageAlbum***.

![Modèle de carte au format Scribus](doc/modele_scribus.png)

Le script utilise également un fichier CSV, avec le point virgule comme séparateur, permettant de renseigner les informations pour les mots de l'activité.

La première ligne doit contenir le nom des colonnes qui sont ***Page***, ***Mot*** et ***Image***, puis chacune des lignes suivantes contiendra la valeur de chacune de ces colonnes pour chaque mot.

La page est un numéro qui indique sur quel page doit se trouver le mot, la deuxième colonne contient le mot lui-même et la troisième colonne le nom du fichier image.

 Par exemple :

> Page;Mot;Image
>
> 1;fulorin;img/fulorin.jpg
>
> 1;kanan;img/kanan.png
>
> 2;kaoter;img/kaoter.jpg

Il est également possible d'indiquer dans ce fichier une image d'album différente par page, dans ce cas il faudra ajouter une ligne spéciale pour chaque page en remplaçant le mot par le mot clé ***imageAlbum***.

 Par exemple :

> Page;Mot;Image
>
> 1;imageAlbum;img/album1.jpg
>
> 1;fulorin;img/fulorin.jpg
>
> 1;kanan;img/kanan.png
>
> 2;kaoter;img/kaoter.jpg

***Dans ce fichier CSV, le chemin dans le nom des images peut être en absolu ou en relatif, à partir de l'emplacement du fichier CSV.***

Il sera souvent préférable de mettre le nom en relatif par rapport au fichier CSV.

Le script permet de créer le fichier CSV en entrée à partir d'un dossier d'image qui restera à compléter manuellement. Le mot sera renseigné avec le nom du fichier image en remplaçant les caractères souligné (`_`) par un espace. Il ne restera donc qu'à compléter la page.

![Modèle de carte au format Scribus](doc/dialog_choice.png)

Lors du chargement d'un fichier CSV préalablement créé, une boîte de dialogue permet de choisir si l'image d'album est à choisir pour toutes les pages (qu'il y en ait une indiquée par page dans le fichier CSV ou non) et si oui, de choisir une image sur le disque.

Le script demande si l'alphabet breton doit être géré. Dans ce cas, les chaînes de caractères ***ch*** et ***c'h*** sont considérées comme une seule lettre.

![Modèle de carte au format Scribus](doc/dialog_bzh.png)

Ensuite le script demande à choisir le mode, qui correspond à un niveau de maternelle :
 - 1 : mot sous l'image + une ligne écriture + ligne collage capitales
 - 2 : mot sous l'image + une ligne écriture + ligne collage capitales + ligne collage minuscules
 - 3 : mot sous l'image + une ligne écriture + ligne collage minuscules + ligne collage cursif

![Modèle de carte au format Scribus](doc/dialog_mode.png)

Enfin le script demande le nombre d'élèves qui feront l'activité :

![Modèle de carte au format Scribus](doc/dialog_eleves.png)

La génération du document peut prendre un certain temps suivant le nombre de mots, le nombre d'élèves indiqué et la puissance de l'ordinateur. La barre de progression de Scribus (en bas à droite de la fenêtre principale) est mise à jour avec la progression de la génération du document.

La première partie du document généré contient les fiches d'activité remises à chaque élève, on y retrouve les mots sous forme de grille avec l'image qui l'illustre, le mot de référence et les lignes d'écriture ou de collage à remplir par l'élève.

Les mots sont placés sur la page indiquée dans le fichier CSV. Attention de ne pas dépasser 3 mots par page, sauf à avoir modifier le fichier modèle pour que l'entête prenne moins de place.

![Modèle de carte au format Scribus](doc/result1.png)

La seconde partie du document correspond aux lettres à découper puis à coller.

Elles sont regroupées par page, puis par élève (un changement de couleur permet d'identifier des paquets de lettres pour élève afin de faciliter la distribution). Chaque paquet contient les lettres pour les différentes lignes de collage dans un ordre aléatoire. Le placement des paquets est fait de façon à essayer de perdre le moins de place possible sur la feuille.

Exemple d'un arragengement de lettres :

![Modèle de carte au format Scribus](doc/result2.png)

Example d'un autre arrangement de lettres :

![Modèle de carte au format Scribus](doc/result3.png)

En cas de problème avec les polices utilisées par le script, ou si vous souhaitez les changer, il faut ouvrir le script avec un éditeur de texte et changer les lignes suivantes pour y remplacer le nom des polices:

> self.cFontRef = "Comic Sans MS Regular"
>
> self.cFont = "Arial Bold"
>
> self.cFontScript = "Belle Allure GS Gras"
>
> self.cFontSymbols = "DejaVu Sans Bold"

L'API Scribus ne permet pas actuellement de proposer une boîte de dialoge affichant la liste des polices disponibles mais cela devrait être le cas dans la prochaine version de Scribus.

La police *Belle Allure GS Gras* peut être téléchargée ici : [https://fr.fonts2u.com/belle-allure-gs-gras.policet](https://fr.fonts2u.com/belle-allure-gs-gras.police)
