import os
import re

extra_translations = {
    'en': {
        "Percorsi": "Paths",
        "Descrizione": "Description",
        "Obiettivi Didattici": "Educational Objectives",
        "Attività Proposte": "Proposed Activities",
        "Oggetti del Percorso": "Items in this Path",
        "Gli oggetti della collezione utilizzati in questo percorso": "The collection items used in this educational path",
        "Quiz Interattivo": "Interactive Quiz",
        "Metti alla prova le tue conoscenze con questo quiz interattivo": "Test your knowledge with this interactive quiz",
        "Il quiz interattivo sarà disponibile a breve": "The interactive quiz will be available soon",
        "Torna ai Percorsi": "Back to Paths",
        "Prenota una Visita →": "Book a Tour →",
        "Provenienza": "Provenance",
        "Regione": "Region",
        "Epoca": "Era",
        "Datazione": "Dating",
        "Materiali": "Materials",
        "Contesto Storico": "Historical Context",
        "Oggetti Correlati": "Related Items",
        "Errore Interno del Museo": "Internal Museum Error",
        "Abbiamo riscontrato un problema tecnico mentre caricavamo l'archivio. Il nostro team di curatori sta già indagando sulla causa. Riprova tra qualche istante.": "We encountered a technical problem while loading the archive. Our curation team is investigating. Please try again soon.",
        "Ritorna all'Ingresso Reale": "Return to the Main Hall",
        "Segnala il Problema": "Report the Issue"
    },
    'fr': {
        "Percorsi": "Parcours",
        "Descrizione": "Description",
        "Obiettivi Didattici": "Objectifs Pédagogiques",
        "Attività Proposte": "Activités Proposées",
        "Oggetti del Percorso": "Objets de ce Parcours",
        "Gli oggetti della collezione utilizzati in questo percorso": "Objets de la collection utilisés dans ce parcours éducatif",
        "Quiz Interattivo": "Quiz Interactif",
        "Metti alla prova le tue conoscenze con questo quiz interattivo": "Testez vos connaissances avec ce quiz interactif",
        "Il quiz interattivo sarà disponibile a breve": "Le quiz interactif sera bientôt disponible",
        "Torna ai Percorsi": "Retour aux Parcours",
        "Prenota una Visita →": "Réserver une Visite →",
        "Provenienza": "Provenance",
        "Regione": "Région",
        "Epoca": "Époque",
        "Datazione": "Datation",
        "Materiali": "Matériaux",
        "Contesto Storico": "Contexte Historique",
        "Oggetti Correlati": "Objets Connexes",
        "Errore Interno del Museo": "Erreur Interne du Musée",
        "Abbiamo riscontrato un problema tecnico mentre caricavamo l'archivio. Il nostro team di curatori sta già indagando sulla causa. Riprova tra qualche istante.": "Nous avons rencontré un problème technique lors du chargement de l'archive. L'équipe étudie la cause.",
        "Ritorna all'Ingresso Reale": "Retour à l'Entrée",
        "Segnala il Problema": "Signaler le Problème"
    },
    'es': {
        "Percorsi": "Rutas",
        "Descrizione": "Descripción",
        "Obiettivi Didattici": "Objetivos Educativos",
        "Attività Proposte": "Actividades Propuestas",
        "Oggetti del Percorso": "Objetos de esta Ruta",
        "Gli oggetti della collezione utilizzati in questo percorso": "Los objetos de la colección utilizados en esta ruta",
        "Quiz Interattivo": "Cuestionario Interactivo",
        "Metti alla prova le tue conoscenze con questo quiz interattivo": "Pon a prueba tus conocimientos con este cuestionario interactivo",
        "Il quiz interattivo sarà disponibile a breve": "El cuestionario interactivo estará disponible pronto",
        "Torna ai Percorsi": "Folver a las Rutas",
        "Prenota una Visita →": "Reserva una Visita →",
        "Provenienza": "Procedencia",
        "Regione": "Región",
        "Epoca": "Época",
        "Datazione": "Datación",
        "Materiali": "Materiales",
        "Contesto Storico": "Contexto Histórico",
        "Oggetti Correlati": "Objetos Relacionados",
        "Errore Interno del Museo": "Error Interno del Museo",
        "Abbiamo riscontrato un problema tecnico mentre caricavamo l'archivio. Il nostro team di curatori sta già indagando sulla causa. Riprova tra qualche istante.": "Ocurrió un problema técnico al cargar el archivo. El equipo lo está solucionando.",
        "Ritorna all'Ingresso Reale": "Volver a la Entrada Principal",
        "Segnala il Problema": "Reportar el Problema"
    },
    'de': {
        "Percorsi": "Routen",
        "Descrizione": "Beschreibung",
        "Obiettivi Didattici": "Lernziele",
        "Attività Proposte": "Vorgeschlagene Aktivitäten",
        "Oggetti del Percorso": "Objekte in diesem Kurs",
        "Gli oggetti della collezione utilizzati in questo percorso": "Objekte der Sammlung, die in diesem Bildungskurs verwendet werden",
        "Quiz Interattivo": "Interaktives Quiz",
        "Metti alla prova le tue conoscenze con questo quiz interattivo": "Testen Sie Ihr Wissen mit diesem interaktiven Quiz",
        "Il quiz interattivo sarà disponibile a breve": "Das interaktive Quiz wird bald verfügbar sein",
        "Torna ai Percorsi": "Zurück zu Touren",
        "Prenota una Visita →": "Tour Buchen →",
        "Provenienza": "Herkunft",
        "Regione": "Region",
        "Epoca": "Epoche",
        "Datazione": "Datierung",
        "Materiali": "Materialien",
        "Contesto Storico": "Historischer Kontext",
        "Oggetti Correlati": "Verwandte Objekte",
        "Errore Interno del Museo": "Interner Fehler",
        "Abbiamo riscontrato un problema tecnico mentre caricavamo l'archivio. Il nostro team di curatori sta già indagando sulla causa. Riprova tra qualche istante.": "Technisches Problem beim Laden des Archivs.",
        "Ritorna all'Ingresso Reale": "Zur Haupthalle",
        "Segnala il Problema": "Problem Melden"
    }
}

base_dir = "translations"
for lang, trans_dict in extra_translations.items():
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
    print(f"Processed extra translations for {lang}")
