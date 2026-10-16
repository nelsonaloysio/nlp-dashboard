# Natural Language Processing Dashboard App

Data processing pipeline, command line interface, notebook, and Streamlit dashboard.

> Proof of concept deployed as a [Streamlit community app](https://nlp-dashboard-app.streamlit.app/) for demonstration purposes.

## About

The pipeline (constructed with `sklearn`) is composed of nine steps executed sequentially:

| # | Step | Description |
| --- | --- | --- |
| 1 | Reader | Loads data into memory |
| 2 | Pandas | Builds Pandas series with text |
| 3 | Tokenizer | Preprocesses text |
| 4 | NLTK | Generates n-grams from text |
| 5 | Spacy | Natural language processor |
| 6 | HF | Generates embeddings from text |
| 7 | KMeans | Clusterize embeddings |
| 8 | UMAP or TSNE | Dimensionality reduction |
| 9 | Processor | Artifacts from results |

## Standalone usage

### Jupyter notebook

A **[Jupyter notebook](notebook/notebook.ipynb)** is included in the repository with guidelines for standalone usage of the pipeline.

### Command line interface

> The application may be installed as a Python module with `python install -e .`

A command line interface is available and accepts the following arguments:

```bash
usage: nlp-pipeline [-h] [--output FOLDER] [--seed SEED]
                    [--no-hf] [--no-kmeans]
                    [--no-nltk] [--no-pandas]
                    [--no-processor] [--no-reader]
                    [--no-spacy] [--no-tokenizer]
                    [--no-tsne] [--no-umap] [--use-tsne]
                    [--steps STEPS] INPUT [INPUT ...]

positional arguments:
  INPUT                 Input file(s) or folder(s).

options:
  -h, --help            show this help message and exit
  --output FOLDER       Path of folder to save files.
  --seed SEED           Random seed number.
  --no-hf               Disable HuggingFace pipeline step.
  --no-kmeans           Disable K-Means pipeline step.
  --no-nltk             Disable NLTK pipeline step.
  --no-pandas           Disable Pandas pipeline step.
  --no-processor        Disable processor pipeline step.
  --no-reader           Disable reader pipeline step.
  --no-spacy            Disable spaCy pipeline step.
  --no-tokenizer        Disable tokenizer pipeline step.
  --no-tsne             Disable TSNE pipeline step.
  --use-tsne            Enable TSNE pipeline step.
  --steps STEPS         Order of steps in pipeline (comma-separated).
```

Example to process data from two files with English-based pretrained models:

```bash
nlp-pipeline file1.ext file2.ext \
             --hf-model annakotarba/sentence-similarity \
             --spacy-model english_web_sm
```

For details, please see the [list of hyperpameters](#list-of-hyperparameters) section.

___

## Dashboard prototype

### Containerized application

Build and run the application in a container while exposing the required port with:

```bash
docker build -t nlp-dashboard . &&
docker run -dp 8501:8501 nlp-dashboard
```

> Also tested and working with rootless [podman](https://github.com/containers/podman).

With the application running, open [localhost:8501](https://localhost:8501) on your browser of choice.

### Without containerization

To start the application without any virtualization, simply run:

```bash
nlp-dashboard
```

If the library is not installed locally, execute instead:

```bash
streamlit run src/nlp_dashboard/dashboard/run.py
```

#### Requirements

Tested with Python versions `3.10` and `3.11` running on Linux. To install the required libraries, run:

```bash
pip install -r requirements.txt
```

___

### Additional requirements

#### GPU/CUDA support

Support for GPUs is implemented for NVidia devices with CUDA:

- Natural language processing (with spaCy): requires [CuPy](https://spacy.io/usage#gpu);

- Embeddings from text (with HuggingFace): requires matching CUDA drivers only;

- K-Means clustering (with PyTorch): requires matching CUDA drivers only.

It is recommended to install the additional requirements using [conda](https://docs.anaconda.com/free/miniconda/):

```bash
conda install -c conda-forge cupy cudnn cutensor nccl cudatoolkit={VERSION}
```

**Note:** replace `{VERSION}` above with the major version obtained by `nvidia-smi | grep CUDA`.

#### Optical character recognition

Support for OCR on images requires [Tesseract](https://github.com/tesseract-ocr/tesseract):

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-eng # tesseract-ocr-all

# Fedora
sudo dnf install tesseract tesseract-langpack-eng

# Arch
sudo pacman -S tesseract tesseract-data-eng

# OpenSUSE
sudo zypper in tesseract-ocr tesseract-ocr-traineddata-english
```

**Note:** additional packages for other languages besides English are also available in the repositories.

___

## List of hyperparameters

```none
reader
  - Accepts no hyperparameters. Supported formats: csv, docx, gzip, json, ods, odt, parquet, pdf, txt, xlsx, zip.

pandas
  - applymap: function to apply to each element of the DataFrame.
  - column: text column(s) to read.
  - compression: compression mode among the following possible values: {'infer', 'gzip', 'bz2', 'zip', 'xz', None}.
  - drop_duplicates: whether to drop duplicates.
  - dropna: whether to drop empty values.
  - engine: parser engine to use. The C engine is faster while the python engine is currently more feature-complete.
  - json_lines: whether to read json lines.
  - json_normalize: whether to normalize json.
  - low_memory: whether to process the file in chunks.
  - nrows: number of rows to read.
  - sep: delimiter to use.
  - sort: whether to sort the data.

tokenizer
  - text: whether to return original text within dictionary.
  - tokens: whether to return tokens within dictionary.
  - hashtags: whether to return hashtags within dictionary.
  - mentions: whether to return mentions within dictionary.
  - numbers: whether to return numbers within dictionary.
  - urls: whether to return URLs within dictionary.
  - clear_accents: whether to clear accents from words.
  - clear_characters: whether to clear undesired characters from text.
  - clear_emojis: whether to clear emojis from text.

nltk
  - min_gram_size: minimum size of word for n-grams.

spacy
  - batch_size: batch size for processing.
  - min_lemma_size: minimum size of word for lemmatization.
  - model: model to use.
  - n_process: number of processes to use.
  - device: 'cpu' or 'gpu' (default: auto).

hf
  - model: model from Hugging Face to use to generate embeddings.
  - max_workers: maximum number of workers to use.
  - chunksize: chunk size for processing.
  - device: 'cpu' or 'cuda' (default: auto).

kmeans
  - n_clusters: number of clusters to consider (default: between 2 and 8).
  - init: initialization of the centroids (default: 'k-means++').
  - n_init: number of times the k-means algorithm will be run with different centroid seeds (default: 20).
  - max_iter: maximum number of iterations of the k-means algorithm for a single run (default: 300).
  - elbow_tol: tolerance with regards to inertia for elbow method (default: 2e-1).
  - tol: relative tolerance with regards to inertia to declare convergence (default: 1e-4).
  - minibatch: whether to use the CPU minibatch k-means algorithm (default: False).
  - device: 'cpu' or 'cuda' (default: auto).
  - preserve_embeddings: whether to preserve the embeddings in the output.
  - seed: random seed number for predictable randomness.
  - verbose: whether to print progress.

umap
  - metric: distance metric (default: "euclidean").
  - min_dist: minimum distance among points (default: 0.1).
  - n_components: number of dimensions (default: 2).
  - n_neighbors: minimum number of neighbors (default: 15).

tsne
  - n_components: number of dimensions to reduce embeddings to.
  - perplexity: perplexity of the t-SNE algorithm (default: 60.0).

processor
  - dates: list, Pandas series or column name (CLI/Jupyter) object containing datetimes.
  - json: whether to return results in JSON format.
  - max_groups: maximum number of groups to return per artifact.
  - max_objects: maximum number of objects to return per artifact.
  - min_time_steps: minimum number of steps to consider for time interval.
  - stopwords_custom: list of additional tokens to include as stopwords.
  - stopwords_language: language to use for stopwords (default: all).
```
