"""
Seed script to populate database with sample museum objects
Run this after creating the database: python seed_data.py
"""
from app import app, db
from models import Item, Category, Region, Material, Era
from datetime import date

def seed_database():
    """Populate database with sample data"""
    
    print("Seeding database with sample data...")
    
    # Create categories
    categories = {
        'militaria': Category(name='Militaria', description='Oggetti militari storici'),
        'cerimoniale': Category(name='Cerimoniale', description='Oggetti per cerimonie e rituali'),
        'abbigliamento': Category(name='Abbigliamento', description='Abiti e accessori tradizionali'),
        'arte': Category(name='Arte Sacra', description='Oggetti religiosi e sacri')
    }
    
    for cat in categories.values():
        db.session.add(cat)
    
    # Create regions
    regions = {
        'asia': Region(name='Asia Orientale', continent='Asia', description='Giappone, Cina, Corea'),
        'himalaya': Region(name='Himalaya', continent='Asia', description='Tibet, Nepal, Bhutan'),
        'africa': Region(name='Africa Occidentale', continent='Africa', description='Nigeria, Mali, Costa d\'Avorio'),
        'europa': Region(name='Europa', continent='Europa', description='Francia, Italia, Germania')
    }
    
    for reg in regions.values():
        db.session.add(reg)
    
    # Create materials
    materials = {
        'ferro': Material(name='Ferro', description='Metallo ferroso'),
        'acciaio': Material(name='Acciaio', description='Lega di ferro e carbonio'),
        'oro': Material(name='Oro', description='Metallo prezioso'),
        'argento': Material(name='Argento', description='Metallo prezioso'),
        'tessuto': Material(name='Tessuto', description='Fibre tessili'),
        'seta': Material(name='Seta', description='Fibra naturale pregiata'),
        'legno': Material(name='Legno', description='Materiale organico'),
        'turchese': Material(name='Turchese', description='Pietra preziosa azzurra'),
        'corallo': Material(name='Corallo', description='Materiale organico marino'),
        'bronzo': Material(name='Bronzo', description='Lega di rame e stagno')
    }
    
    for mat in materials.values():
        db.session.add(mat)
    
    # Create eras
    eras = {
        'medievale': Era(name='Medievale', year_start=500, year_end=1500, description='Medioevo'),
        'rinascimento': Era(name='Rinascimento', year_start=1400, year_end=1600, description='Rinascimento'),
        'edo': Era(name='Periodo Edo', year_start=1603, year_end=1868, description='Epoca Edo giapponese'),
        'napoleonico': Era(name='Epoca Napoleonica', year_start=1799, year_end=1815, description='Periodo napoleonico'),
        'moderno': Era(name='Moderno', year_start=1800, year_end=1950, description='Epoca moderna')
    }
    
    for era in eras.values():
        db.session.add(era)
    
    db.session.commit()
    print("✓ Categories, Regions, Materials, and Eras created")
    
    # Create sample items
    items_data = [
        {
            'title': 'Armatura Samurai Completa (Gusoku)',
            'description': 'Armatura completa da samurai comprensiva di elmo (kabuto), maschera facciale (mempo), corazza (do), protezioni per spalle e braccia.',
            'historical_context': 'Le armature samurai rappresentano il culmine dell\'artigianato bellico giapponese. Questa armatura risale al periodo Edo ed era utilizzata da un guerriero di alto rango. Le decorazioni dorate e le corde di seta intrecciata (odoshi) indicano lo status elevato del proprietario.',
            'year_from': 1750,
            'year_to': 1800,
            'provenance': 'Kyoto, Giappone',
            'image_url': 'images/items/Armatura Samurai Completa (Gusoku).jpg',
            'conservation_state': 'Ottimo',
            'category': categories['militaria'],
            'region': regions['asia'],
            'era': eras['edo'],
            'materials': [materials['ferro'], materials['acciaio'], materials['oro'], materials['seta']]
        },
        {
            'title': 'Feluca Napoleonica da Ufficiale',
            'description': 'Cappello bicorno (feluca) da ufficiale dell\'esercito napoleonico, realizzato in feltro nero con bordature dorate.',
            'historical_context': 'Il bicorno era il copricapo distintivo degli ufficiali napoleonici. Questo esemplare apparteneva probabilmente a un capitano di artiglieria, come suggerito dalle decorazioni specifiche e dal grado delle finiture.',
            'year_from': 1805,
            'year_to': 1815,
            'provenance': 'Francia',
            'image_url': 'images/items/Feluca-Napoleonica-da-Ufficiale.jpg',
            'conservation_state': 'Buono',
            'category': categories['militaria'],
            'region': regions['europa'],
            'era': eras['napoleonico'],
            'materials': [materials['tessuto']]
        },
        {
            'title': 'Perak Himalayano Tibetano',
            'description': 'Copricapo cerimoniale femminile tibetano decorato con turchesi, coralli e argento.',
            'historical_context': 'Il perak è un elaborato copricapo indossato dalle donne tibetane durante le cerimonie importanti. Le pietre turchesi simboleggiano il cielo e la spiritualità, mentre i coralli rappresentano la vitalità. Questo perak proviene dalla regione del Ladakh ed era parte della dote di una famiglia nobile.',
            'year_from': 1880,
            'year_to': 1920,
            'provenance': 'Ladakh, Tibet',
            'image_url': 'images/items/Perak Himalayano Tibetano.jpg',
            'conservation_state': 'Discreto',
            'category': categories['cerimoniale'],
            'region': regions['himalaya'],
            'era': eras['moderno'],
            'materials': [materials['argento'], materials['turchese'], materials['corallo']]
        },
        {
            'title': 'Maschera Yoruba Gelede',
            'description': 'Maschera cerimoniale del popolo Yoruba utilizzata nelle danze Gelede per onorare le donne anziane.',
            'historical_context': 'Le maschere Gelede sono utilizzate in cerimonie che celebrano il potere spirituale delle donne nella società Yoruba. Questa maschera rappresenta una donna con acconciatura elaborata ed era indossata durante danze rituali che si svolgevano di notte alla luce delle torce.',
            'year_from': 1920,
            'year_to': 1950,
            'provenance': 'Nigeria',
            'image_url': 'images/items/Maschera Yoruba Gelede.jpg',
            'conservation_state': 'Buono',
            'category': categories['cerimoniale'],
            'region': regions['africa'],
            'era': eras['moderno'],
            'materials': [materials['legno']]
        },
        {
            'title': 'Elmo Barbaresco Longobardo',
            'description': 'Elmo conico in ferro battuto con nasale protettivo, tipico dei guerrieri longobardi.',
            'historical_context': 'Gli elmi longobardi sono rari esempi di metallurgia altomedievale. Questo esemplare presenta la caratteristica forma conica che offriva eccellente protezione deflettendo i colpi. Il nasale fisso era una innovazione tecnologica dell\'epoca.',
            'year_from': 600,
            'year_to': 700,
            'provenance': 'Italia settentrionale',
            'image_url': 'images/items/Elmo Barbaresco Longobardo.jpg',
            'conservation_state': 'Restaurato',
            'category': categories['militaria'],
            'region': regions['europa'],
            'era': eras['medievale'],
            'materials': [materials['ferro'], materials['bronzo']]
        },
        {
            'title': 'Kimono Formale da Cerimonia (Furisode)',
            'description': 'Kimono in seta con maniche lunghe decorato con motivi floreali dipinti a mano e ricami in oro.',
            'historical_context': 'Il furisode è il kimono più formale per le giovani donne non sposate. Questo esemplare era indossato durante il Seijin no Hi (giorno della maggiore età). I motivi raffigurano ciliegi in fiore (sakura) e gru, simboli di bellezza e longevità.',
            'year_from': 1890,
            'year_to': 1910,
            'provenance': 'Tokyo, Giappone',
            'image_url': 'images/items/Kimono Formale da Cerimonia (Furisode).jpg',
            'conservation_state': 'Ottimo',
            'category': categories['abbigliamento'],
            'region': regions['asia'],
            'era': eras['moderno'],
            'materials': [materials['seta'], materials['oro']]
        }
    ]
    
    for item_data in items_data:
        item = Item(
            title=item_data['title'],
            description=item_data['description'],
            historical_context=item_data['historical_context'],
            year_from=item_data['year_from'],
            year_to=item_data['year_to'],
            provenance=item_data['provenance'],
            image_url=item_data['image_url'],
            conservation_state=item_data['conservation_state'],
            category=item_data['category'],
            region=item_data['region'],
            era=item_data['era']
        )
        
        for material in item_data['materials']:
            item.materials.append(material)
        
        db.session.add(item)
    
    db.session.commit()
    print(f"✓ {len(items_data)} sample items created")
    print("\n=== Database seeding complete! ===")
    print("You can now run: python app.py")


if __name__ == '__main__':
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Seed new data
        seed_database()
