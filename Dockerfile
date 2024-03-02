FROM python:3.11

WORKDIR /app

ADD ./ /app

RUN apt-get update && apt-get install -y ffmpeg

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app","--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]