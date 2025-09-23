```sh
cd backend
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
python -m scripts.ingest_docs
uvicorn app.main:app --reload --port 8000
```