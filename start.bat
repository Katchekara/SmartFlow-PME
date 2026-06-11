@echo off
title SmartFlow PME - Lancement automatique
color 0A

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║       SmartFlow PME - Démarrage          ║
echo  ║       STIC'26 - Burkina Faso             ║
echo  ╚══════════════════════════════════════════╝
echo.

echo [1/3] Entraînement des modèles IA...
python ai_models/train_credit.py > nul 2>&1
python ai_models/train_fraud.py > nul 2>&1
echo      OK - Modèles IA prêts !

echo.
echo [2/3] Lancement de l'API...
start /B python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 > nul 2>&1
timeout /t 3 /nobreak > nul
echo      OK - API lancée sur http://127.0.0.1:8000

echo.
echo [3/3] Lancement du site web...
start /B python -m http.server 5500 --directory frontend > nul 2>&1
timeout /t 2 /nobreak > nul
echo      OK - Site lancé sur http://127.0.0.1:5500

echo.
echo  ✅ SmartFlow PME est opérationnel !
echo.
echo  Site web : http://127.0.0.1:5500
echo  API docs : http://127.0.0.1:8000/docs
echo.

start http://127.0.0.1:5500
echo  Appuyez sur une touche pour arrêter tous les serveurs...
pause > nul

echo.
echo Arrêt des serveurs...
taskkill /f /im python.exe > nul 2>&1
echo Serveurs arrêtés. Au revoir !
timeout /t 2 /nobreak > nul