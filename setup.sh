#!/bin/bash

# Script de configuration du Téléchargeur de postulats du Conseil d'État VD
# Ce script aide à configurer le projet avec uv

set -e

echo "Téléchargeur de postulats du Conseil d'État VD - Script de configuration"
echo "======================================================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé. Veuillez installer Python 3.8+ d'abord."
    exit 1
fi

echo "✅ Python 3 trouvé : $(python3 --version)"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installation de uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✅ uv installé avec succès"
    
    # Add uv to PATH for current session
    export PATH="$HOME/.cargo/bin:$PATH"
else
    echo "✅ uv trouvé : $(uv --version)"
fi

# Install dependencies
echo "📦 Installation des dépendances du projet..."
uv sync

# Setup pre-commit hooks
echo "🔧 Configuration des hooks pre-commit..."
uv run pre-commit install

echo "✅ Hooks pre-commit installés avec succès !"

echo ""
echo "🎉 Configuration terminée avec succès !"
echo ""
echo "Pour lancer l'application :"
echo "   python run.py"
echo ""
echo "Pour plus d'informations, consultez README.md" 