"""
Da ogni capo del mondo - Digital Museum
Main Flask application with routes and business logic
"""
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session, send_file, send_from_directory
from functools import wraps
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import or_, and_, func, desc
from models import (db, Item, Category, Region, Material, Era, User, PrivateNote, Loan,
                    Exhibition, ItemImage, ItemDocument, ItemValuation, ItemQRCode, Notification)
from config import config
from datetime import datetime, date, timedelta
import os
import json
from pathlib import Path
from werkzeug.utils import secure_filename
from PIL import Image
import qrcode
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config['development'])
app.config['BASE_DIR'] = Path(__file__).resolve().parent

# Initialize database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Per favore, effettua il login per accedere a questa area.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Simple i18n helper (without Babel for now)
def get_locale():
    """Get current language from session"""
    return session.get('language', 'it')

def _(text):
    """Simple translation function - returns text as-is for now"""
    # In a full implementation, this would use Babel or a translation dictionary
    return text

# Make _ available to templates
app.jinja_env.globals['_'] = _

# Jinja2 filter for image URLs
@app.template_filter('image_url')
def image_url_filter(image_path):
    """Convert image path to proper URL (handles both absolute URLs and relative paths)"""
    if not image_path:
        return ''
    # If it's already an absolute URL (http/https), return as is
    if image_path.startswith('http://') or image_path.startswith('https://'):
        return image_path
    # Otherwise, treat it as a static file path
    # Flask's url_for handles URL encoding automatically for spaces and special characters
    try:
        return url_for('static', filename=image_path)
    except:
        # Fallback: return the path as-is if url_for fails (shouldn't happen in request context)
        return f'/static/{image_path}'


# ===== ROUTES =====

@app.route('/')
def home():
    """Homepage - Landing page with featured items and globe preview"""
    # Get 3 random items (or last 3 added) for featured section
    featured_items = Item.query.order_by(Item.created_at.desc()).limit(3).all()
    
    # If we have less than 3 items, get all available
    if len(featured_items) < 3:
        featured_items = Item.query.limit(3).all()
    
    # Get globe data for preview
    from sqlalchemy import func
    
    regions = Region.query.all()
    
    # Geographic coordinates for each region (same as globe page)
    region_coords = {
        'Asia Orientale': {'lat': 35.0, 'lng': 105.0},
        'Himalaya': {'lat': 28.0, 'lng': 84.0},
        'Africa Occidentale': {'lat': 8.0, 'lng': -2.0},
        'Europa': {'lat': 50.0, 'lng': 10.0},
        'Asia': {'lat': 34.0, 'lng': 100.0},
        'Africa': {'lat': 0.0, 'lng': 20.0},
        'Americhe': {'lat': 10.0, 'lng': -75.0},
        'Oceania': {'lat': -25.0, 'lng': 140.0}
    }
    
    region_data = []
    total_items = 0
    
    for region in regions:
        items = region.items.all()
        if not items:
            continue
            
        coords = region_coords.get(region.name, {'lat': 0, 'lng': 0})
        
        eras = set()
        for item in items:
            if item.era:
                eras.add(item.era.name)
        
        items_data = []
        for item in items[:3]:  # Limit to 3 items for preview
            items_data.append({
                'id': item.id,
                'title': item.title,
                'image_url': item.image_url,
                'category': item.category.name if item.category else None,
                'era': item.era.name if item.era else None
            })
        
        region_data.append({
            'id': region.id,
            'name': region.name,
            'lat': coords['lat'],
            'lng': coords['lng'],
            'item_count': len(items),
            'unique_eras': len(eras),
            'items': items_data
        })
        
        total_items += len(items)
    
    # Ensure we always have valid values
    if not region_data:
        region_data = []
    if total_items is None:
        total_items = 0
    
    return render_template('index.html', 
                         featured_items=featured_items,
                         globe_region_data=region_data,
                         globe_total_items=total_items,
                         globe_total_regions=len(region_data))


