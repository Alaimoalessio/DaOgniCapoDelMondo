"""
Initialize translations for Flask-Babel
Run this script to extract translatable strings and create translation files
"""
import os
from flask import Flask
from flask_babel import Babel

# Create a minimal Flask app for Babel
app = Flask(__name__)
app.config['LANGUAGES'] = {
    'it': 'Italiano',
    'en': 'English',
    'es': 'Español',
    'fr': 'Français',
    'de': 'Deutsch'
}

babel = Babel(app)

if __name__ == '__main__':
    print("Initializing translations...")
    print("\nTo extract translatable strings, run:")
    print("  pybabel extract -F babel.cfg -k _l -o messages.pot .")
    print("\nTo create translation files, run:")
    print("  pybabel init -i messages.pot -d translations -l en")
    print("  pybabel init -i messages.pot -d translations -l es")
    print("  pybabel init -i messages.pot -d translations -l fr")
    print("  pybabel init -i messages.pot -d translations -l de")
    print("\nTo update translations after changes:")
    print("  pybabel update -i messages.pot -d translations")
    print("\nTo compile translations:")
    print("  pybabel compile -d translations")

