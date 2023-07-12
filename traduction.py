#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gimpfu import *
from translate import Translator

def translate_text_layers(image, drawable):
    image.undo_group_start()
    
    translator = Translator(to_lang="fr", from_lang="es")
    print("------------start--------------")
    pdb.gimp_message_set_handler(MESSAGE_BOX)
    
    # Recuperation du groupe de calques selectionne
    group = pdb.gimp_image_get_active_layer(image)
    
    # Récupération du groupe de calques "text-fr" s'il existe
    group_text = None
    for layer in image.layers:
        if pdb.gimp_item_is_group(layer) and pdb.gimp_item_get_name(layer) == "text-fr":
            group_text = layer
            break

    if group_text is None:
        # Créer un groupe de calques nommé "text-fr" s'il n'existe pas
        group_text = pdb.gimp_layer_group_new(image)
        pdb.gimp_item_set_name(group_text, "text-fr")
        pdb.gimp_image_insert_layer(image, group_text, None, 0)

    if pdb.gimp_item_is_group(group):
        print("----------layer is group-------------")
        # Creer un groupe de calques nommé "text-fr"
        group_text = pdb.gimp_layer_group_new(image)
        pdb.gimp_item_set_name(group_text, "text-fr")
        pdb.gimp_image_insert_layer(image, group_text, None, 0)
        # Parcours de tous les calques du groupe
        for layer in group.layers:
            # Vérification si le calque est de type texte
            if pdb.gimp_item_is_text_layer(layer):
                # Dupliquer le calque
                duplicate = pdb.gimp_layer_copy(layer, True)
                
                # Ajouter le calque duplique au groupe "text-fr"
                pdb.gimp_image_insert_layer(image, duplicate, group_text, 0)
                
                # Récupérer le contenu texte du calque dupliqué
                text = pdb.gimp_text_layer_get_text(duplicate)
                
                # Vérifier si le texte n'est pas de type NoneType
                if text is not None:
                    # Traduire le texte en utilisant la bibliothèque translate
                    translated_text = translator.translate(text)
                else:
                    translated_text = "ERREUR TEXTE NON TRADUIT\n{}".format(text)

                
                # Mettre à jour le texte du calque dupliqué avec la traduction
                pdb.gimp_text_layer_set_text(duplicate, translated_text)

        # Actualisation de l'affichage de l'image
        pdb.gimp_displays_flush()
    elif pdb.gimp_item_is_text_layer(group):
        print("----------layer is text-------------")
        # Si le calque sélectionné est un calque de texte
        # Dupliquer le calque
        duplicate = pdb.gimp_layer_copy(group, True)
        
        # Ajouter le calque duplique au groupe "text-fr"
        pdb.gimp_image_insert_layer(image, duplicate, group_text, 0)
        
        # Récupérer le contenu texte du calque dupliqué
        text = pdb.gimp_text_layer_get_text(duplicate)
        
        # Traduire le texte en utilisant la bibliothèque translate
        translated_text = translator.translate(text)
        
        # Mettre à jour le texte du calque dupliqué avec la traduction
        pdb.gimp_text_layer_set_text(duplicate, translated_text)
    else:
        print("--------Veuillez sélectionner un groupe de calques ou un calque de texte.----")
        gimp.message("Veuillez sélectionner un groupe de calques ou un calque de texte.")
    
    pdb.gimp_message("fini")
    # restore stuff
    image.undo_group_end()

register(
    "python-fu-translate-text-layers",
    "Translate text layers from French to English",
    "Translate text layers from French to English",
    "Your Name",
    "Your Name",
    "2023",
    "<Image>/Filters/Language/Translate Text Layers",
    "*",
    [],
    [],
    translate_text_layers)

main()

