FROM python:3.9-slim

WORKDIR /app

COPY plot.py requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "plot.py"]
