@echo off
echo Instalando dependencias...
pip install -r requirements.txt

echo.
echo Ejecutando aplicacion Streamlit...
streamlit run app.py

pause