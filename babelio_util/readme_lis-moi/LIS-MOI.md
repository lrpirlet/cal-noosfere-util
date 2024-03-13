# Le site de babelio

Le URL de nooSFere est <"https://www.babelio.com/" >.

## cal-babelio

Mon idée est de me permettre de télécharger les informations relatives à un
volume du livre dans calibre

## cal-babelio-util

Avant de télécharger de nouvelles informations à propos d'un volume, il
peut être nécessaire de supprimer plusieurs champs existants tels que Série,
ISBN, éditeur, collection, coll_srl... en effet, calibre ne permet pas d'effacer
un champ à partir d'un metadata source plugin (Calibre combine les informations
dans ces champs)

L'intention de cal-babelio-util est de pouvoir choisir le volume de l'ouvrage
et de préparer l'enregistrement de nouvelles informations.

Ensuite cal-babelio peut être exécuté pour remplir calibre avec une information correcte.
