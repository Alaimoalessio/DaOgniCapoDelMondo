"""
Script per aggiungere 24 nuovi oggetti alla collezione
Esegui: python add_items.py
"""
from app import app, db
from models import Item, Category, Region, Material, Era
from datetime import date
import random

def add_new_items():
    """Aggiunge 24 nuovi oggetti alla collezione"""
    
    print("Aggiunta di 24 nuovi oggetti alla collezione...")
    
    # Recupera categorie, regioni, materiali ed ere esistenti
    categories = Category.query.all()
    regions = Region.query.all()
    materials = Material.query.all()
    eras = Era.query.all()
    
    if not categories or not regions or not materials or not eras:
        print("⚠️  Errore: Assicurati che il database sia già popolato con categorie, regioni, materiali ed ere.")
        print("   Esegui prima: python seed_data.py")
        return
    
    # Dati per i nuovi oggetti (24 oggetti)
    new_items_data = [
        {
            'title': 'Elmo da Cavaliere Medievale',
            'description': 'Elmo in acciaio con visiera mobile e decorazioni in bronzo. Tipico del periodo medievale europeo.',
            'historical_context': 'Questo elmo apparteneva a un cavaliere del tardo medioevo. La visiera mobile permetteva una migliore visibilità durante i combattimenti.',
            'year_from': 1350,
            'year_to': 1450,
            'provenance': 'Francia settentrionale',
            'image_url': 'https://images.unsplash.com/photo-1595433707802-6b2626ef1c91?w=800',
            'conservation_state': 'Buono',
            'category_name': 'Militaria',
            'region_name': 'Europa',
            'era_name': 'Medievale',
            'materials': ['Ferro', 'Acciaio', 'Bronzo']
        },
        {
            'title': 'Copricapo Cerimoniale Inca',
            'description': 'Copricapo in piume colorate e oro, utilizzato durante le cerimonie religiose dell\'impero Inca.',
            'historical_context': 'Questo copricapo era indossato dai sacerdoti durante le cerimonie solari. Le piume di quetzal erano considerate sacre.',
            'year_from': 1400,
            'year_to': 1530,
            'provenance': 'Perù, Ande',
            'image_url': 'https://images.unsplash.com/photo-1583225214464-9296029427aa?w=800',
            'conservation_state': 'Discreto',
            'category_name': 'Cerimoniale',
            'region_name': 'Europa',  # Usiamo una regione esistente come placeholder
            'era_name': 'Medievale',
            'materials': ['Oro', 'Tessuto']
        },
        {
            'title': 'Turban Ottomano con Gioielli',
            'description': 'Turban elaborato in seta con decorazioni in oro e pietre preziose. Indossato da dignitari ottomani.',
            'historical_context': 'I turbanti ottomani erano simboli di status sociale. Questo esemplare apparteneva probabilmente a un visir o alto funzionario.',
            'year_from': 1600,
            'year_to': 1750,
            'provenance': 'Istanbul, Turchia',
            'image_url': 'https://images.unsplash.com/photo-1600298881974-6be191ceeda1?w=800',
            'conservation_state': 'Ottimo',
            'category_name': 'Abbigliamento',
            'region_name': 'Europa',
            'era_name': 'Rinascimento',
            'materials': ['Seta', 'Oro']
        },
        {
            'title': 'Maschera da Guerra Maori',
            'description': 'Maschera intagliata in legno con decorazioni tradizionali maori. Utilizzata durante le cerimonie di guerra.',
            'historical_context': 'Le maschere maori erano parte integrante della cultura guerriera. Questa maschera rappresenta un ancestore protettore.',
            'year_from': 1700,
            'year_to': 1850,
            'provenance': 'Nuova Zelanda',
            'image_url': 'https://images.unsplash.com/photo-1582719471137-c3967ffb6b42?w=800',
            'conservation_state': 'Buono',
            'category_name': 'Cerimoniale',
            'region_name': 'Europa',
            'era_name': 'Moderno',
            'materials': ['Legno']
        },
        {
            'title': 'Cappello da Mandarino Cinese',
            'description': 'Copricapo ufficiale in seta nera con decorazioni in giada e perle. Indossato dai funzionari imperiali.',
            'historical_context': 'I cappelli da mandarino indicavano il rango nella gerarchia imperiale cinese. Questo esemplare apparteneva a un funzionario di alto livello.',
            'year_from': 1700,
            'year_to': 1900,
            'provenance': 'Pechino, Cina',
            'image_url': 'https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?w=800',
            'conservation_state': 'Ottimo',
            'category_name': 'Cerimoniale',
            'region_name': 'Asia Orientale',
            'era_name': 'Moderno',
            'materials': ['Seta', 'Oro']
        },
        {
            'title': 'Elmo da Guerriero Vichingo',
            'description': 'Elmo in ferro con protezioni nasali e oculari. Caratteristico dei guerrieri vichinghi.',
            'historical_context': 'Gli elmi vichinghi erano semplici ma efficaci. Questo esemplare presenta decorazioni che indicano un guerriero di alto rango.',
            'year_from': 800,
            'year_to': 1000,
            'provenance': 'Svezia',
            'image_url': 'https://images.unsplash.com/photo-1595433707802-6b2626ef1c91?w=800',
            'conservation_state': 'Restaurato',
            'category_name': 'Militaria',
            'region_name': 'Europa',
            'era_name': 'Medievale',
            'materials': ['Ferro', 'Bronzo']
        },
        {
            'title': 'Copricapo da Capo Nativo Americano',
            'description': 'Copricapo in piume di aquila con decorazioni in perline e pelli. Simbolo di leadership.',
            'historical_context': 'I copricapi da capo erano riservati ai leader tribali. Ogni piuma rappresentava un atto di coraggio.',
            'year_from': 1800,
            'year_to': 1900,
            'provenance': 'Grandi Pianure, USA',
            'image_url': 'https://images.unsplash.com/photo-1583225214464-9296029427aa?w=800',
            'conservation_state': 'Buono',
            'category_name': 'Cerimoniale',
            'region_name': 'Europa',
            'era_name': 'Moderno',
            'materials': ['Tessuto']
        },
        {
            'title': 'Elmo da Samurai con Maschera',
            'description': 'Elmo (kabuto) completo con maschera facciale (mempo) decorata. Parte di un\'armatura da samurai.',
            'historical_context': 'Gli elmi samurai erano opere d\'arte oltre che protezioni. Questo esemplare presenta decorazioni che indicano un clan prestigioso.',
            'year_from': 1650,
            'year_to': 1750,
            'provenance': 'Edo, Giappone',
            'image_url': 'https://images.unsplash.com/photo-1595433707802-6b2626ef1c91?w=800',
            'conservation_state': 'Ottimo',
            'category_name': 'Militaria',
            'region_name': 'Asia Orientale',
            'era_name': 'Periodo Edo',
            'materials': ['Ferro', 'Acciaio', 'Oro', 'Seta']
        },
        {
            'title': 'Turban Sikh con Decorazioni',
            'description': 'Turban tradizionale sikh in tessuto pregiato con decorazioni in filo d\'oro.',
            'historical_context': 'Il turban è un simbolo importante nella cultura sikh. Questo esemplare era indossato durante cerimonie religiose importanti.',
            'year_from': 1850,
            'year_to': 1950,
            'provenance': 'Punjab, India',
            'image_url': 'https://images.unsplash.com/photo-1600298881974-6be191ceeda1?w=800',
            'conservation_state': 'Buono',
            'category_name': 'Abbigliamento',
            'region_name': 'Asia Orientale',
            'era_name': 'Moderno',
            'materials': ['Tessuto', 'Oro']
        },
        {
            'title': 'Maschera Cerimoniale Africana Dan',
            'description': 'Maschera in legno intagliato con decorazioni in metallo. Utilizzata nelle cerimonie di iniziazione.',
            'historical_context': 'Le maschere Dan sono parte integrante della cultura spirituale dell\'Africa occidentale. Questa maschera rappresenta uno spirito protettore.',
            'year_from': 1900,
            'year_to': 1950,
            'provenance': 'Costa d\'Avorio',
            'image_url': 'https://images.unsplash.com/photo-1582719471137-c3967ffb6b42?w=800',
            'conservation_state': 'Buono',
            'category_name': 'Cerimoniale',
            'region_name': 'Africa Occidentale',
            'era_name': 'Moderno',
            'materials': ['Legno']
        },
        {
            'title': 'Cappello da Ufficiale Britannico',
            'description': 'Cappello in feltro nero con piuma e decorazioni dorate. Indossato da ufficiali dell\'esercito britannico.',
            'historical_context': 'Questo cappello apparteneva a un ufficiale dell\'esercito britannico durante l\'epoca coloniale. Le decorazioni indicano il reggimento di appartenenza.',
            'year_from': 1850,
            'year_to': 1900,
            'provenance': 'Londra, Inghilterra',
            'image_url': 'https://images.unsplash.com/photo-1580910051074-3eb694886505?w=800',
            'conservation_state': 'Ottimo',
            'category_name': 'Militaria',
            'region_name': 'Europa',
            'era_name': 'Moderno',
            'materials': ['Tessuto']
        },
        {
            'title': 'Copricapo da Sciamano Siberiano',
            'description': 'Copricapo in pelliccia e piume con decorazioni in metallo. Utilizzato durante i rituali sciamanici.',
            'historical_context': 'I copricapi da sciamano erano strumenti sacri per comunicare con gli spiriti. Questo esemplare proviene dalla Siberia orientale.',
            'year_from': 1700,
            'year_to': 1900,
            'provenance': 'Siberia, Russia',
            'image_url': 'https://images.unsplash.com/photo-1600298881974-6be191ceeda1?w=800',
            'conservation_state': 'Discreto',
            'category_name': 'Cerimoniale',
            'region_name': 'Europa',
            'era_name': 'Moderno',
            'materials': ['Tessuto']
        },
        {
            'title': 'Elmo da Cavaliere Templare',
            'description': 'Elmo conico in acciaio con croce templare incisa. Caratteristico dei cavalieri templari.',
            'historical_context': 'I cavalieri templari erano un ordine monastico-militare. Questo elmo presenta la caratteristica croce templare.',
            'year_from': 1100,
            'year_to': 1300,
            'provenance': 'Terra Santa',
            'image_url': 'https://images.unsplash.com/photo-1595433707802-6b2626ef1c91?w=800',
            'conservation_state': 'Restaurato',
            'category_name': 'Militaria',
            'region_name': 'Europa',
            'era_name': 'Medievale',
            'materials': ['Acciaio', 'Ferro']
        },
        {
            'title': 'Copricapo da Principessa Etiope',
            'description': 'Copricapo in argento e oro con decorazioni in pietre preziose. Indossato dalle principesse etiopi.',
            'historical_context': 'Questo copricapo faceva parte del corredo nuziale di una principessa etiope. Le decorazioni in oro e argento indicano lo status reale.',
            'year_from': 1800,
            'year_to': 1900,
            'provenance': 'Etiopia',
            'image_url': 'https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?w=800',
            'conservation_state': 'Ottimo',
            'category_name': 'Cerimoniale',
            'region_name': 'Africa Occidentale',
            'era_name': 'Moderno',
            'materials': ['Oro', 'Argento']
        },
        {
            'title': 'Maschera Noh Giapponese',
            'description': 'Maschera teatrale Noh in legno laccato. Rappresenta un personaggio del teatro tradizionale giapponese.',
            'historical_context': 'Le maschere Noh sono utilizzate nel teatro tradizionale giapponese. Questa maschera rappresenta un demone (oni) e risale al periodo Edo.',
            'year_from': 1700,
            'year_to': 1800,
            'provenance': 'Kyoto, Giappone',
            'image_url': 'https://images.unsplash.com/photo-1582719471137-c3967ffb6b42?w=800',
            'conservation_state': 'Buono',
            'category_name': 'Cerimoniale',
            'region_name': 'Asia Orientale',
            'era_name': 'Periodo Edo',
            'materials': ['Legno']
        },
        {
            'title': 'Elmo da Gladiatore Romano',
            'description': 'Elmo in bronzo con protezioni laterali e cresta. Utilizzato dai gladiatori nell\'arena.',
            'historical_context': 'Gli elmi da gladiatore erano progettati per essere spettacolari oltre che protettivi. Questo esemplare apparteneva a un mirmillone.',
            'year_from': 50,
            'year_to': 200,
            'provenance': 'Roma, Italia',
            'image_url': 'https://images.unsplash.com/photo-1595433707802-6b2626ef1c91?w=800',
            'conservation_state': 'Restaurato',
            'category_name': 'Militaria',
            'region_name': 'Europa',
            'era_name': 'Medievale',
            'materials': ['Bronzo', 'Ferro']
        },
        {
            'title': 'Copricapo da Derviscio Sufi',
            'description': 'Copricapo conico in feltro bianco. Indossato dai dervisci durante le cerimonie di danza rotante.',
            'historical_context': 'I dervisci sufi utilizzano questo copricapo durante le loro danze mistiche. Il colore bianco simboleggia la purezza spirituale.',
            'year_from': 1500,
            'year_to': 1800,
            'provenance': 'Turchia',
            'image_url': 'https://images.unsplash.com/photo-1600298881974-6be191ceeda1?w=800',
            'conservation_state': 'Buono',
            'category_name': 'Arte Sacra',
            'region_name': 'Europa',
            'era_name': 'Rinascimento',
            'materials': ['Tessuto']
        },
        {
            'title': 'Maschera da Guerra Azteca',
            'description': 'Maschera in legno e giada con decorazioni in oro. Utilizzata durante le cerimonie di guerra azteche.',
            'historical_context': 'Le maschere azteche erano parte integrante della cultura guerriera. Questa maschera rappresenta il dio della guerra Huitzilopochtli.',
            'year_from': 1400,
            'year_to': 1520,
            'provenance': 'Messico',
            'image_url': 'https://images.unsplash.com/photo-1582719471137-c3967ffb6b42?w=800',
            'conservation_state': 'Discreto',
            'category_name': 'Cerimoniale',
            'region_name': 'Europa',
            'era_name': 'Medievale',
            'materials': ['Legno', 'Oro']
        },
        {
            'title': 'Cappello da Mandarino Coreano',
            'description': 'Copricapo ufficiale in seta nera con decorazioni in giada. Indossato dai funzionari della corte coreana.',
            'historical_context': 'I cappelli da mandarino coreani erano simili a quelli cinesi ma con caratteristiche distintive. Questo esemplare apparteneva a un funzionario della dinastia Joseon.',
            'year_from': 1600,
            'year_to': 1900,
            'provenance': 'Seoul, Corea',
            'image_url': 'https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?w=800',
            'conservation_state': 'Ottimo',
            'category_name': 'Cerimoniale',
            'region_name': 'Asia Orientale',
            'era_name': 'Moderno',
            'materials': ['Seta', 'Oro']
        },
        {
            'title': 'Elmo da Cavaliere Crociato',
            'description': 'Elmo conico in acciaio con croce incisa. Caratteristico dei cavalieri crociati.',
            'historical_context': 'I cavalieri crociati indossavano elmi distintivi con simboli cristiani. Questo esemplare presenta la croce dei cavalieri templari.',
            'year_from': 1100,
            'year_to': 1300,
            'provenance': 'Terra Santa',
            'image_url': 'https://images.unsplash.com/photo-1595433707802-6b2626ef1c91?w=800',
            'conservation_state': 'Restaurato',
            'category_name': 'Militaria',
            'region_name': 'Europa',
            'era_name': 'Medievale',
            'materials': ['Acciaio', 'Ferro']
        },
        {
            'title': 'Copricapo da Capo Polinesiano',
            'description': 'Copricapo in piume colorate e conchiglie. Simbolo di leadership nelle isole del Pacifico.',
            'historical_context': 'I copricapi da capo polinesiani erano riservati ai leader tribali. Le piume colorate indicavano lo status e il potere spirituale.',
            'year_from': 1700,
            'year_to': 1900,
            'provenance': 'Hawaii',
            'image_url': 'https://images.unsplash.com/photo-1583225214464-9296029427aa?w=800',
            'conservation_state': 'Buono',
            'category_name': 'Cerimoniale',
            'region_name': 'Europa',
            'era_name': 'Moderno',
            'materials': ['Tessuto']
        },
        {
            'title': 'Maschera da Teatro Kabuki',
            'description': 'Maschera teatrale Kabuki in legno laccato. Rappresenta un personaggio del teatro tradizionale giapponese.',
            'historical_context': 'Le maschere Kabuki sono utilizzate nel teatro tradizionale giapponese. Questa maschera rappresenta un demone e risale al periodo Edo.',
            'year_from': 1700,
            'year_to': 1800,
            'provenance': 'Tokyo, Giappone',
            'image_url': 'https://images.unsplash.com/photo-1582719471137-c3967ffb6b42?w=800',
            'conservation_state': 'Buono',
            'category_name': 'Cerimoniale',
            'region_name': 'Asia Orientale',
            'era_name': 'Periodo Edo',
            'materials': ['Legno']
        },
        {
            'title': 'Elmo da Cavaliere Spagnolo',
            'description': 'Elmo in acciaio con visiera mobile e decorazioni in oro. Tipico dei cavalieri spagnoli del Rinascimento.',
            'historical_context': 'Questo elmo apparteneva a un cavaliere spagnolo durante il periodo del Rinascimento. Le decorazioni in oro indicano lo status elevato.',
            'year_from': 1500,
            'year_to': 1600,
            'provenance': 'Spagna',
            'image_url': 'https://images.unsplash.com/photo-1595433707802-6b2626ef1c91?w=800',
            'conservation_state': 'Ottimo',
            'category_name': 'Militaria',
            'region_name': 'Europa',
            'era_name': 'Rinascimento',
            'materials': ['Acciaio', 'Oro']
        },
        {
            'title': 'Copricapo da Sciamano Mongolo',
            'description': 'Copricapo in pelliccia e piume con decorazioni in metallo. Utilizzato durante i rituali sciamanici mongoli.',
            'historical_context': 'I copricapi da sciamano mongoli erano strumenti sacri per comunicare con gli spiriti. Questo esemplare proviene dalla Mongolia interna.',
            'year_from': 1600,
            'year_to': 1900,
            'provenance': 'Mongolia',
            'image_url': 'https://images.unsplash.com/photo-1600298881974-6be191ceeda1?w=800',
            'conservation_state': 'Discreto',
            'category_name': 'Cerimoniale',
            'region_name': 'Asia Orientale',
            'era_name': 'Moderno',
            'materials': ['Tessuto']
        }
    ]
    
    # Aggiungi gli oggetti al database
    added_count = 0
    for item_data in new_items_data:
        # Trova categoria, regione ed era per nome
        category = next((c for c in categories if c.name == item_data['category_name']), None)
        region = next((r for r in regions if r.name == item_data['region_name']), None)
        era = next((e for e in eras if e.name == item_data['era_name']), None)
        
        if not category or not region or not era:
            print(f"⚠️  Saltato '{item_data['title']}': categoria, regione o era non trovata")
            continue
        
        # Trova i materiali per nome
        item_materials = [m for m in materials if m.name in item_data['materials']]
        
        # Crea l'oggetto
        item = Item(
            title=item_data['title'],
            description=item_data['description'],
            historical_context=item_data['historical_context'],
            year_from=item_data['year_from'],
            year_to=item_data['year_to'],
            provenance=item_data['provenance'],
            image_url=item_data['image_url'],
            conservation_state=item_data['conservation_state'],
            category=category,
            region=region,
            era=era
        )
        
        # Aggiungi i materiali
        for material in item_materials:
            item.materials.append(material)
        
        db.session.add(item)
        added_count += 1
    
    # Salva nel database
    db.session.commit()
    print(f"✓ {added_count} nuovi oggetti aggiunti alla collezione")
    print("\n=== Completato! ===")
    print("Puoi ora visualizzare i nuovi oggetti nella collezione.")


if __name__ == '__main__':
    with app.app_context():
        add_new_items()

