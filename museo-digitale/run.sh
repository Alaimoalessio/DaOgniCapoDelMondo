#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
echo ""
echo "=== Da ogni capo del mondo - Digital Museum ==="
echo "Avvio del server backend..."
echo ""
python app.py
