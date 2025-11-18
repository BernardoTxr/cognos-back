run local:
pip install uvicorn[standard]
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

run com docker só para build:
docker build -t back .
docker run -p 8000:8000 back