FROM python:3

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN apt update && apt install -y libsm6 libxext6 ffmpeg libfontconfig1 libxrender1 libgl1-mesa-glx
    
COPY . /app

CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8080"]
