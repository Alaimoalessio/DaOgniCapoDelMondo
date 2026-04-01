"""
Script per aggiornare automaticamente le immagini degli oggetti
basandosi sul matching tra titolo dell'oggetto e nome del file immagine
"""
import os
import re
from pathlib import Path
from app import app
from models import db, Item

def normalize_filename(text):
    """
    Converte un titolo in un nome file normalizzato
    Es: "Armatura Samurai Completa" -> "armatura-samurai-completa"
    """
    # Converti in minuscolo
    text = text.lower()
    
    # Rimuovi caratteri speciali e accenti comuni
    text = text.replace('à', 'a').replace('è', 'e').replace('é', 'e')
    text = text.replace('ì', 'i').replace('ò', 'o').replace('ù', 'u')
    
    # Sostituisci spazi, trattini multipli, underscore con un singolo trattino
    text = re.sub(r'[\s_\-]+', '-', text)
    
    # Rimuovi caratteri non alfanumerici e trattini
    text = re.sub(r'[^a-z0-9\-]', '', text)
    
    # Rimuovi trattini multipli
    text = re.sub(r'-+', '-', text)
    
    # Rimuovi trattini all'inizio e alla fine
    text = text.strip('-')
    
    return text

def find_matching_image(item_title, images_dir):
    """
    Cerca un'immagine corrispondente al titolo dell'oggetto
    """
    base_name = normalize_filename(item_title)
    
    # Estensioni supportate
    extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
    
    # Cerca corrispondenze esatte o parziali
    for ext in extensions:
        # Prova nome esatto
        exact_match = images_dir / f"{base_name}.{ext}"
        if exact_match.exists():
            return exact_match.name
        
        # Prova varianti comuni
        variants = [
            base_name.replace('-', '_'),  # Trattini -> underscore
            base_name.replace('-', ''),   # Senza trattini
            base_name.split('-')[0],      # Solo prima parola
        ]
        
        for variant in variants:
            if variant:  # Evita stringhe vuote
                variant_match = images_dir / f"{variant}.{ext}"
                if variant_match.exists():
                    return variant_match.name
    
    # Cerca corrispondenze parziali (il titolo contiene parte del nome file o viceversa)
    for image_file in images_dir.iterdir():
        if image_file.is_file() and image_file.suffix.lower() in [f'.{ext}' for ext in extensions]:
            image_name = normalize_filename(image_file.stem)
            
            # Controlla se il nome dell'immagine è contenuto nel titolo o viceversa
            if base_name in image_name or image_name in base_name:
                # Preferisci corrispondenze più lunghe
                return image_file.name
    
    return None

def update_item_images(images_folder='items', base_path=None):
    """
    Aggiorna le immagini di tutti gli oggetti nel database
    
    Args:
        images_folder: Nome della cartella contenente le immagini (default: 'items')
        base_path: Percorso base (default: static/images/)
    """
    with app.app_context():
        # Determina il percorso delle immagini
        if base_path is None:
            base_path = Path(__file__).parent / 'static' / 'images'
        else:
            base_path = Path(base_path)
        
        images_dir = base_path / images_folder
        
        if not images_dir.exists():
            print(f"❌ Errore: La cartella {images_dir} non esiste!")
            print(f"   Crea la cartella e metti le tue immagini lì dentro.")
            return
        
        # Ottieni tutti gli oggetti
        items = Item.query.all()
        print(f"\n📦 Trovati {len(items)} oggetti nel database")
        print(f"📁 Cercando immagini in: {images_dir}\n")
        
        # Lista immagini disponibili
        available_images = [f.name for f in images_dir.iterdir() if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']]
        print(f"🖼️  Trovate {len(available_images)} immagini disponibili\n")
        
        updated = 0
        not_found = []
        
        for item in items:
            # Cerca immagine corrispondente
            image_filename = find_matching_image(item.title, images_dir)
            
            if image_filename:
                # Costruisci il percorso relativo per Flask
                relative_path = f"images/{images_folder}/{image_filename}"
                
                # Aggiorna solo se diverso
                if item.image_url != relative_path:
                    old_url = item.image_url or "(nessuna)"
                    item.image_url = relative_path
                    print(f"✅ {item.title}")
                    print(f"   {old_url} → {relative_path}")
                    updated += 1
                else:
                    print(f"ℹ️  {item.title} (già aggiornato)")
            else:
                not_found.append(item.title)
                print(f"⚠️  {item.title} - Nessuna immagine trovata")
        
        # Salva le modifiche
        if updated > 0:
            db.session.commit()
            print(f"\n✅ Aggiornati {updated} oggetti nel database!")
        else:
            print("\nℹ️  Nessun aggiornamento necessario.")
        
        # Mostra oggetti senza immagine
        if not_found:
            print(f"\n⚠️  {len(not_found)} oggetti senza immagine corrispondente:")
            for title in not_found:
                print(f"   - {title}")
            print(f"\n💡 Suggerimento: Rinomina le immagini seguendo questa convenzione:")
            if not_found:
                print(f"   Esempio: '{not_found[0]}' → '{normalize_filename(not_found[0])}.jpg'")

if __name__ == '__main__':
    print("=" * 60)
    print("🖼️  AGGIORNAMENTO IMMAGINI OGGETTI")
    print("=" * 60)
    
    # Puoi cambiare 'items' con il nome della tua cartella
    # Es: 'items', 'oggetti', 'collezione', etc.
    update_item_images(images_folder='items')
    
    print("\n" + "=" * 60)
    print("✅ Completato!")
    print("=" * 60)

