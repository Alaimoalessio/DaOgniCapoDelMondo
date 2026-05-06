"""
Educational paths data and queries for the Didattica section.
This module separates the hardcoded data from the main app.py file to respect the MVC pattern.
Ideally, this data should be migrated to the database.
"""
from models import Item
from sqlalchemy import or_

def get_percorsi_list():
    """Restituisce la lista di base dei percorsi didattici."""
    return [
        {
            'id': 1,
            'title': 'Viaggio nel Tempo: dalle Armature ai Copricapi',
            'age_group': 'Scuola Primaria',
            'age_range': '6-10 anni',
            'duration': '1-2 ore',
            'description': 'Un viaggio affascinante attraverso la storia, esplorando armature, elmi e copricapi cerimoniali di diverse epoche e culture.',
            'icon': '🛡️',
            'color': 'gold'
        },
        {
            'id': 2,
            'title': 'Culture del Mondo: Tradizioni e Simboli',
            'age_group': 'Scuola Secondaria I grado',
            'age_range': '11-13 anni',
            'duration': '2 ore',
            'description': 'Scopri come i copricapi e gli abiti tradizionali raccontano storie di culture diverse, simboli di identità e tradizioni millenarie.',
            'icon': '🌍',
            'color': 'turquoise'
        },
        {
            'id': 3,
            'title': 'Arte e Artigianato: Materiali e Tecniche',
            'age_group': 'Scuola Secondaria II grado',
            'age_range': '14-18 anni',
            'duration': '2-3 ore',
            'description': 'Analisi approfondita dei materiali, delle tecniche artigianali e dell\'evoluzione dell\'arte attraverso gli oggetti della collezione.',
            'icon': '🎨',
            'color': 'purple'
        },
        {
            'id': 4,
            'title': 'Storia Militare: Armi e Armature',
            'age_group': 'Scuola Secondaria II grado',
            'age_range': '14-18 anni',
            'duration': '2-3 ore',
            'description': 'Un percorso dedicato alla storia militare, esplorando l\'evoluzione di armi, armature e strategie attraverso i secoli.',
            'icon': '⚔️',
            'color': 'red'
        }
    ]

def get_percorso_detail(percorso_id):
    """Restituisce il dettaglio di un percorso e la sua query associata per gli items."""
    percorsi_data = {
        1: {
            'id': 1,
            'title': 'Viaggio nel Tempo: dalle Armature ai Copricapi',
            'age_group': 'Scuola Primaria',
            'age_range': '6-10 anni',
            'duration': '1-2 ore',
            'description': 'Un viaggio affascinante attraverso la storia, esplorando armature, elmi e copricapi cerimoniali di diverse epoche e culture.',
            'objectives': [
                'Comprendere l\'evoluzione delle armature e dei copricapi nel tempo',
                'Conoscere diverse culture attraverso i loro oggetti tradizionali',
                'Sviluppare capacità di osservazione e analisi',
                'Apprezzare la diversità culturale mondiale'
            ],
            'activities': [
                'Osservazione guidata degli oggetti',
                'Attività di disegno e colorazione',
                'Quiz interattivo su epoche e culture',
                'Creazione di una timeline personale'
            ]
        },
        2: {
            'id': 2,
            'title': 'Culture del Mondo: Tradizioni e Simboli',
            'age_group': 'Scuola Secondaria I grado',
            'age_range': '11-13 anni',
            'duration': '2 ore',
            'description': 'Scopri come i copricapi e gli abiti tradizionali raccontano storie di culture diverse, simboli di identità e tradizioni millenarie.',
            'objectives': [
                'Comprendere il significato culturale degli oggetti tradizionali',
                'Esplorare la diversità culturale mondiale',
                'Analizzare simboli e significati nelle diverse culture',
                'Sviluppare empatia e rispetto per le differenze culturali'
            ],
            'activities': [
                'Analisi comparativa di oggetti da diverse regioni',
                'Ricerca su simboli e significati culturali',
                'Discussione guidata su identità e tradizioni',
                'Creazione di mappe culturali interattive'
            ]
        },
        3: {
            'id': 3,
            'title': 'Arte e Artigianato: Materiali e Tecniche',
            'age_group': 'Scuola Secondaria II grado',
            'age_range': '14-18 anni',
            'duration': '2-3 ore',
            'description': 'Analisi approfondita dei materiali, delle tecniche artigianali e dell\'evoluzione dell\'arte attraverso gli oggetti della collezione.',
            'objectives': [
                'Comprendere le proprietà e l\'uso dei materiali storici',
                'Analizzare tecniche artigianali tradizionali',
                'Valutare l\'evoluzione tecnologica nell\'artigianato',
                'Apprezzare la maestria artigianale del passato'
            ],
            'activities': [
                'Studio approfondito dei materiali (oro, argento, seta, legno)',
                'Analisi delle tecniche di lavorazione',
                'Confronto tra tecniche antiche e moderne',
                'Progetto di ricerca su un materiale specifico'
            ]
        },
        4: {
            'id': 4,
            'title': 'Storia Militare: Armi e Armature',
            'age_group': 'Scuola Secondaria II grado',
            'age_range': '14-18 anni',
            'duration': '2-3 ore',
            'description': 'Un percorso dedicato alla storia militare, esplorando l\'evoluzione di armi, armature e strategie attraverso i secoli.',
            'objectives': [
                'Comprendere l\'evoluzione delle armi e armature',
                'Analizzare strategie militari storiche',
                'Valutare l\'impatto della tecnologia militare',
                'Riflettere sul significato della guerra nella storia'
            ],
            'activities': [
                'Analisi cronologica di armi e armature',
                'Studio delle strategie militari per epoche',
                'Confronto tra armature di diverse culture',
                'Discussione guidata su pace e conflitto'
            ]
        }
    }
    
    percorso = percorsi_data.get(percorso_id)
    if not percorso:
        return None
        
    # Assegna gli items tramite DB queries
    try:
        if percorso_id == 1:
            percorso['path_items'] = Item.query.filter(
                or_(
                    Item.category_id.in_([1]),  # Militaria
                    Item.title.like('%elmo%'),
                    Item.title.like('%armatura%'),
                    Item.title.like('%copricapo%')
                )
            ).limit(8).all()
        elif percorso_id == 2:
            percorso['path_items'] = Item.query.filter(
                Item.region_id.isnot(None)
            ).limit(10).all()
        elif percorso_id == 3:
            percorso['path_items'] = Item.query.join(Item.materials).limit(12).all()
        elif percorso_id == 4:
            percorso['path_items'] = Item.query.filter(
                Item.category_id.in_([1])
            ).limit(10).all()
    except Exception as e:
        print(f"Error fetching path_items for percorso {percorso_id}: {e}")
        percorso['path_items'] = []
        
    return percorso
