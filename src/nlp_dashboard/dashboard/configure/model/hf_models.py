MODEL_LANGUAGE = {
    "Multi-language": "xx",
    # "Catalan": "ca",
    # "Chinese": "zh",
    # "Croatian": "hr",
    # "Danish": "da",
    # "Dutch": "nl",
    "English": "en",
    # "Finnish": "fi",
    # "French": "fr",
    # "German": "de",
    # "Greek": "el",
    # "Italian": "it",
    # "Japanese": "ja",
    # "Korean": "ko",
    # "Lithuanian": "lt",
    # "Macedonian": "mk",
    # "Norwegian Bokmål": "nb",
    # "Polish": "pl",
    # "Portuguese": "pt",
    # "Romanian": "ro",
    # "Russian": "ru",
    # "Spanish": "es",
    # "Swedish": "sv",
    # "Ukrainian": "uk",
    "Custom model": "zz",
}

MODELS_AVAILABLE = {
    "en": [
        "annakotarba/sentence-similarity",
        "distilbert/distilbert-base-cased",
        "distilbert/distilbert-base-uncased",
        "google-bert/bert-base-cased",
        "google-bert/bert-base-uncased",
    ],
    "xx": [
        "bert-base-multilingual-cased",
        "bert-base-multilingual-uncased",
    ],
}

MODEL_DESCRIPTION = {
    "annakotarba/sentence-similarity":
        "Pretrained transformer model with 384 dimensions mainly used for clustering and semantic search.",
    "distilbert/distilbert-base-cased":
        "Pretrained transformer model with 768 dimensions based on BERT with case accents.",
    "distilbert/distilbert-base-uncased":
        "Pretrained transformer model with 768 dimensions based on BERT without case accents.",
    "google-bert/bert-base-multilingual-cased":
        "Pretrained transformer model with 768 dimensions using a masked language modeling objective and with case accents.",
    "google-bert/bert-base-multilingual-uncased":
        "Pretrained transformer model with 768 dimensions using a masked language modeling objective and without case accents.",
    "google-bert/bert-base-cased":
        "Pretrained transformer model with 768 dimensions using a masked language modeling objective and with case accents.",
    "google-bert/bert-base-uncased":
        "Pretrained transformer model with 768 dimensions using a masked language modeling objective and without case accents.",
}
