ARG LTS=24.04

FROM ubuntu:${LTS}

USER root

FROM python:3.10

COPY . /tmp/app

WORKDIR /tmp/app

RUN apt-get update

RUN apt-get install -y libgl1-mesa-glx tesseract-ocr tesseract-ocr-eng # tesseract-ocr-all

# RUN apt-get install -y tesseract-ocr-all

RUN pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "run.py"]
