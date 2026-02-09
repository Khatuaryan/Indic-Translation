import os
import re

from indicnlp.tokenize import sentence_tokenize


def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def save_file(filepath, text):
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)


def normalize_text(text):
    """
    Minimal but essential normalization for Indic MT evaluation.
    """
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    return text


def split_sentences(text, lang='kn'):
    """
    Sentence segmentation using Indic NLP Library.
    """
    sentences = sentence_tokenize.sentence_split(text, lang=lang)
    return [s.strip() for s in sentences if s.strip()]