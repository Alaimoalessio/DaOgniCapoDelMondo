# Da ogni capo del mondo - Museo Digitale

🏛️ **Un museo digitale per catalogare e esporre oltre 700 copricapi, abiti e oggetti storici provenienti da tutto il mondo.**

## 📋 Panoramica

Questa applicazione web trasforma una collezione fisica di oggetti storici in un museo digitale accessibile, funzionando sia come archivio gestionale che come vetrina espositiva per il pubblico.

### Tech Stack

- **Backend**: Python 3.x + Flask
- **Database**: SQLite (scalabile a PostgreSQL)
- **ORM**: SQLAlchemy
- **Frontend**: HTML5 Semantico + CSS3 Custom + JavaScript Vanilla
- **Design**: Dark Museum Theme con Masonry Grid

---

## 🚀 Installazione Rapida

### 1. Prerequisiti

- Python 3.8 o superiore
- pip (gestore pacchetti Python)

### 2. Clonare/Navigare nella directory

```bash
cd museo-digitale
```

### 3. Creare ambiente virtuale (consigliato)

```bash
# Creare virtual environment
python3 -m venv venv

# Attivare virtual environment
# Su Linux/Mac:
source venv/bin/activate

# Su Windows:
# venv\Scripts\activate
```

### 4. Installare dipendenze

```bash
pip install -r requirements.txt
```

### 5. Popolare il database con dati di esempio

```bash
python seed_data.py
```

Questo comando:
- Crea il database SQLite (`museo.db`)
- Genera le tabelle (Items, Categories, Regions, Materials, Eras)
- Inserisce 6 oggetti di esempio (Armatura Samurai, Feluca Napoleonica, Perak Tibetano, etc.)

### 6. Avviare il server

```bash
python app.py
```

Il server sarà disponibile su: **http://localhost:5000**

---

## 📂 Struttura del Progetto

```
museo-digitale/
├── app.py                      # Applicazione Flask principale
├── models.py                   # Modelli database SQLAlchemy
├── config.py                   # Configurazioni
├── seed_data.py               # Script per dati di esempio
├── requirements.txt           # Dipendenze Python
├── museo.db                   # Database SQLite (auto-generato)
│
├── static/
│   ├── css/
│   │   └── style.css         # Dark Museum Theme
│   ├── js/
│   │   └── main.js           # JavaScript interattivo
│   └── images/               # Immagini locali (opzionale)
│
└── templates/
    ├── base.html             # Template base
    ├── index.html            # Homepage con gallery
    └── detail.html           # Pagina dettaglio oggetto
```

---

## 🎨 Design System - "Dark Museum"

### Palette Colori

- **Background**: `#121212` (nero profondo)
- **Cards**: `#1e1e1e` (grigio scuro)
- **Accent Gold**: `#D4AF37` (oro museo)
- **Accent Turquoise**: `#40E0D0` (turchese)
- **Testo**: `#E8E8E8` (bianco sporco)

### Tipografia

- **Titoli**: Playfair Display (serif elegante)
- **Testo**: Inter (sans-serif moderno)

### Layout

- **Masonry Grid**: Griglia responsive a colonne variabili
- **Responsive**: 1 colonna (mobile), 2 colonne (tablet), 3+ colonne (desktop)

---

## 💾 Schema Database

### Tabelle Principali

**Items** (Oggetti del museo)
- `id`, `title`, `description`, `historical_context`
- `year_from`, `year_to`, `provenance`
- `image_url`, `conservation_state`
- Relazioni: Category, Region, Era, Materials (many-to-many)

**Categories** (Militaria, Cerimoniale, Abbigliamento, Arte Sacra)

**Regions** (Asia Orientale, Himalaya, Africa, Europa)

**Materials** (Ferro, Oro, Seta, Legno, Turchese, etc.)

**Eras** (Medievale, Rinascimento, Edo, Napoleonico, Moderno)

---

## 🔧 Utilizzo

### Visualizzare la Collezione

1. Apri browser: `http://localhost:5000`
2. Naviga la gallery con Masonry Grid
3. Usa i filtri laterali (Categoria, Regione, Epoca)

### Visualizzare Dettaglio Oggetto

- Clicca su qualsiasi card nella gallery
- Visualizza immagine grande, metadata completi, contesto storico
- Vedi oggetti correlati in fondo alla pagina

### Filtrare Oggetti

- **Server-side**: Usa i radio button nella sidebar e clicca "Applica Filtri"
- **API JSON**: Endpoint disponibile su `/api/filter?category=1&region=2`

---

## 🌐 Deployment Produzione

### PostgreSQL (Raccomandato)

1. Installare PostgreSQL
2. Creare database:
   ```bash
   createdb museo_db
   ```

3. Modificare `config.py`:
   ```python
   SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/museo_db'
   ```

4. Installare driver:
   ```bash
   pip install psycopg2-binary
   ```

### Server Produzione (Gunicorn)

```bash
# Installare Gunicorn
pip install gunicorn

# Avviare con 4 worker
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Docker (Opzionale)

Creare `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

---

## 📝 Aggiungere Nuovi Oggetti

### Metodo 1: Manualmente via Python

```python
from app import app, db
from models import Item, Category, Region, Material, Era

with app.app_context():
    # Creare nuovo oggetto
    item = Item(
        title="Nuovo Oggetto",
        description="Descrizione...",
        historical_context="Contesto storico...",
        year_from=1800,
        provenance="Luogo di origine",
        image_url="https://...",
        conservation_state="Ottimo",
        category_id=1,
        region_id=2,
        era_id=3
    )
    
    db.session.add(item)
    db.session.commit()
```

### Metodo 2: Creare Form Admin (Enhancement Futuro)

Implementare route `/admin/add` con form HTML per inserimento dati.

---

## 🎯 API Endpoints

### GET `/`
Homepage con gallery completa

### GET `/item/<id>`
Dettaglio singolo oggetto

### GET `/filter`
Risultati filtrati (HTML)
- Parametri: `category`, `region`, `era`, `material`

### GET `/api/filter`
Risultati filtrati (JSON)
- Parametri: `category`, `region`, `era`, `material`
- Risposta:
  ```json
  {
    "count": 5,
    "items": [
      {
        "id": 1,
        "title": "...",
        "description": "...",
        "region": "Asia",
        ...
      }
    ]
  }
  ```

---

## 🐛 Troubleshooting

### Database non si crea

```bash
# Forzare ricreazione
rm museo.db
python seed_data.py
```

### Dipendenze mancanti

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Porta 5000 già in uso

Modificare in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)
```

---

## 📚 Prossimi Sviluppi

- [ ] Form di inserimento oggetti tramite web
- [ ] Upload immagini locale
- [ ] Ricerca full-text
- [ ] Esportazione catalogo PDF
- [ ] Sistema autenticazione admin
- [ ] Gallery lightbox per immagini

---

## 📄 Licenza

© 2024 Da ogni capo del mondo - Museo Digitale. Tutti i diritti riservati.

---

## 👨‍💻 Supporto

Per domande o problemi tecnici, consultare la documentazione o aprire una issue.

**Versione**: 1.0.0  
**Data**: Dicembre 2024