@app.route('/collezione')
def collezione():
    """Collection page - Full collection with filters and search"""
    page = request.args.get('page', 1, type=int)
    per_page = app.config['ITEMS_PER_PAGE']
    search_query = request.args.get('q', '').strip()
    
    # Build query
    query = Item.query
    
    # Full-text search
    if search_query:
        search_term = f'%{search_query}%'
        query = query.filter(
            or_(
                Item.title.ilike(search_term),
                Item.description.ilike(search_term),
                Item.historical_context.ilike(search_term),
                Item.provenance.ilike(search_term)
            )
        )
    
    # Get filter parameters
    category_id = request.args.get('category', type=int)
    region_id = request.args.get('region', type=int)
    material_id = request.args.get('material', type=int)
    era_id = request.args.get('era', type=int)
    
    # Apply filters
    if category_id:
        query = query.filter(Item.category_id == category_id)
    if region_id:
        query = query.filter(Item.region_id == region_id)
    if era_id:
        query = query.filter(Item.era_id == era_id)
    if material_id:
        query = query.join(Item.materials).filter(Material.id == material_id)
    
    # Order and paginate
    query = query.order_by(Item.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    items = pagination.items
    
    # Get filter options
    categories = Category.query.all()
    regions = Region.query.all()
    materials = Material.query.all()
    eras = Era.query.all()
    
    # Active filters for display
    active_filters = {
        'category': category_id,
        'region': region_id,
        'material': material_id,
        'era': era_id
    }
    
    return render_template('collezione.html',
                         items=items,
                         pagination=pagination,
                         categories=categories,
                         regions=regions,
                         materials=materials,
                         eras=eras,
                         search_query=search_query,
                         active_filters=active_filters)


@app.route('/item/<int:item_id>')
def item_detail(item_id):
    """Detailed view of a single object"""
    item = Item.query.get_or_404(item_id)
    
    # Increment view count
    item.view_count += 1
    db.session.commit()
    
    # Get related items (same category or region)
    related = Item.query.filter(
        and_(
            Item.id != item_id,
            or_(
                Item.category_id == item.category_id,
                Item.region_id == item.region_id
            )
        )
    ).limit(4).all()
    
    return render_template('detail.html', item=item, related=related)


@app.route('/material/<int:material_id>')
def material_detail(material_id):
    """Detailed view of a material with properties, uses, and historical significance"""
    material = Material.query.get_or_404(material_id)
    
    # Get all items that use this material
    items_with_material = Item.query.join(Item.materials).filter(
        Material.id == material_id
    ).limit(12).all()
    
    # Material details dictionary (can be extended to database fields later)
    material_details = {
        'Ferro': {
            'properties': 'Il ferro è un metallo duttile e malleabile, facilmente lavorabile quando riscaldato. Ha una buona resistenza meccanica e può essere temprato per aumentare la durezza.',
            'quality': 'Materiale robusto e resistente, ideale per oggetti che richiedono durabilità. Tende ad arrugginire se non protetto.',
            'historical_uses': 'Utilizzato fin dall\'antichità per armi, armature, strumenti e oggetti d\'uso quotidiano. Il ferro battuto era la tecnica principale per forgiare oggetti complessi.',
            'significance': 'Il ferro ha rivoluzionato la produzione di armi e armature, permettendo la creazione di protezioni più efficaci e armi più affilate. La sua lavorazione richiedeva grande maestria artigianale.'
        },
        'Acciaio': {
            'properties': 'L\'acciaio è una lega di ferro e carbonio, più duro e resistente del ferro puro. Può essere temprato e rinvenuto per ottenere diverse proprietà meccaniche.',
            'quality': 'Materiale di alta qualità, superiore al ferro per durezza e resistenza. Ideale per armi e armature di pregio.',
            'historical_uses': 'Utilizzato per creare le migliori armi e armature, specialmente per cavalieri e samurai. L\'acciaio damascato era particolarmente pregiato.',
            'significance': 'L\'acciaio rappresentava il culmine della metallurgia antica. Le tecniche di forgiatura dell\'acciaio erano segreti custoditi gelosamente dagli artigiani.'
        },
        'Oro': {
            'properties': 'L\'oro è un metallo prezioso, malleabile, duttile e resistente alla corrosione. Ha un colore caratteristico e un\'elevata lucentezza.',
            'quality': 'Materiale di lusso per eccellenza, simbolo di ricchezza e potere. Non si ossida e mantiene la sua bellezza nel tempo.',
            'historical_uses': 'Utilizzato per decorazioni, gioielli, oggetti cerimoniali e simboli di status. L\'oro era riservato a re, nobili e oggetti sacri.',
            'significance': 'L\'oro ha sempre rappresentato potere, divinità e immortalità. La sua incorruttibilità lo rendeva simbolo di eternità in molte culture.'
        },
        'Argento': {
            'properties': 'L\'argento è un metallo prezioso, molto malleabile e con la migliore conducibilità elettrica e termica tra tutti i metalli. Ha una lucentezza caratteristica.',
            'quality': 'Materiale pregiato, più accessibile dell\'oro ma comunque simbolo di ricchezza. Tende ad ossidarsi formando una patina scura.',
            'historical_uses': 'Utilizzato per gioielli, monete, oggetti cerimoniali e decorazioni. L\'argento aveva anche proprietà antibatteriche riconosciute.',
            'significance': 'L\'argento era associato alla luna e alla purezza in molte culture. Era utilizzato per oggetti sacri e cerimoniali.'
        },
        'Tessuto': {
            'properties': 'I tessuti sono materiali flessibili realizzati mediante intreccio di fibre. Possono essere naturali (lana, cotone) o sintetici.',
            'quality': 'Materiale versatile e confortevole, adatto a molti usi. La qualità dipende dal tipo di fibra e dalla lavorazione.',
            'historical_uses': 'Utilizzato per abbigliamento, copricapi, decorazioni e oggetti cerimoniali. I tessuti pregiati erano simbolo di status.',
            'significance': 'I tessuti hanno sempre rappresentato cultura e tradizione. I motivi e le tecniche di tessitura erano trasmessi di generazione in generazione.'
        },
        'Seta': {
            'properties': 'La seta è una fibra proteica naturale prodotta dal baco da seta. È liscia, lucente, resistente e ha eccellenti proprietà termiche.',
            'quality': 'Materiale di lusso per eccellenza, morbido, elegante e pregiato. La seta era riservata ai ceti più elevati.',
            'historical_uses': 'Utilizzata per abiti cerimoniali, kimono, turbanti e oggetti di pregio. La Via della Seta collegava Oriente e Occidente.',
            'significance': 'La seta era così preziosa da essere usata come moneta. I segreti della sua produzione erano custoditi gelosamente in Cina per secoli.'
        },
        'Legno': {
            'properties': 'Il legno è un materiale organico, leggero ma resistente, facilmente lavorabile. Ogni essenza ha caratteristiche uniche.',
            'quality': 'Materiale versatile e naturale, la qualità dipende dall\'essenza e dalla stagionatura. Può durare secoli se ben conservato.',
            'historical_uses': 'Utilizzato per maschere, sculture, mobili, strumenti e oggetti cerimoniali. Il legno intagliato era una forma d\'arte importante.',
            'significance': 'Il legno era il materiale più accessibile e lavorabile. Le tecniche di intaglio e scultura erano trasmesse da maestro ad allievo.'
        },
        'Turchese': {
            'properties': 'Il turchese è una pietra preziosa di colore azzurro-verde, opaca o semi-trasparente. È relativamente morbida e porosa.',
            'quality': 'Pietra preziosa di media durezza, apprezzata per il suo colore caratteristico. Richiede protezione da sostanze chimiche.',
            'historical_uses': 'Utilizzata in gioielli, decorazioni e oggetti cerimoniali, specialmente in Tibet, Persia e nelle Americhe. Simbolo di cielo e spiritualità.',
            'significance': 'Il turchese era considerato una pietra sacra in molte culture. In Tibet era associata al cielo e alla protezione spirituale.'
        },
        'Corallo': {
            'properties': 'Il corallo è un materiale organico marino, duro e compatto. Ha colori che vanno dal rosa al rosso intenso.',
            'quality': 'Materiale pregiato e raro, apprezzato per il suo colore e la sua lucentezza. Richiede protezione da calore e sostanze acide.',
            'historical_uses': 'Utilizzato in gioielli, decorazioni e oggetti cerimoniali. Il corallo rosso era particolarmente pregiato nel Mediterraneo e in Asia.',
            'significance': 'Il corallo era considerato un amuleto protettivo. In molte culture era associato alla vitalità e alla protezione dal male.'
        },
        'Bronzo': {
            'properties': 'Il bronzo è una lega di rame e stagno, dura, resistente alla corrosione e facilmente lavorabile. Ha un colore caratteristico dorato-rossastro.',
            'quality': 'Materiale di alta qualità per l\'antichità, superiore al rame puro. Ideale per armi, armature e oggetti decorativi.',
            'historical_uses': 'Utilizzato fin dall\'Età del Bronzo per armi, armature, strumenti e oggetti d\'arte. Il bronzo era il materiale principale per le armature antiche.',
            'significance': 'Il bronzo segnò l\'inizio dell\'età dei metalli. Le tecniche di fusione del bronzo permisero la creazione di oggetti complessi e decorativi.'
        }
    }
    
    # Get material details or use default
    details = material_details.get(material.name, {
        'properties': material.description or 'Materiale utilizzato nella produzione di oggetti storici e artistici.',
        'quality': 'Materiale di qualità variabile a seconda della lavorazione e dell\'epoca.',
        'historical_uses': 'Utilizzato in vari contesti storici per la produzione di oggetti d\'arte, armi, armature e oggetti cerimoniali.',
        'significance': 'Materiale di importanza storica e culturale nella produzione di oggetti d\'arte e uso quotidiano.'
    })
    
    return render_template('material.html', 
                         material=material, 
                         items=items_with_material,
                         details=details)


@app.route('/era/<int:era_id>')
def era_detail(era_id):
    """Detailed view of an era with historical context and connection to collection items"""
    era = Era.query.get_or_404(era_id)
    
    # Get all items from this era
    items_from_era = Item.query.filter(Item.era_id == era_id).limit(12).all()
    
    # Get current item from query parameter (if coming from item detail page)
    current_item_id = request.args.get('item_id', type=int)
    current_item = None
    if current_item_id:
        current_item = Item.query.get(current_item_id)
    
    # Era details dictionary with comprehensive information
    era_details = {
        'Medievale': {
            'description': 'Il Medioevo è un periodo storico che si estende dal V al XV secolo, caratterizzato dalla caduta dell\'Impero Romano d\'Occidente fino all\'inizio del Rinascimento. Fu un\'epoca di grandi trasformazioni sociali, politiche e culturali.',
            'characteristics': 'Caratterizzato da sistema feudale, forte influenza della Chiesa, sviluppo dell\'arte romanica e gotica, crociate, e nascita delle prime università. L\'artigianato raggiunse livelli di eccellenza nella produzione di armi, armature e oggetti cerimoniali.',
            'historical_context': 'Il periodo medievale vide la frammentazione politica dell\'Europa, l\'ascesa del potere papale, le invasioni barbariche, e la nascita degli stati nazionali. Fu un\'epoca di guerre, ma anche di grande sviluppo tecnologico e artistico.',
            'cultural_significance': 'Il Medioevo gettò le basi per la cultura europea moderna. L\'arte, l\'architettura, la letteratura e l\'artigianato di questo periodo riflettono valori di onore, fede e maestria. Gli oggetti prodotti erano spesso simboli di status e potere.'
        },
        'Rinascimento': {
            'description': 'Il Rinascimento, dal XIV al XVI secolo, segnò una rinascita culturale e artistica in Europa. Fu caratterizzato da un rinnovato interesse per l\'antichità classica, l\'umanesimo e l\'innovazione artistica e scientifica.',
            'characteristics': 'Caratterizzato da riscoperta dell\'antichità classica, sviluppo dell\'umanesimo, innovazioni artistiche (prospettiva, anatomia), mecenatismo delle corti, e grande attenzione alla bellezza e all\'eleganza. L\'artigianato raggiunse livelli di raffinatezza senza precedenti.',
            'historical_context': 'Il Rinascimento coincise con grandi scoperte geografiche, la Riforma protestante, e l\'ascesa delle signorie italiane. Fu un periodo di grande prosperità economica e culturale, con corti che competevano per il prestigio attraverso l\'arte e gli oggetti di lusso.',
            'cultural_significance': 'Il Rinascimento rappresenta l\'apice dell\'artigianato europeo. Oggetti come armature, gioielli e abiti erano vere opere d\'arte, riflettendo i valori di bellezza, eleganza e prestigio. La maestria artigianale era considerata una forma d\'arte superiore.'
        },
        'Periodo Edo': {
            'description': 'Il Periodo Edo (1603-1868) fu un\'epoca di pace e stabilità in Giappone sotto lo shogunato Tokugawa. Caratterizzato da isolamento dal resto del mondo (sakoku) e sviluppo di una cultura distintivamente giapponese.',
            'characteristics': 'Caratterizzato da rigida gerarchia sociale (samurai, contadini, artigiani, mercanti), sviluppo delle arti tradizionali (teatro Noh, Kabuki, ukiyo-e), perfezionamento dell\'artigianato, e codificazione di rituali e cerimonie. L\'estetica wabi-sabi raggiunse la sua massima espressione.',
            'historical_context': 'Dopo secoli di guerre civili, il Giappone visse 250 anni di pace sotto lo shogunato Tokugawa. L\'isolamento favorì lo sviluppo di una cultura unica, mentre l\'economia fiorì grazie al commercio interno e all\'artigianato di qualità.',
            'cultural_significance': 'Il Periodo Edo rappresenta l\'apice della cultura tradizionale giapponese. Oggetti come kimono, maschere teatrali, armature samurai e oggetti cerimoniali riflettono valori di onore, disciplina, estetica e maestria artigianale. Ogni oggetto aveva un significato profondo nella società gerarchica.'
        },
        'Epoca Napoleonica': {
            'description': 'L\'Epoca Napoleonica (1799-1815) fu un periodo di grandi trasformazioni in Europa sotto l\'influenza di Napoleone Bonaparte. Caratterizzata da guerre, riforme amministrative e diffusione degli ideali rivoluzionari.',
            'characteristics': 'Caratterizzata da uniformi militari elaborate, simboli imperiali (aquila, api, N), stile neoclassico nell\'arte e nell\'architettura, e grande attenzione alla gerarchia e alle decorazioni. L\'abbigliamento e gli accessori militari erano simboli di status e potere.',
            'historical_context': 'Dopo la Rivoluzione Francese, Napoleone creò un impero che si estese su gran parte dell\'Europa. Le guerre napoleoniche diffusero nuovi ideali e stili, mentre l\'esercito divenne il centro della società, con uniformi e decorazioni che riflettevano il rango e il prestigio.',
            'cultural_significance': 'L\'Epoca Napoleonica rappresenta la transizione tra antico regime e modernità. Gli oggetti militari, come cappelli, uniformi e decorazioni, erano simboli di potere e prestigio. Lo stile neoclassico influenzò l\'arte e l\'artigianato di tutta Europa.'
        },
        'Moderno': {
            'description': 'L\'epoca moderna (1800-1950) fu caratterizzata da rivoluzione industriale, espansione coloniale, guerre mondiali e grandi trasformazioni sociali. Fu un periodo di contatto tra culture diverse e di cambiamenti rapidi.',
            'characteristics': 'Caratterizzata da industrializzazione, espansione coloniale, contatto tra culture, sviluppo di nuove tecnologie, e preservazione delle tradizioni locali. Gli oggetti riflettono sia tradizioni antiche che influenze moderne, con artigianato che si adatta ai nuovi tempi.',
            'historical_context': 'L\'epoca moderna vide l\'ascesa delle potenze coloniali europee, la rivoluzione industriale, le guerre mondiali, e il contatto sempre più frequente tra culture diverse. Molti oggetti tradizionali furono preservati mentre altri si adattarono ai nuovi contesti.',
            'cultural_significance': 'L\'epoca moderna rappresenta un momento di transizione cruciale. Gli oggetti di questo periodo riflettono sia la preservazione delle tradizioni antiche che l\'influenza della modernità. Sono testimonianze di culture in trasformazione, dove l\'artigianato tradizionale convive con nuove influenze e tecnologie.'
        }
    }
    
    # Get era details or use default
    details = era_details.get(era.name, {
        'description': era.description or 'Epoca storica caratterizzata da sviluppi culturali, sociali e artistici significativi.',
        'characteristics': 'Periodo caratterizzato da sviluppi distintivi nell\'arte, nella cultura e nella società.',
        'historical_context': 'Epoca di grande importanza storica con eventi e trasformazioni significative.',
        'cultural_significance': 'Epoca che ha lasciato un\'impronta duratura sulla cultura e sull\'artigianato, influenzando la produzione di oggetti d\'arte e uso quotidiano.'
    })
    
    # Mappatura immagini epoche
    era_images = {
        'Medievale': 'medievale.jpg',
        'Rinascimento': 'rinascimento.jpg',
        'Periodo Edo': 'periodo-edo.jpg',
        'Epoca Napoleonica': 'epoca-napoleonica.jpg',
        'Moderno': 'moderno.jpg'
    }
    
    era_image = era_images.get(era.name, None)
    
    return render_template('era.html',
                         era=era,
                         items=items_from_era,
                         current_item=current_item,
                         details=details,
                         era_image=era_image)


@app.route('/epoche')
def epoche():
    """Page showing all historical eras"""
    eras = Era.query.order_by(Era.year_start.asc()).all()
    # Immagine di sfondo per la pagina Epoche (1920x1080)
    epoche_image = 'epoche.jpg'  # Assicurati di avere questa immagine in static/images/epoche/
    return render_template('epoche.html', eras=eras, epoche_image=epoche_image)


@app.route('/didattica')
def didattica():
    """Educational section landing page for schools"""
    return render_template('didattica.html')


@app.route('/didattica/percorsi')
def percorsi():
    """List of all educational paths"""
    # Percorsi didattici (hardcoded per ora, può essere migrato a DB in futuro)
    percorsi_data = [
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
    return render_template('percorsi.html', percorsi=percorsi_data)


@app.route('/didattica/percorso/<int:percorso_id>')
def percorso_detail(percorso_id):
    """Detail page for a specific educational path"""
    # Dati percorsi (hardcoded, può essere migrato a DB)
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
            ],
            'path_items': Item.query.filter(
                or_(
                    Item.category_id.in_([1]),  # Militaria
                    Item.title.like('%elmo%'),
                    Item.title.like('%armatura%'),
                    Item.title.like('%copricapo%')
                )
            ).limit(8).all()
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
            ],
            'path_items': Item.query.filter(
                Item.region_id.isnot(None)
            ).limit(10).all()
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
            ],
            'path_items': Item.query.join(Item.materials).limit(12).all()
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
                'Studio delle strategie militari per epoca',
                'Confronto tra armature di diverse culture',
                'Discussione guidata su pace e conflitto'
            ],
            'path_items': Item.query.filter(
                Item.category_id.in_([1])  # Militaria
            ).limit(10).all()
        }
    }
    
    percorso = percorsi_data.get(percorso_id)
    if not percorso:
        from flask import abort
        abort(404)
    
    return render_template('percorso-detail.html', percorso=percorso)


