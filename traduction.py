#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gimpfu import *
import re
import HTMLParser
import os,sys,json

whereIAm=os.path.dirname(sys.argv[0]) # find location of executed file
sys.path.append(whereIAm) # add to Python path
from translate import Translator



debug = True
def trace(s):
    if debug:
        print (s)

class HTMLDecodeParser(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.result = ""

    def handle_data(self, data):
        self.result += data
        
        
def translate_text_layers(image, drawable, from_langue, to_langue):
    image.undo_group_start()

    # Chemin du fichier JSON où on enregistre les valeurs par défaut
    json_file_name = os.path.basename(__file__).replace(".py", ".json")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(current_dir, "..","..", json_file_name)

    # Créer un dictionnaire avec les valeurs par défaut
    data = {
        "from_langue": from_langue,
        "to_langue": to_langue
    }

    # Sauvegarder les données dans le fichier JSON
    try:
        with open(json_file_path, "w") as json_file:
            json.dump(data, json_file)
        print("Données sauvegardées avec succès dans", json_file_path)
    except Exception as e:
        print("Erreur lors de la sauvegarde des données :", e)


    translator = Translator(to_lang=to_langue, from_lang=from_langue)
    trace("------------start--------------")
    
    # Recuperation du calque ou groupe de calques selectionne
    selected_layer = pdb.gimp_image_get_active_layer(image)
    
    # Récupération du groupe de calques "text-fr" s'il existe
    group_text = None
    group_name = "text-"+to_langue
    for layer in image.layers:
        if pdb.gimp_item_is_group(layer) and pdb.gimp_item_get_name(layer) == group_name:
            group_text = layer
            trace ("------------groupe preexistant-------------")
            break

    if group_text is None:
        # Créer un groupe de calques nommé "text-fr" s'il n'existe pas
        group_text = pdb.gimp_layer_group_new(image)
        pdb.gimp_item_set_name(group_text, group_name)
        pdb.gimp_image_insert_layer(image, group_text, None, 0)
        trace("----------------groupe créé-----------------")

    if pdb.gimp_item_is_group(selected_layer):
        trace("----------layer is group-------------")
        layers = selected_layer.layers
        trace (layers)
    elif pdb.gimp_item_is_text_layer(selected_layer):
        trace("----------layer is text-------------")
        layers=[selected_layer]
        trace (layers)
    else:
        print("--------Veuillez sélectionner un groupe de calques ou un calque de texte.----")
        gimp.message("Veuillez sélectionner un groupe de calques ou un calque de texte.")
        image.undo_group_end()
        return
        
    # Parcours de tous les calques du groupe
    trace(layers)
    for layer in layers:
        trace("------------for--------------")
        trace (layer)
        # Vérification si le calque est de type texte
        if pdb.gimp_item_is_text_layer(layer):
            # Dupliquer le calque
            duplicate = pdb.gimp_layer_copy(layer, True)
		
            # Ajouter le calque duplique au groupe "text-fr"
            pdb.gimp_image_insert_layer(image, duplicate, group_text, 0)
            
            # Récupérer le contenu texte du calque dupliqué
            text = pdb.gimp_text_layer_get_text(duplicate)
            if text is None :
                trace ("----------text had markup-------------")
                text = pdb.gimp_text_layer_get_markup(duplicate)
                # quitter les markups avec une RegEx
                text= re.sub(r"<.*?>", "", text)
		
            # essayer de traduir
            try:
                text = text.decode("utf-8")
                translated_text = translator.translate(text)
            except Exception as e:
                translated_text = "Erreur lors de la traduction : {}".format(e)
                trace("Erreur lors de la traduction : {}".format(e))

            # vérifier s'il y a des caractères spéciaux html
			# translated_text="J'aime les bananes &amp; les oranges &#128512;" #pour tester
            if re.search(r"&[#\w]+;", translated_text):
                trace("-----------caractères html---------------")
                # remplacer les caractères 
                parser = HTMLDecodeParser()
                parser.feed(translated_text)
                translated_text = parser.result
            # Mettre à jour le texte du calque dupliqué avec la traduction
            pdb.gimp_text_layer_set_text(duplicate, translated_text)
    # Actualisation de l'affichage de l'image
    pdb.gimp_displays_flush()
    #pdb.gimp_message("fini")
    # restore stuff
    #trace(image)
    image.undo_group_end()

def translate_text_layers_quick (image, drawable):
    # Créer le nom du fichier JSON où sont sauvegardées les valeurs par défaut
    json_file_name = os.path.basename(__file__).replace(".py", ".json")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(current_dir, "..","..", json_file_name)

    # Lire les données à partir du fichier JSON
    data={}
    try:
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)
        print("Données lues avec succès depuis", json_file_path)
        print("from_lang =", data["from_lang"])
        print("to_lang =", data["to_lang"])
    except Exception as e:
        print("Erreur lors de la lecture des données :", e)
    #dans la ligne suivante, "fr" et "es" sont des valeurs renvoyées is la clé n'est pas trouvée.
    translate_text_layers(image, drawable, data.get("from_langue","fr"), data.get("to_langue","es"))

author = "Jacques Duflos"
root_menu = "<Image>/Filters/Language/"
blurb = "Translate text layers from a language to another"
date = "2023"

register(
    "python-fu-translate-text-layers",
    blurb,
    '''The plug-in creates copies of the text layers and move them to a layer group named \"text-xx\" where xx is the language code according to ISO 639-1.
    It will create the layer group if not found. Then it will translate the text with the online service Mymemory and update the text of the
    copied layer. This plug-in will behave diferentely according to the selected layer.
text layer selected

If a text layer is selected, the plug-in will copy and translate the one selected text layer.
layer selected

If a layer group is selected, the plug-in will copy one by one each text layer of the group and translate them. Non recursive. If there is a sub-layer
group, it will not be fetched
any other selection

If neither a text layer nor a layer group is selected, the plug-in displays an error message and stops''',
    author,
    author,
    date,
    root_menu+"Translate Text Layers...",
    "*",
    [
        (PF_STRING, 'from_langue',      'Translate from language','es'),
        (PF_STRING, 'to_langue',      'Translate to language ','fr')
    ],
    [],
    translate_text_layers)

register(
    "python-fu-translate-text-layers-quick",
    blurb,
    '''The plug-in creates copies of the text layers and move them to a layer group named \"text-xx\" where xx is the language code according to ISO 639-1.
    It will create the layer group if not found. Then it will translate the text with the online service Mymemory and update the text of the
    copied layer. This plug-in will behave diferentely according to the selected layer.
text layer selected

If a text layer is selected, the plug-in will copy and translate the one selected text layer.
layer selected

If a layer group is selected, the plug-in will copy one by one each text layer of the group and translate them. Non recursive. If there is a sub-layer
group, it will not be fetched
any other selection

If neither a text layer nor a layer group is selected, the plug-in displays an error message and stops''',
    author,
    author,
    date,
    root_menu+"Translate Text Layers",
    "*",
    [],
    [],
    translate_text_layers_quick)

main()

