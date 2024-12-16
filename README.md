
****MotClef****

   Le panneaux MotClef pour but de gérer l'exportation et l'itération d'un fichier selon ses différents mots clefs associés à des calques.
   
   Les calques liés aux mots cléfs peuvent être facilement affichés ou masqués depuis le panneaux.
    à la différence des Label de couleur, un calque peux posseder plusieurs mots cléf et donc appartenir à plusieurs groupes.
    
    
**INSTALLATION**
 
 * Télécharger les fichiers en .zip depuis git hub.
 * Dans Krita,=> Outils => Script => "installer une extention à partir d'un fichier"
 * selctionner le .zip téléchargé.
 * ça marche!

****Usage****


**Ajouter un mot clef**
 
les mot clef utilisés par ce gestionnaires sont simplement des mot écrit dans le nom du claque avec le séparateur **'/'**


   * ils peuvent être rajoutés à la main en écrivant directement '/monMotClef' dans le titre du calque, puis en cliquent sur "Rafraichir"
   * ou bien en passant par le champ texte "new word" présent dans le panneau. Ecrivez votre mot puis cliquez sur le bouton "+" à droite. Le mot clef sera automatiquement rajouté dans la liste et à tous les calques séléctionnés.


 **Actuellement, le boutons *"Rafraichir"* est necessaire pour mettre à jour la liste des mots si vous en rajoutez à la main ou si vous changez de documents (Work in progress)**
 

 **Le Gestionnaire**
 
   dans le panneau, chaque mot clef possède plusieurs actions : 
 
   * un radio bouton <i>solo</i> qui masque tous les calques utilisant d'autres mots clef, laissant uniquement celui ci visible
   * une checkBox pour afficher ou masquer les calques associés à ce mot clef
 
  **le mot clef en lui même.**
 
  il est possible de le modifier directement dans la boite texte. Dans ce cas là, toute les occurance du mot seront modifiées aussi.
        si vous changez manuellement le mot clef d'un calque, il sera considéré comme un nouveaux mot clef une fois la liste rafraichit.
 
   * le bouton "Ecrire" rajoutera le mot clef à <bo>tous les calques séléctionnés

   * le bouton "Effacer" effecera le mot celf de <bo>tous les calques séléctionnés</bo>. <br> si plus aucun calque ne possède ce mot clef, il serra retiré de la liste
 
 **Le mot OFF**
 
   Le mot clef */off* est un cas particulier pour les calques que vous ne voulez pas rendre visible lors de l'export
   	
 **les calques /off seront automatiquement masqué lors de l'exportation**
 
 Dans le gestionnaire, le mot *off* ne peut pas être modifié, et sera toujours présent dans la liste.
      Il peut être visible, ajouté ou retiré avec les boutons comme les autres mots clef mais ne possède pas de bouton <q>solo</q>
 
**L'exportation**

Le bouton *Exporter* active une nouvelle fenêtre  La liste de mots clef présent dans le document apparaît à nouveaux avec un seul bouton : ce sont les option d'itération du mot clef
Les options d'exportations ne concernent que les calques liés à des mots clefs. les calques ne comportant pas de mot clef seront soit visible, soit laissés en l'état au moment de l'export (voir *sho all other layer* )plus bas

 1) **Normal** :  exporte une version où seule les calques liés à ce mot clef seront visibles (les autres mots clef seront masqués)

 1) **Hide** :  Les claques lié à ce mot clés seront toujours masqués, pas d'itération de ce mot clef
 1) **Show** :  Les claques lié à ce mot clés seront toujours visibles, pas d'itération de ce mot clef
 1) **More Iteration** :  Pour chaque itération<q>Normale</q>, une version supplémentaire avec ce mot clef sera exporté.

   *Show all other layers**
    l'option force tous les autre calques (sans mots clef) à être affichés
   Export Folder
   de base, le chemin proposé est celui du document plus /export/  il est possible de changer le dossier avec le bouton dossier
