MODEL_LANGUAGE = {
    "Multi-language": "xx",
    "Catalan": "ca",
    "Chinese": "zh",
    "Croatian": "hr",
    "Danish": "da",
    "Dutch": "nl",
    "English": "en",
    "Finnish": "fi",
    "French": "fr",
    "German": "de",
    "Greek": "el",
    "Italian": "it",
    "Japanese": "ja",
    "Korean": "ko",
    "Lithuanian": "lt",
    "Macedonian": "mk",
    "Norwegian Bokmål": "nb",
    "Polish": "pl",
    "Portuguese": "pt",
    "Romanian": "ro",
    "Russian": "ru",
    "Spanish": "es",
    "Swedish": "sv",
    "Ukrainian": "uk",
    "Custom model": "zz",
}

MODEL_TYPE = {
    "core": "general-purpose model with tagging, parsing, lemmatization, and named entity recognition",
    "dep": "model with only tagging, parsing, and lemmatization",
    "ent": "model with only named entity recognition",
    "sent": "model with only sentence segmentation",
}

MODEL_GENRE = {
    "web": "web text data",
    "news": "news stories data (posts and comments)",
    "ud": "undefined data",
    "wiki": "Wikipedia data",
}

MODEL_SIZE = {
    "sm": "small size (no word vectors)",
    "md": "medium size (reduced word vector table)",
    "lg": "large size (word vector table)",
    "trf": "transformers-based (focused on accuracy over efficiency)",
}

MODELS_AVAILABLE = {
    "ca": [
        "ca_core_news_sm",
        "ca_core_news_md",
        "ca_core_news_lg",
        "ca_core_news_trf",
    ],
    "da": [
        "da_core_news_sm",
        "da_core_news_md",
        "da_core_news_lg",
        "da_core_news_trf",
    ],
    "de": [
        "de_core_news_sm",
        "de_core_news_md",
        "de_core_news_lg",
        "de_dep_news_trf",
    ],
    "el": [
        "el_core_news_sm",
        "el_core_news_md",
        "el_core_news_lg",
    ],
    "en": [
        "en_core_web_sm",
        "en_core_web_md",
        "en_core_web_lg",
        "en_core_web_trf",
    ],
    "es": [
        "es_core_news_sm",
        "es_core_news_md",
        "es_core_news_lg",
        "es_dep_news_trf",
    ],
    "fi": [
        "fi_core_news_sm",
        "fi_core_news_md",
        "fi_core_news_lg",
    ],
    "fr": [
        "fr_core_news_sm",
        "fr_core_news_md",
        "fr_core_news_lg",
        "fr_dep_news_trf",
    ],
    "hr": [
        "hr_core_news_sm",
        "hr_core_news_md",
        "hr_core_news_lg",
    ],
    "it": [
        "it_core_news_sm",
        "it_core_news_md",
        "it_core_news_lg",
    ],
    "ja": [
        "ja_core_news_sm",
        "ja_core_news_md",
        "ja_core_news_lg",
        "ja_core_news_trf",
    ],
    "ko": [
        "ko_core_news_sm",
        "ko_core_news_md",
        "ko_core_news_lg",
    ],
    "lt": [
        "lt_core_news_sm",
        "lt_core_news_md",
        "lt_core_news_lg",
    ],
    "mk": [
        "mk_core_news_sm",
        "mk_core_news_md",
        "mk_core_news_lg",
    ],
    "nb": [
        "nb_core_news_sm",
        "nb_core_news_md",
        "nb_core_news_lg",
    ],
    "nl": [
        "nl_core_news_sm",
        "nl_core_news_md",
        "nl_core_news_lg",
    ],
    "pl": [
        "pl_core_news_sm",
        "pl_core_news_md",
        "pl_core_news_lg",
    ],
    "pt": [
        "pt_core_news_sm",
        "pt_core_news_md",
        "pt_core_news_lg",
    ],
    "ro": [
        "ro_core_news_sm",
        "ro_core_news_md",
        "ro_core_news_lg",
    ],
    "ru": [
        "ru_core_news_sm",
        "ru_core_news_md",
        "ru_core_news_lg",
    ],
    "sv": [
        "sv_core_news_sm",
        "sv_core_news_md",
        "sv_core_news_lg",
    ],
    "uk": [
        "uk_core_news_sm",
        "uk_core_news_md",
        "uk_core_news_lg",
        "uk_core_news_trf",
    ],
    "xx": [
        "xx_ent_wiki_sm",
        "xx_sent_ud_sm",
    ],
    "zh": [
        "zh_core_web_sm",
        "zh_core_web_md",
        "zh_core_web_lg",
        "zh_core_web_trf",
    ],
}