@app.route('/didattica/timeline')
def timeline_didattica():
    """Interactive timeline for educational purposes"""
    # Get items ordered by year
    items = Item.query.filter(Item.year_from.isnot(None)).order_by(Item.year_from.asc()).all()
    eras = Era.query.all()
    return render_template('timeline-didattica.html', items=items, eras=eras)


@app.route('/didattica/insegnanti')
def insegnanti():
    """Teachers area with educational materials"""
    return render_template('insegnanti.html')


@app.route('/filter')
def filter_items():
    """Server-side filtering with HTML response"""
    # Get filter parameters
    category_id = request.args.get('category', type=int)
    region_id = request.args.get('region', type=int)
    material_id = request.args.get('material', type=int)
    era_id = request.args.get('era', type=int)
    
    # Build query
    query = Item.query
    
    if category_id:
        query = query.filter(Item.category_id == category_id)
    if region_id:
        query = query.filter(Item.region_id == region_id)
    if era_id:
        query = query.filter(Item.era_id == era_id)
    if material_id:
        query = query.join(Item.materials).filter(Material.id == material_id)
    
    items = query.all()
    
    # Get filter options
    categories = Category.query.all()
    regions = Region.query.all()
    materials = Material.query.all()
    eras = Era.query.all()
    
    return render_template('collezione.html',
                         items=items,
                         pagination=None,
                         categories=categories,
                         regions=regions,
                         materials=materials,
                         eras=eras,
                         active_filters={
                             'category': category_id,
                             'region': region_id,
                             'material': material_id,
                             'era': era_id
                         })


