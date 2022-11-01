# ✨ The Culture Hack Labs NLP Dashboard App ✨

Streamlit dashboard for natural language processing.

## Usage

A [Jupyter notebook](notebook.ipynb) is included with usage guidelines for standalone NLP usage.

___

### Containerized application

Build and run the application in a container while exposing the required port with:

```
docker build -t nlp-dashboard . &&
docker run -dp 8501:8501 nlp-dashboard
```

With the application running, open [localhost:8501](localhost:8501) on your browser of choice.

> Also tested and working with rootless [podman](https://github.com/containers/podman).

___

### Without containerization

To start the application without any virtualization, simply run:

```
streamlit run run.py
```

#### Requirements

Tested with Python versions `3.10` and `3.11` running on Linux. To install the required libraries, run:

```
pip install -r requirements.txt
```

#### Additional requirements

For optical character recognition (OCR), [Tesseract](https://github.com/tesseract-ocr/tesseract) is required:

```
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-eng # tesseract-ocr-all

# Fedora
sudo dnf install tesseract tesseract-langpack-eng

# Arch
sudo pacman -S tesseract tesseract-data-eng

# OpenSUSE
sudo zypper in tesseract-ocr tesseract-ocr-traineddata-english
```

Additional packages for other languages besides English are also available in the repositories.
