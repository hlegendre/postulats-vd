#!/bin/bash

# Script de configuration du Téléchargeur de séances du Conseil d'État VD
# Ce script aide à configurer le projet avec uv

set -e

echo "Téléchargeur de séances du Conseil d'État VD - Script de configuration"
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

# Create hooks directory if it doesn't exist
mkdir -p .git/hooks

# Copy pre-commit hook if it already exists
if [ -f ".git/hooks/pre-commit" ]; then
    echo "📝 Pre-commit hook déjà existant, sauvegarde..."
    cp .git/hooks/pre-commit .git/hooks/pre-commit.backup
fi

# Create the pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash

# Pre-commit hook to run code quality checks
# This script runs before each commit

echo "🔍 Running pre-commit checks..."

# Get the list of staged Python files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')

if [ -z "$STAGED_FILES" ]; then
    echo "✅ No Python files staged for commit"
    exit 0
fi

echo "📝 Staged Python files:"
echo "$STAGED_FILES"

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed or not in PATH"
    exit 1
fi

# Run Black formatting check
echo "🎨 Checking code formatting with Black..."
uv run black --check $STAGED_FILES
if [ $? -ne 0 ]; then
    echo "❌ Code formatting check failed!"
    echo "💡 Run 'uv run black .' to fix formatting issues"
    exit 1
fi

# Run flake8 linting (if available)
if uv run which flake8 &> /dev/null; then
    echo "🔍 Running flake8 linting..."
    uv run flake8 $STAGED_FILES
    if [ $? -ne 0 ]; then
        echo "❌ Linting check failed!"
        exit 1
    fi
fi

echo "✅ All pre-commit checks passed!"
exit 0
EOF

# Make the hook executable
chmod +x .git/hooks/pre-commit

echo "✅ Hooks pre-commit installés avec succès !"

echo ""
echo "🎉 Configuration terminée avec succès !"
echo ""
echo "Prochaines étapes :"
echo "1. Activer l'environnement virtuel :"
echo "   source .venv/bin/activate"
echo ""
echo "2. Tester l'application :"
echo "   uv run pytest"
echo ""
echo "3. Lancer l'application principale :"
echo "   python run.py"
echo ""
echo "4. Formater / linter le code :"
echo "   uv run ruff check ."
echo ""
echo "📋 Les hooks pre-commit vérifient automatiquement :"
echo "   • Le formatage et le lint du code avec Ruff"
echo "   • Seulement les fichiers Python modifiés"
echo ""
echo "💡 Pour ignorer les hooks (urgence uniquement) :"
echo "   git commit --no-verify -m 'message d'urgence'"
echo ""
echo "Pour plus d'informations, consultez README.md" 