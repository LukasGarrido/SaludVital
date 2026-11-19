"""
Entrypoint principal para Streamlit (redirige a app/app.py).
"""
from __future__ import annotations
import sys
from pathlib import Path

# Asegurar que el directorio actual esté en sys.path para importaciones de paquetes
sys.path.insert(0, str(Path(__file__).parent))

from app.app import main

if __name__ == "__main__":
    main()
