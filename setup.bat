@echo off
REM Script de configuration du Téléchargeur de postulats du Conseil d'État VD pour Windows
REM Ce script aide à configurer le projet avec uv

echo Téléchargeur de postulats du Conseil d'État VD - Script de configuration
echo ========================================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou pas dans le PATH. Veuillez installer Python 3.8+ d'abord.
    pause
    exit /b 1
)

echo ✅ Python trouvé :
python --version

REM Check if uv is installed
uv --version >nul 2>&1
if errorlevel 1 (
    echo 📦 Installation de uv...
    echo Veuillez installer uv manuellement en visitant :
    echo https://docs.astral.sh/uv/getting-started/installation/
    echo.
    echo Ou utilisez pip comme fallback :
    echo pip install uv
    pause
    exit /b 1
) else (
    echo ✅ uv trouvé :
    uv --version
)

REM Install dependencies
echo 📦 Installation des dépendances du projet...
uv sync
if errorlevel 1 (
    echo ❌ Échec de l'installation des dépendances.
    pause
    exit /b 1
)

REM Setup pre-commit hooks
echo 🔧 Configuration des hooks pre-commit...
uv run pre-commit install
if errorlevel 1 (
    echo ❌ Échec de la configuration des hooks pre-commit.
    pause
    exit /b 1
)

echo.
echo 🎉 Configuration terminée avec succès !
echo.
echo Pour lancer l'application :
echo    python run.py
echo.
echo Pour plus d'informations, consultez README.md
pause 