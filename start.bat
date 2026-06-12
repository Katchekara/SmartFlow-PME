@echo off
title SmartFlow PME - Lancement automatique
color 0A
cd /d "%~dp0"

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║       SmartFlow PME - Démarrage          ║
echo  ║       STIC'26 - Burkina Faso             ║
echo  ╚══════════════════════════════════════════╝
echo.

echo [1/3] Entraînement des modèles IA...
python ai_models/train_credit.py > nul 2>&1
python ai_models/train_fraud.py > nul 2>&1
echo      OK - Modèles IA prets !

echo.
echo [2/3] Lancement de l'API...
start "SmartFlow-API" python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
echo      Attente demarrage API...
timeout /t 5 /nobreak > nul

echo.
echo [3/3] Lancement du site web...
start "SmartFlow-Site" python -m http.server 5500 --directory frontend
timeout /t 3 /nobreak > nul

echo.
echo  SmartFlow PME est operationnel !
echo.
echo  Site web : http://127.0.0.1:5500
echo  API docs : http://127.0.0.1:8000/docs
echo.

start http://127.0.0.1:5500

echo  Appuyez sur une touche pour arreter...
pause > nul

echo Arret des serveurs...
taskkill /f /fi "WINDOWTITLE eq SmartFlow-API" > nul 2>&1
taskkill /f /fi "WINDOWTITLE eq SmartFlow-Site" > nul 2>&1
echo Termine !
timeout /t 2 /nobreak > nul