@app.route('/api/filter')
def api_filter():
    """JSON API endpoint for dynamic filtering"""
    # Get filter parameters
    category_id = request.args.get('category', type=int)
    region_id = request.args.get('region', type=int)
    material_id = request.args.get('material', type=int)
    era_id = request.args.get('era', type=int)
    
    # Build query
    query = Item.query
    
    if category_id:
        query = query.filter(Item.category_id == category_id)
    if region_id:
        query = query.filter(Item.region_id == region_id)
    if era_id:
        query = query.filter(Item.era_id == era_id)
    if material_id:
        query = query.join(Item.materials).filter(Material.id == material_id)
    
    items = query.all()
    
    # Convert to JSON
    return jsonify({
        'count': len(items),
        'items': [item.to_dict() for item in items]
    })


@app.route('/globe')
def globe():
    """Interactive 3D globe view of collection by geographic region"""
    from sqlalchemy import func
    
    # Get all regions with their items
    regions = Region.query.all()
    
    # Geographic coordinates for each region (approximate center points)
    region_coords = {
        'Asia Orientale': {'lat': 35.0, 'lng': 105.0},
        'Himalaya': {'lat': 28.0, 'lng': 84.0},
        'Africa Occidentale': {'lat': 8.0, 'lng': -2.0},
        'Europa': {'lat': 50.0, 'lng': 10.0},
        'Asia': {'lat': 34.0, 'lng': 100.0},
        'Africa': {'lat': 0.0, 'lng': 20.0},
        'Americhe': {'lat': 10.0, 'lng': -75.0},
        'Oceania': {'lat': -25.0, 'lng': 140.0}
    }
    
    region_data = []
    total_items = 0
    
    for region in regions:
        items = region.items.all()
        if not items:
            continue
            
        # Get coordinates for this region
        coords = region_coords.get(region.name, {'lat': 0, 'lng': 0})
        
        # Get unique eras for this region
        eras = set()
        for item in items:
            if item.era:
                eras.add(item.era.name)
        
        # Prepare item data
        items_data = []
        for item in items:
            items_data.append({
                'id': item.id,
                'title': item.title,
                'image_url': item.image_url,
                'category': item.category.name if item.category else None,
                'era': item.era.name if item.era else None
            })
        
        region_data.append({
            'id': region.id,
            'name': region.name,
            'lat': coords['lat'],
            'lng': coords['lng'],
            'item_count': len(items),
            'unique_eras': len(eras),
            'items': items_data
        })
        
        total_items += len(items)
    
    return render_template('globe.html',
                         region_data=region_data,
                         total_regions=len(region_data),
                         total_items=total_items)


@app.route('/chi-siamo')
def chi_siamo():
    """About page - Information about the museum and collection"""
    return render_template('chi-siamo.html')


