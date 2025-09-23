@echo off
echo Starting INGRES AI Chatbot Backend Server...
echo =============================================
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload