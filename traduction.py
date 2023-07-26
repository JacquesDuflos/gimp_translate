#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gimpfu import *
import re
import HTMLParser

import os,sys

whereIAm=os.path.dirname(sys.argv[0]) # find location of executed file

sys.path.append(whereIAm) # add to Python path
from translate import Translator

class HTMLDecodeParser(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.result = ""

    def handle_data(self, data):
        self.result += data
        
        
def translate_text_layers(image, drawable, from_langue, to_langue):
    image.undo_group_start()
    
    translator = Translator(to_lang=to_langue, from_lang=from_langue)
    print("------------start--------------")
    pdb.gimp_message_set_handler(MESSAGE_BOX)
    
    # Recuperation du groupe de calques selectionne
    selected_layer = pdb.gimp_image_get_active_layer(image)
    
    # Récupération du groupe de calques "text-fr" s'il existe
    group_text = None
    group_name = "text-"+to_langue
    for layer in image.layers:
        if pdb.gimp_item_is_group(layer) and pdb.gimp_item_get_name(layer) == group_name:
            group_text = layer
            print ("------------groupe preexistant-------------")
            break

    if group_text is None:
        # Créer un groupe de calques nommé "text-fr" s'il n'existe pas
        group_text = pdb.gimp_layer_group_new(image)
        pdb.gimp_item_set_name(group_text, group_name)
        pdb.gimp_image_insert_layer(image, group_text, None, 0)
        print("----------------groupe créé-----------------")

    if pdb.gimp_item_is_group(selected_layer):
        print("----------layer is group-------------")
        layers = selected_layer.layers
        print (layers)
    elif pdb.gimp_item_is_text_layer(selected_layer):
        print("----------layer is text-------------")
        layers=[selected_layer]
        print (layers)
    else:
        print("--------Veuillez sélectionner un groupe de calques ou un calque de texte.----")
        gimp.message("Veuillez sélectionner un groupe de calques ou un calque de texte.")
        image.undo_group_end()
        return
        
    # Parcours de tous les calques du groupe
    print(layers)
    for layer in layers:
        print("------------for--------------")
        print (layer)
        # Vérification si le calque est de type texte
        if pdb.gimp_item_is_text_layer(layer):
            # Dupliquer le calque
            duplicate = pdb.gimp_layer_copy(layer, True)
		
            # Ajouter le calque duplique au groupe "text-fr"
            pdb.gimp_image_insert_layer(image, duplicate, group_text, 0)
            
            # Récupérer le contenu texte du calque dupliqué
            text = pdb.gimp_text_layer_get_text(duplicate)
            if text is None :
                print ("----------text had markup-------------")
                text = pdb.gimp_text_layer_get_markup(duplicate)
                # quitter les markups avec une RegEx
                text= re.sub(r"<.*?>", "", text)
		
            # essayer de traduir
            try:
                text = text.decode("utf-8")
                translated_text = translator.translate(text)
            except Exception as e:
                translated_text = "Erreur lors de la traduction : {}".format(e)
                print("Erreur lors de la traduction : {}".format(e))

            # vérifier s'il y a des caractères spéciaux html
			# translated_text="J'aime les bananes &amp; les oranges &#128512;" #pour tester
            if re.search(r"&[#\w]+;", translated_text):
                print("-----------caractères html---------------")
                # remplacer les caractères 
                parser = HTMLDecodeParser()
                parser.feed(translated_text)
                translated_text = parser.result
            # Mettre à jour le texte du calque dupliqué avec la traduction
            pdb.gimp_text_layer_set_text(duplicate, translated_text)
    # Actualisation de l'affichage de l'image
    pdb.gimp_displays_flush()
    pdb.gimp_message("fini")
    # restore stuff
    print(image)
    image.undo_group_end()

def translate_text_layers_quick (image, drawable):
    translate_text_layers(image, drawable, "fr", "es")


register(
    "python-fu-translate-text-layers",
    "Translate text layers from a language to another",
    "Translate text layers from a language to another",
    "Your Name",
    "Your Name",
    "2023",
    "<Image>/Filters/Language/Translate Text Layers...",
    "*",
    [
        #(PF_IMAGE,  'image',            'Image', None),
        (PF_STRING, 'from_langue',      'Translate from language','es'),
        (PF_STRING, 'to_langue',      'Translate to language ','fr')
    ],
    [],
    translate_text_layers)

register(
    "python-fu-translate-text-layers-quick",
    "Translate text layers from a language to another",
    "Translate text layers from a language to another",
    "Your Name",
    "Your Name",
    "2023",
    "<Image>/Filters/Language/Translate Text Layers",
    "*",
    [],
    [],
    translate_text_layers_quick)

main()

