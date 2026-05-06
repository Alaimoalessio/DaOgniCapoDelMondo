import os
import re

globe_translations = {
    'en': {
        "Esplora il Mondo": "Explore the World",
        "Il Mondo in Collezione": "The World in the Collection",
        "Esplora la provenienza geografica degli oggetti. Ruota il globo e clicca sugli indicatori dorati per scoprire tesori da ogni continente.": "Explore the geographical provenance of the items. Rotate the globe and click on the golden indicators to discover treasures from every continent.",
        "Guida all'esplorazione": "Exploration Guide",
        "Trascina per ruotare il globo o usa le frecce per navigare": "Drag to rotate the globe or use arrows to navigate",
        "Usa lo scroll per fare zoom": "Use scroll to zoom in",
        "Clicca sui marker dorati per i dettagli": "Click on golden markers for details",
        "Caricamento del globo terrestre...": "Loading the Earth globe...",
        "oggetto": "item",
        "oggetti": "items"
    },
    'fr': {
        "Esplora il Mondo": "Explorer le Monde",
        "Il Mondo in Collezione": "Le Monde dans la Collection",
        "Esplora la provenienza geografica degli oggetti. Ruota il globo e clicca sugli indicatori dorati per scoprire tesori da ogni continente.": "Explorez la provenance géographique des objets. Faites pivoter le globe et cliquez sur les indicateurs.",
        "Guida all'esplorazione": "Guide d'exploration",
        "Trascina per ruotare il globo o usa le frecce per navigare": "Faites glisser pour faire pivoter le globe",
        "Usa lo scroll per fare zoom": "Utilisez le défilement pour zoomer",
        "Clicca sui marker dorati per i dettagli": "Cliquez sur les marqueurs dorés pour les détails",
        "Caricamento del globo terrestre...": "Chargement du globe terrestre...",
        "oggetto": "objet",
        "oggetti": "objets"
    },
    'es': {
        "Esplora il Mondo": "Explorar el Mundo",
        "Il Mondo in Collezione": "El Mundo en la Colección",
        "Esplora la provenienza geografica degli oggetti. Ruota il globo e clicca sugli indicatori dorati per scoprire tesori da ogni continente.": "Explora la procedencia geográfica de los objetos. Haz girar el globo y haz clic en los indicadores dorados.",
        "Guida all'esplorazione": "Guía de exploración",
        "Trascina per ruotare il globo o usa le frecce per navigare": "Arrastra para rotar el globo o usa las flechas",
        "Usa lo scroll per fare zoom": "Usa la rueda para acercar",
        "Clicca sui marker dorati per i dettagli": "Haz clic en los marcadores dorados para los detalles",
        "Caricamento del globo terrestre...": "Cargando el globo terráqueo...",
        "oggetto": "objeto",
        "oggetti": "objetos"
    },
    'de': {
        "Esplora il Mondo": "Welt Erkunden",
        "Il Mondo in Collezione": "Die Welt in der Sammlung",
        "Esplora la provenienza geografica degli oggetti. Ruota il globo e clicca sugli indicatori dorati per scoprire tesori da ogni continente.": "Erkunden Sie die geografische Herkunft der Objekte. Drehen Sie den Globus und klicken Sie auf die goldenen Indikatoren.",
        "Guida all'esplorazione": "Entdeckerleitfaden",
        "Trascina per ruotare il globo o usa le frecce per navigare": "Ziehen, um den Globus zu drehen",
        "Usa lo scroll per fare zoom": "Scrollen zum Zoomen",
        "Clicca sui marker dorati per i dettagli": "Klicken Sie auf goldene Markierungen für Details",
        "Caricamento del globo terrestre...": "Globus wird geladen...",
        "oggetto": "Objekt",
        "oggetti": "Objekte"
    }
}

base_dir = "translations"
for lang, trans_dict in globe_translations.items():
    po_path = os.path.join(base_dir, lang, "LC_MESSAGES", "messages.po")
    if not os.path.exists(po_path):
        continue
    
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()

    for eng_id, translated_str in trans_dict.items():
        safe_id = eng_id.replace('"', '\\"')
        safe_trans = translated_str.replace('"', '\\"')
        # Replace empty strings
        pattern = r'msgid "' + re.escape(safe_id) + r'"\nmsgstr "[^"]*"'
        replacement = 'msgid "' + safe_id + '"\nmsgstr "' + safe_trans + '"'
        content = re.sub(pattern, replacement, content)

    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Processed globe translations for {lang}")
