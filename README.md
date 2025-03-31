python3 app.py

gunicorn -w 2 -b 0.0.0.0:8090 app:app

curl --silent http://0.0.0.0:8090/health