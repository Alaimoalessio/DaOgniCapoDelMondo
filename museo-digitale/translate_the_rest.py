import os
import re

files_replacements = {
    'templates/era.html': [
        "Linea del Tempo",
        "Esplora la collezione attraverso le epoche storiche. Clicca su un'epoca per scoprire gli oggetti che la caratterizzano.",
        "Nessun oggetto trovato per quest'epoca."
    ],
    'templates/epoche.html': [
        "Epoche Storiche",
        "Esplora le diverse epoche storiche rappresentate nella nostra collezione",
        "Esplora epoca →"
    ],
    'templates/contatti.html': [
        "Siamo qui per rispondere alle tue domande",
        "Invia un Messaggio",
        "Nome *",
        "Il tuo nome",
        "Email *",
        "tua.email@esempio.com",
        "Oggetto *",
        "Seleziona un argomento",
        "Informazioni generali",
        "Informazioni sulla collezione",
        "Richiesta di ricerca",
        "Proposta di collaborazione",
        "Richiesta media",
        "Altro",
        "Messaggio *",
        "Scrivi qui il tuo messaggio...",
        "Accetto la",
        "privacy policy",
        "Invia Messaggio",
        "Informazioni di Contatto",
        "Indirizzo",
        "Museo Digitale",
        "Collezione Virtuale",
        "Telefono",
        "Lun-Ven: 9:00 - 18:00",
        "Risposta entro 48 ore",
        "Orari",
        "Sempre aperto",
        "Accesso 24/7 online",
        "Seguici",
        "Domande Frequenti",
        "Come posso visitare la collezione?",
        "La collezione è completamente accessibile online 24/7. Puoi esplorare gli oggetti attraverso la galleria principale o utilizzare la mappa interattiva per scoprire le origini geografiche.",
        "La collezione è gratuita?",
        "Sì, l'accesso alla collezione digitale è completamente gratuito. Non vendiamo nulla e il nostro obiettivo è rendere il patrimonio culturale accessibile a tutti.",
        "Posso richiedere informazioni su un oggetto specifico?",
        "Certamente! Utilizza il form di contatto selezionando \"Informazioni sulla collezione\" come oggetto. Ti risponderemo con tutte le informazioni disponibili.",
        "Accettate donazioni di oggetti?",
        "Valutiamo ogni proposta di donazione. Contattaci attraverso il form selezionando \"Proposta di collaborazione\" per discutere la possibilità."
    ],
    'templates/chi-siamo.html': [
        "La Nostra Storia",
        "La collezione \"Da ogni capo del mondo\" nasce dalla passione per la preservazione e la condivisione del patrimonio culturale globale. Fondata con l'obiettivo di rendere accessibile a tutti la bellezza e la diversità delle tradizioni che hanno caratterizzato l'umanità attraverso i secoli.",
        "La nostra missione è quella di custodire, studiare e condividere oltre 700 copricapi, abiti e oggetti storici provenienti da ogni angolo del pianeta. Ogni pezzo racconta una storia unica, testimonia l'ingegno umano e rappresenta un ponte tra passato e presente.",
        "Attraverso questo museo digitale, vogliamo rendere omaggio alle culture del mondo, preservando la memoria di tradizioni che rischiano di essere dimenticate e offrendo a tutti la possibilità di esplorare la ricchezza del patrimonio culturale globale.",
        "Oggetti in Collezione",
        "Paesi Rappresentati",
        "Anni di Storia",
        "La Nostra Missione",
        "Preservazione",
        "Conservare e proteggere il patrimonio culturale per le generazioni future, garantendo che ogni oggetto sia documentato, studiato e preservato secondo i più alti standard museali.",
        "Accessibilità",
        "Rendere la cultura accessibile a tutti, senza barriere geografiche o economiche, attraverso una piattaforma digitale aperta e gratuita.",
        "Educazione",
        "Promuovere la comprensione interculturale e l'apprezzamento della diversità attraverso l'educazione e la condivisione della conoscenza.",
        "Ricerca",
        "Supportare la ricerca accademica e la scoperta continua, collaborando con studiosi e istituzioni per approfondire la conoscenza del patrimonio culturale mondiale.",
        "La Collezione",
        "La nostra collezione comprende una straordinaria varietà di oggetti che spaziano dai copricapi cerimoniali alle armature militari, dagli abiti tradizionali agli accessori di valore storico e culturale.",
        "Ogni pezzo è stato selezionato per la sua importanza storica, culturale o artistica, rappresentando tradizioni che vanno dall'antichità ai giorni nostri. La collezione è organizzata per categorie, regioni geografiche ed epoche storiche, permettendo ai visitatori di esplorare il patrimonio culturale attraverso diverse prospettive.",
        "Copricapi cerimoniali e tradizionali",
        "Abiti e costumi storici",
        "Oggetti militari e cerimoniali",
        "Accessori e gioielli tradizionali",
        "Esplora la collezione attraverso la mappa interattiva e scopri le origini geografiche di ogni oggetto.",
        "I Nostri Valori",
        "Rispetto",
        "Rispettiamo ogni cultura e tradizione, riconoscendo il valore intrinseco di ogni espressione del patrimonio umano.",
        "Trasparenza",
        "Operiamo con trasparenza e integrità, condividendo apertamente informazioni sulla collezione e le nostre attività.",
        "Innovazione",
        "Utilizziamo la tecnologia per rendere il patrimonio culturale più accessibile e coinvolgente.",
        "Collaborazione",
        "Lavoriamo con istituzioni, studiosi e comunità per preservare e valorizzare il patrimonio culturale globale."
    ],
    'templates/didattica.html': [
        "Didattica per Scuole",
        "Scopri la nostra collezione attraverso percorsi didattici pensati per studenti di tutte le età",
        "Perché la Nostra Collezione",
        "La nostra collezione privata offre un'opportunità unica per gli studenti di esplorare la storia, le culture e le tradizioni del mondo attraverso oggetti autentici e rari.",
        "Ogni oggetto racconta una storia: da dove viene, chi lo ha creato, come è stato utilizzato. Attraverso percorsi didattici strutturati, gli studenti possono:",
        "Esplorare culture diverse da tutto il mondo",
        "Comprendere l'evoluzione storica attraverso oggetti reali",
        "Sviluppare capacità di osservazione e analisi",
        "Apprezzare la diversità e l'arte artigianale",
        "I nostri percorsi didattici sono progettati per coinvolgere gli studenti attraverso attività interattive, quiz e materiali di supporto.",
        "Esplora i Percorsi →",
        "Materiali per Insegnanti",
        "Offriamo materiali didattici completi per supportare gli insegnanti nella preparazione delle visite e delle attività in classe.",
        "Schede didattiche, guide per i percorsi, domande di riflessione e bibliografia per approfondimenti. Tutti i materiali sono disponibili nell'area riservata.",
        "Accedi all'Area Insegnanti →",
        "Schede PDF scaricabili, guide complete e risorse aggiuntive per arricchire l'esperienza didattica."
    ]
}

# Advanced replacement ignoring newlines and spaces
for file_path, sentences in files_replacements.items():
    if not os.path.exists(file_path):
        continue
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    for sentence in sentences:
        # Match the text precisely, handling exact whitespaces or varied whitespaces in the source.
        # But for simpler approach and exactness, we just replace it directly.
        # Since HTML might have multiline we do a regex replace
        escaped_sentence = re.escape(sentence).replace(r'\ ', r'\s+').replace(r'\n', r'\s*')
        # prevent double replace
        if f"{{{{ _('{sentence}') }}}}" not in content:
            # We want to use the exact string the user provided if it matches nicely
            # Actually simplest is just simple `content.replace(sentence, f"{{{{ _('{sentence}') }}}}")`
            # For multiline we use regex
            match = re.search(escaped_sentence, content)
            if match:
                content = content[:match.start()] + f"{{{{ _('{sentence}') }}}}" + content[match.end():]

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

# We will let Babel extract them naturally!