@app.route('/contatti', methods=['GET', 'POST'])
def contact():
    """Contact page with contact form"""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        privacy = request.form.get('privacy')
        
        # Basic validation
        if not all([name, email, subject, message, privacy]):
            flash('Per favore, compila tutti i campi obbligatori.', 'error')
            return render_template('contatti.html')
        
        # In a real application, you would:
        # 1. Send an email with the contact form data
        # 2. Save to database
        # 3. Send confirmation email to user
        
        # For now, just flash a success message
        flash('Messaggio inviato con successo! Ti risponderemo al più presto.', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contatti.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for family/private area"""
    if current_user.is_authenticated:
        return redirect(url_for('area_privata'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        if not username or not password:
            flash(_('Per favore, inserisci username e password.'), 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('area_privata'))
        else:
            flash(_('Username o password non corretti.'), 'error')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash(_('Logout effettuato con successo.'), 'success')
    return redirect(url_for('home'))


@app.route('/area-privata')
@login_required
def area_privata():
    """Private area dashboard for family members"""
    # Check for loans due soon
    check_loan_due_dates()
    
    # Get user's private notes
    user_notes = PrivateNote.query.filter_by(user_id=current_user.id).order_by(PrivateNote.updated_at.desc()).limit(10).all()
    
    # Get active loans
    active_loans = Loan.query.filter_by(user_id=current_user.id, status='active').order_by(Loan.start_date.desc()).all()
    
    # Get total items count
    total_items = Item.query.count()
    
    # Get unread notifications count
    unread_notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    
    # Get items with private notes
    items_with_notes = db.session.query(Item, PrivateNote).join(
        PrivateNote, Item.id == PrivateNote.item_id
    ).filter(PrivateNote.user_id == current_user.id).all()
    
    return render_template('area-privata.html',
                         user_notes=user_notes,
                         active_loans=active_loans,
                         total_items=total_items,
                         items_with_notes=items_with_notes,
                         unread_notifications=unread_notifications)


@app.route('/area-privata/note/<int:item_id>', methods=['GET', 'POST'])
@login_required
def private_note(item_id):
    """Add or edit private note for an item"""
    item = Item.query.get_or_404(item_id)
    
    if request.method == 'POST':
        note_text = request.form.get('note', '').strip()
        
        # Find existing note or create new
        existing_note = PrivateNote.query.filter_by(
            user_id=current_user.id,
            item_id=item_id
        ).first()
        
        if existing_note:
            existing_note.note = note_text
            existing_note.updated_at = datetime.utcnow()
        else:
            new_note = PrivateNote(
                user_id=current_user.id,
                item_id=item_id,
                note=note_text
            )
            db.session.add(new_note)
        
        db.session.commit()
        flash(_('Nota salvata con successo.'), 'success')
        return redirect(url_for('item_detail', item_id=item_id))
    
    # Get existing note if any
    existing_note = PrivateNote.query.filter_by(
        user_id=current_user.id,
        item_id=item_id
    ).first()
    
    return render_template('note-private.html', item=item, note=existing_note)


@app.route('/set-language/<lang>')
def set_language(lang):
    """Set language preference"""
    if lang in app.config['LANGUAGES']:
        session['language'] = lang
    return redirect(request.referrer or url_for('home'))


# ===== HELPER FUNCTIONS =====

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash(_('Accesso negato. Solo gli amministratori possono accedere a questa sezione.'), 'error')
            return redirect(url_for('area_privata'))
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def save_uploaded_image(file, item_id=None):
    """Save uploaded image and return path"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Create unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{timestamp}{ext}"
        
        # Create directory if needed
        upload_dir = app.config['UPLOAD_FOLDER'] / 'items'
        if item_id:
            upload_dir = upload_dir / str(item_id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = upload_dir / unique_filename
        file.save(str(filepath))
        
        # Resize if too large
        try:
            img = Image.open(filepath)
            if img.width > 1920 or img.height > 1920:
                img.thumbnail((1920, 1920), Image.Resampling.LANCZOS)
                img.save(filepath, optimize=True, quality=85)
        except Exception as e:
            print(f"Error resizing image: {e}")
        
        # Return relative path
        return f"images/items/{item_id if item_id else 'temp'}/{unique_filename}"
    return None


def generate_qr_code(item_id):
    """Generate QR code for an item"""
    url = f"{request.host_url}item/{item_id}"
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR code
    qr_dir = app.config['UPLOAD_FOLDER'] / 'qrcodes'
    qr_dir.mkdir(parents=True, exist_ok=True)
    qr_path = qr_dir / f"item_{item_id}.png"
    img.save(str(qr_path))
    
    return f"images/qrcodes/item_{item_id}.png"


# ===== ADMIN PANEL - CRUD OPERATIONS =====

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    total_items = Item.query.count()
    total_exhibitions = Exhibition.query.count()
    active_loans = Loan.query.filter_by(status='active').count()
    pending_notifications = Notification.query.filter_by(is_read=False).count()
    
    recent_items = Item.query.order_by(Item.created_at.desc()).limit(5).all()
    recent_exhibitions = Exhibition.query.order_by(Exhibition.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_items=total_items,
                         total_exhibitions=total_exhibitions,
                         active_loans=active_loans,
                         pending_notifications=pending_notifications,
                         recent_items=recent_items,
                         recent_exhibitions=recent_exhibitions)


@app.route('/admin/items')
@admin_required
def admin_items():
    """List all items for admin"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category_id = request.args.get('category', type=int)
    region_id = request.args.get('region', type=int)
    
    query = Item.query
    
    if search:
        query = query.filter(or_(
            Item.title.ilike(f'%{search}%'),
            Item.description.ilike(f'%{search}%')
        ))
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if region_id:
        query = query.filter_by(region_id=region_id)
    
    items = query.order_by(Item.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    categories = Category.query.all()
    regions = Region.query.all()
    
    return render_template('admin/items.html',
                         items=items,
                         categories=categories,
                         regions=regions,
                         search=search,
                         category_id=category_id,
                         region_id=region_id)


@app.route('/admin/items/new', methods=['GET', 'POST'])
@admin_required
def admin_item_new():
    """Create new item"""
    if request.method == 'POST':
        try:
            item = Item(
                title=request.form.get('title', '').strip(),
                description=request.form.get('description', '').strip(),
                historical_context=request.form.get('historical_context', '').strip(),
                year_from=request.form.get('year_from', type=int) or None,
                year_to=request.form.get('year_to', type=int) or None,
                provenance=request.form.get('provenance', '').strip(),
                conservation_state=request.form.get('conservation_state', '').strip(),
                category_id=request.form.get('category_id', type=int) or None,
                region_id=request.form.get('region_id', type=int) or None,
                era_id=request.form.get('era_id', type=int) or None,
                notes=request.form.get('notes', '').strip(),
                is_visible=bool(request.form.get('is_visible')),
                acquisition_date=datetime.strptime(request.form.get('acquisition_date'), '%Y-%m-%d').date() if request.form.get('acquisition_date') else None,
                acquisition_cost=float(request.form.get('acquisition_cost', 0)) if request.form.get('acquisition_cost') else None
            )
            
            db.session.add(item)
            db.session.flush()  # Get item.id
            
            # Handle image upload
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    image_path = save_uploaded_image(file, item.id)
                    if image_path:
                        item.image_url = image_path
            
            # Handle materials
            material_ids = request.form.getlist('materials')
            if material_ids:
                materials = Material.query.filter(Material.id.in_([int(m) for m in material_ids])).all()
                item.materials = materials
            
            db.session.commit()
            flash(_('Oggetto creato con successo.'), 'success')
            return redirect(url_for('admin_item_edit', item_id=item.id))
        except Exception as e:
            db.session.rollback()
            flash(_('Errore durante la creazione: ') + str(e), 'error')
    
    categories = Category.query.all()
    regions = Region.query.all()
    eras = Era.query.all()
    materials = Material.query.all()
    
    return render_template('admin/item_form.html',
                         item=None,
                         categories=categories,
                         regions=regions,
                         eras=eras,
                         materials=materials)


@app.route('/admin/items/<int:item_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_item_edit(item_id):
    """Edit item"""
    item = Item.query.get_or_404(item_id)
    
    if request.method == 'POST':
        try:
            item.title = request.form.get('title', '').strip()
            item.description = request.form.get('description', '').strip()
            item.historical_context = request.form.get('historical_context', '').strip()
            item.year_from = request.form.get('year_from', type=int) or None
            item.year_to = request.form.get('year_to', type=int) or None
            item.provenance = request.form.get('provenance', '').strip()
            item.conservation_state = request.form.get('conservation_state', '').strip()
            item.category_id = request.form.get('category_id', type=int) or None
            item.region_id = request.form.get('region_id', type=int) or None
            item.era_id = request.form.get('era_id', type=int) or None
            item.notes = request.form.get('notes', '').strip()
            item.is_visible = bool(request.form.get('is_visible'))
            item.acquisition_date = datetime.strptime(request.form.get('acquisition_date'), '%Y-%m-%d').date() if request.form.get('acquisition_date') else None
            item.acquisition_cost = float(request.form.get('acquisition_cost', 0)) if request.form.get('acquisition_cost') else None
            item.updated_at = datetime.utcnow()
            
            # Handle image upload
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    image_path = save_uploaded_image(file, item.id)
                    if image_path:
                        item.image_url = image_path
            
            # Handle materials
            material_ids = request.form.getlist('materials')
            materials = Material.query.filter(Material.id.in_([int(m) for m in material_ids])).all() if material_ids else []
            item.materials = materials
            
            db.session.commit()
            flash(_('Oggetto aggiornato con successo.'), 'success')
            return redirect(url_for('admin_item_edit', item_id=item.id))
        except Exception as e:
            db.session.rollback()
            flash(_('Errore durante l\'aggiornamento: ') + str(e), 'error')
    
    categories = Category.query.all()
    regions = Region.query.all()
    eras = Era.query.all()
    materials = Material.query.all()
    selected_material_ids = [m.id for m in item.materials]
    
    return render_template('admin/item_form.html',
                         item=item,
                         categories=categories,
                         regions=regions,
                         eras=eras,
                         materials=materials,
                         selected_material_ids=selected_material_ids)


@app.route('/admin/items/<int:item_id>/delete', methods=['POST'])
@admin_required
def admin_item_delete(item_id):
    """Delete item"""
    item = Item.query.get_or_404(item_id)
    
    try:
        # Delete associated images
        for img in item.images:
            if os.path.exists(os.path.join('static', img.image_url)):
                os.remove(os.path.join('static', img.image_url))
        
        db.session.delete(item)
        db.session.commit()
        flash(_('Oggetto eliminato con successo.'), 'success')
    except Exception as e:
        db.session.rollback()
        flash(_('Errore durante l\'eliminazione: ') + str(e), 'error')
    
    return redirect(url_for('admin_items'))


# ===== IMAGE MANAGEMENT =====

@app.route('/admin/items/<int:item_id>/images', methods=['GET', 'POST'])
@admin_required
def admin_item_images(item_id):
    """Manage item images"""
    item = Item.query.get_or_404(item_id)
    
    if request.method == 'POST':
        if 'images' in request.files:
            files = request.files.getlist('images')
            for file in files:
                if file and file.filename:
                    image_path = save_uploaded_image(file, item.id)
                    if image_path:
                        is_primary = len(item.images) == 0
                        img = ItemImage(
                            item_id=item.id,
                            image_url=image_path,
                            caption=request.form.get('caption', '').strip(),
                            is_primary=is_primary,
                            display_order=len(item.images)
                        )
                        db.session.add(img)
            
            db.session.commit()
            flash(_('Immagini caricate con successo.'), 'success')
            return redirect(url_for('admin_item_images', item_id=item.id))
    
    return render_template('admin/item_images.html', item=item)


@app.route('/admin/items/<int:item_id>/images/<int:image_id>/delete', methods=['POST'])
@admin_required
def admin_item_image_delete(item_id, image_id):
    """Delete item image"""
    img = ItemImage.query.get_or_404(image_id)
    
    if img.item_id != item_id:
        flash(_('Immagine non trovata.'), 'error')
        return redirect(url_for('admin_item_images', item_id=item_id))
    
    try:
        if os.path.exists(os.path.join('static', img.image_url)):
            os.remove(os.path.join('static', img.image_url))
        db.session.delete(img)
        db.session.commit()
        flash(_('Immagine eliminata con successo.'), 'success')
    except Exception as e:
        db.session.rollback()
        flash(_('Errore: ') + str(e), 'error')
    
    return redirect(url_for('admin_item_images', item_id=item_id))


@app.route('/admin/items/<int:item_id>/images/<int:image_id>/set-primary', methods=['POST'])
@admin_required
def admin_item_image_set_primary(item_id, image_id):
    """Set image as primary"""
    img = ItemImage.query.get_or_404(image_id)
    
    if img.item_id != item_id:
        flash(_('Immagine non trovata.'), 'error')
        return redirect(url_for('admin_item_images', item_id=item_id))
    
    # Unset all primary
    ItemImage.query.filter_by(item_id=item_id).update({'is_primary': False})
    img.is_primary = True
    db.session.commit()
    
    flash(_('Immagine principale impostata.'), 'success')
    return redirect(url_for('admin_item_images', item_id=item_id))


# ===== EXHIBITIONS MANAGEMENT =====

@app.route('/admin/exhibitions')
@admin_required
def admin_exhibitions():
    """List all exhibitions"""
    exhibitions = Exhibition.query.order_by(Exhibition.start_date.desc()).all()
    return render_template('admin/exhibitions.html', exhibitions=exhibitions)


@app.route('/admin/exhibitions/new', methods=['GET', 'POST'])
@admin_required
def admin_exhibition_new():
    """Create new exhibition"""
    if request.method == 'POST':
        try:
            exhibition = Exhibition(
                title=request.form.get('title', '').strip(),
                description=request.form.get('description', '').strip(),
                location=request.form.get('location', '').strip(),
                address=request.form.get('address', '').strip(),
                start_date=datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date(),
                end_date=datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date() if request.form.get('end_date') else None,
                status=request.form.get('status', 'planned'),
                notes=request.form.get('notes', '').strip()
            )
            
            db.session.add(exhibition)
            db.session.flush()
            
            # Add items
            item_ids = request.form.getlist('items')
            if item_ids:
                items = Item.query.filter(Item.id.in_([int(i) for i in item_ids])).all()
                exhibition.items = items
            
            db.session.commit()
            flash(_('Mostra creata con successo.'), 'success')
            return redirect(url_for('admin_exhibitions'))
        except Exception as e:
            db.session.rollback()
            flash(_('Errore: ') + str(e), 'error')
    
    items = Item.query.filter_by(is_visible=True).order_by(Item.title).all()
    return render_template('admin/exhibition_form.html', exhibition=None, items=items)


@app.route('/admin/exhibitions/<int:exhibition_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_exhibition_edit(exhibition_id):
    """Edit exhibition"""
    exhibition = Exhibition.query.get_or_404(exhibition_id)
    
    if request.method == 'POST':
        try:
            exhibition.title = request.form.get('title', '').strip()
            exhibition.description = request.form.get('description', '').strip()
            exhibition.location = request.form.get('location', '').strip()
            exhibition.address = request.form.get('address', '').strip()
            exhibition.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
            exhibition.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date() if request.form.get('end_date') else None
            exhibition.status = request.form.get('status', 'planned')
            exhibition.notes = request.form.get('notes', '').strip()
            exhibition.updated_at = datetime.utcnow()
            
            # Update items
            item_ids = request.form.getlist('items')
            items = Item.query.filter(Item.id.in_([int(i) for i in item_ids])).all() if item_ids else []
            exhibition.items = items
            
            db.session.commit()
            flash(_('Mostra aggiornata con successo.'), 'success')
            return redirect(url_for('admin_exhibitions'))
        except Exception as e:
            db.session.rollback()
            flash(_('Errore: ') + str(e), 'error')
    
    items = Item.query.filter_by(is_visible=True).order_by(Item.title).all()
    selected_item_ids = [i.id for i in exhibition.items]
    
    return render_template('admin/exhibition_form.html',
                         exhibition=exhibition,
                         items=items,
                         selected_item_ids=selected_item_ids)


@app.route('/admin/exhibitions/<int:exhibition_id>/delete', methods=['POST'])
@admin_required
def admin_exhibition_delete(exhibition_id):
    """Delete exhibition"""
    exhibition = Exhibition.query.get_or_404(exhibition_id)
    
    try:
        db.session.delete(exhibition)
        db.session.commit()
        flash(_('Mostra eliminata con successo.'), 'success')
    except Exception as e:
        db.session.rollback()
        flash(_('Errore: ') + str(e), 'error')
    
    return redirect(url_for('admin_exhibitions'))


# ===== VALUATIONS MANAGEMENT =====

@app.route('/admin/items/<int:item_id>/valuations', methods=['GET', 'POST'])
@admin_required
def admin_item_valuations(item_id):
    """Manage item valuations"""
    item = Item.query.get_or_404(item_id)
    
    if request.method == 'POST':
        try:
            valuation = ItemValuation(
                item_id=item.id,
                estimated_value=float(request.form.get('estimated_value', 0)) if request.form.get('estimated_value') else None,
                currency=request.form.get('currency', 'EUR'),
                valuation_date=datetime.strptime(request.form.get('valuation_date'), '%Y-%m-%d').date(),
                valuator=request.form.get('valuator', '').strip(),
                insurance_value=float(request.form.get('insurance_value', 0)) if request.form.get('insurance_value') else None,
                insurance_company=request.form.get('insurance_company', '').strip(),
                insurance_policy_number=request.form.get('insurance_policy_number', '').strip(),
                notes=request.form.get('notes', '').strip()
            )
            db.session.add(valuation)
            db.session.commit()
            flash(_('Valutazione aggiunta con successo.'), 'success')
        except Exception as e:
            db.session.rollback()
            flash(_('Errore: ') + str(e), 'error')
    
    valuations = ItemValuation.query.filter_by(item_id=item_id).order_by(ItemValuation.valuation_date.desc()).all()
    return render_template('admin/item_valuations.html', item=item, valuations=valuations)


# ===== QR CODE GENERATION =====

@app.route('/admin/items/<int:item_id>/qrcode', methods=['POST'])
@admin_required
def admin_item_qrcode(item_id):
    """Generate QR code for item"""
    item = Item.query.get_or_404(item_id)
    
    try:
        qr_path = generate_qr_code(item.id)
        
        # Save or update QR code record
        qrcode_record = ItemQRCode.query.filter_by(item_id=item.id).first()
        if qrcode_record:
            qrcode_record.qr_code_url = qr_path
        else:
            qrcode_record = ItemQRCode(item_id=item.id, qr_code_url=qr_path)
            db.session.add(qrcode_record)
        
        db.session.commit()
        flash(_('QR code generato con successo.'), 'success')
    except Exception as e:
        db.session.rollback()
        flash(_('Errore: ') + str(e), 'error')
    
    return redirect(url_for('admin_item_edit', item_id=item.id))


# ===== ADVANCED SEARCH =====

@app.route('/search')
def advanced_search():
    """Advanced search page"""
    query = request.args.get('q', '')
    category_id = request.args.get('category', type=int)
    region_id = request.args.get('region', type=int)
    era_id = request.args.get('era', type=int)
    material_id = request.args.get('material', type=int)
    year_from = request.args.get('year_from', type=int)
    year_to = request.args.get('year_to', type=int)
    conservation_state = request.args.get('conservation_state', '')
    
    items_query = Item.query.filter_by(is_visible=True)
    
    if query:
        items_query = items_query.filter(or_(
            Item.title.ilike(f'%{query}%'),
            Item.description.ilike(f'%{query}%'),
            Item.historical_context.ilike(f'%{query}%'),
            Item.provenance.ilike(f'%{query}%')
        ))
    
    if category_id:
        items_query = items_query.filter_by(category_id=category_id)
    
    if region_id:
        items_query = items_query.filter_by(region_id=region_id)
    
    if era_id:
        items_query = items_query.filter_by(era_id=era_id)
    
    if material_id:
        items_query = items_query.join(Item.materials).filter(Material.id == material_id)
    
    if year_from:
        items_query = items_query.filter(or_(
            Item.year_from >= year_from,
            Item.year_to >= year_from
        ))
    
    if year_to:
        items_query = items_query.filter(or_(
            Item.year_from <= year_to,
            Item.year_to <= year_to
        ))
    
    if conservation_state:
        items_query = items_query.filter_by(conservation_state=conservation_state)
    
    items = items_query.distinct().all()
    
    categories = Category.query.all()
    regions = Region.query.all()
    eras = Era.query.all()
    materials = Material.query.all()
    
    return render_template('search.html',
                         items=items,
                         query=query,
                         categories=categories,
                         regions=regions,
                         eras=eras,
                         materials=materials,
                         category_id=category_id,
                         region_id=region_id,
                         era_id=era_id,
                         material_id=material_id,
                         year_from=year_from,
                         year_to=year_to,
                         conservation_state=conservation_state)


# ===== STATISTICS =====

@app.route('/admin/statistics')
@admin_required
def admin_statistics():
    """Advanced statistics dashboard"""
    # Collection statistics
    total_items = Item.query.count()
    visible_items = Item.query.filter_by(is_visible=True).count()
    total_value = db.session.query(func.sum(ItemValuation.estimated_value)).scalar() or 0
    
    # By category
    category_stats = db.session.query(
        Category.name,
        func.count(Item.id).label('count')
    ).join(Item).group_by(Category.name).all()
    
    # By region
    region_stats = db.session.query(
        Region.name,
        func.count(Item.id).label('count')
    ).join(Item).group_by(Region.name).all()
    
    # By era
    era_stats = db.session.query(
        Era.name,
        func.count(Item.id).label('count')
    ).join(Item).group_by(Era.name).all()
    
    # Acquisition timeline
    acquisitions = db.session.query(
        func.extract('year', Item.acquisition_date).label('year'),
        func.count(Item.id).label('count')
    ).filter(Item.acquisition_date.isnot(None)).group_by('year').order_by('year').all()
    
    # Most viewed items
    most_viewed = Item.query.filter_by(is_visible=True).order_by(desc(Item.view_count)).limit(10).all()
    
    # Active exhibitions
    active_exhibitions = Exhibition.query.filter_by(status='active').all()
    
    return render_template('admin/statistics.html',
                         total_items=total_items,
                         visible_items=visible_items,
                         total_value=total_value,
                         category_stats=category_stats,
                         region_stats=region_stats,
                         era_stats=era_stats,
                         acquisitions=acquisitions,
                         most_viewed=most_viewed,
                         active_exhibitions=active_exhibitions)


# ===== NOTIFICATIONS =====

@app.route('/area-privata/notifications')
@login_required
def notifications_list():
    """List user notifications"""
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', notifications=notifications)


@app.route('/area-privata/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def notification_read(notification_id):
    """Mark notification as read"""
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.user_id != current_user.id:
        flash(_('Non autorizzato.'), 'error')
        return redirect(url_for('notifications_list'))
    
    notification.is_read = True
    db.session.commit()
    
    return redirect(url_for('notifications_list'))


def check_loan_due_dates():
    """Check for loans due soon and create notifications"""
    today = date.today()
    due_soon = today + timedelta(days=7)
    
    loans_due = Loan.query.filter(
        Loan.status == 'active',
        Loan.expected_return_date <= due_soon,
        Loan.expected_return_date >= today
    ).all()
    
    for loan in loans_due:
        # Check if notification already exists
        existing = Notification.query.filter_by(
            user_id=loan.user_id,
            type='loan_due',
            related_loan_id=loan.id,
            is_read=False
        ).first()
        
        if not existing:
            notification = Notification(
                user_id=loan.user_id,
                type='loan_due',
                title=f'Prestito in scadenza: {loan.item.title}',
                message=f'Il prestito scade il {loan.expected_return_date.strftime("%d/%m/%Y")}',
                related_loan_id=loan.id
            )
            db.session.add(notification)
    
    db.session.commit()


# ===== PDF EXPORT =====

@app.route('/admin/export/pdf')
@admin_required
def export_pdf():
    """Export catalog to PDF"""
    category_id = request.args.get('category', type=int)
    region_id = request.args.get('region', type=int)
    era_id = request.args.get('era', type=int)
    
    query = Item.query.filter_by(is_visible=True)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    if region_id:
        query = query.filter_by(region_id=region_id)
    if era_id:
        query = query.filter_by(era_id=era_id)
    
    items = query.order_by(Item.title).all()
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#D4AF37'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Title
    story.append(Paragraph('Catalogo Collezione', title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Items
    for item in items:
        story.append(Paragraph(item.title, styles['Heading2']))
        
        if item.description:
            story.append(Paragraph(item.description, styles['Normal']))
        
        if item.category:
            story.append(Paragraph(f'<b>Categoria:</b> {item.category.name}', styles['Normal']))
        if item.region:
            story.append(Paragraph(f'<b>Regione:</b> {item.region.name}', styles['Normal']))
        if item.era:
            story.append(Paragraph(f'<b>Epoca:</b> {item.era.name}', styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
        story.append(PageBreak())
    
    doc.build(story)
    buffer.seek(0)
    
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name='catalogo.pdf')


# ===== BACKUP & RESTORE =====

@app.route('/admin/backup')
@admin_required
def admin_backup():
    """Backup database"""
    try:
        backup_dir = app.config['BASE_DIR'] / 'backups'
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = backup_dir / f'museo_backup_{timestamp}.db'
        
        # Copy database file
        import shutil
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
            if not os.path.isabs(db_path):
                db_path = os.path.join(app.config['BASE_DIR'], db_path)
            shutil.copy2(db_path, backup_file)
        else:
            flash(_('Backup disponibile solo per SQLite.'), 'error')
            return redirect(url_for('admin_dashboard'))
        
        flash(_('Backup creato con successo.'), 'success')
        return send_file(str(backup_file), as_attachment=True, download_name=f'museo_backup_{timestamp}.db')
    except Exception as e:
        flash(_('Errore durante il backup: ') + str(e), 'error')
        return redirect(url_for('admin_dashboard'))


@app.route('/admin/export/json')
@admin_required
def export_json():
    """Export all data to JSON"""
    data = {
        'items': [item.to_dict() for item in Item.query.all()],
        'categories': [{'id': c.id, 'name': c.name, 'description': c.description} for c in Category.query.all()],
        'regions': [{'id': r.id, 'name': r.name, 'description': r.description} for r in Region.query.all()],
        'eras': [{'id': e.id, 'name': e.name, 'description': e.description} for e in Era.query.all()],
        'materials': [{'id': m.id, 'name': m.name, 'description': m.description} for m in Material.query.all()],
        'exhibitions': [{'id': e.id, 'title': e.title, 'location': e.location, 'start_date': str(e.start_date)} for e in Exhibition.query.all()]
    }
    
    return jsonify(data)


# ===== DATABASE INITIALIZATION =====

def init_db():
    """Initialize database and create tables"""
    with app.app_context():
        db.create_all()
        print("✓ Database tables created successfully")


# ===== APPLICATION ENTRY POINT =====

if __name__ == '__main__':
    # Create database if it doesn't exist
    if not os.path.exists('museo.db'):
        print("Initializing database...")
        init_db()
        print("Database ready. Run 'python seed_data.py' to add sample data.")
    
    # Run development server
    print("\n=== Da ogni capo del mondo - Digital Museum ===")
    print("Server running at: http://localhost:5001")
    print("Press CTRL+C to stop\n")
    
    app.run(debug=True, host='127.0.0.1', port=5001)
