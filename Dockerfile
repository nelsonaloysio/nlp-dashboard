ARG LTS=24.04

FROM ubuntu:${LTS}

USER root

FROM python:3.11

COPY . /tmp/app

WORKDIR /tmp/app

RUN apt-get update

RUN apt-get install -y libgl1-mesa-glx tesseract-ocr tesseract-ocr-eng

# RUN apt-get install -y tesseract-ocr-all

RUN pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "src/dashboard/run.py"]
