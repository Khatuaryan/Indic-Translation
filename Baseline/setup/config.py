import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TRANSLATION_DIRECTIONS = [
    {
        "name": "kn_mr",

        "src_lang": "kn",
        "tgt_lang": "mr",

        "src_dir": os.path.join(BASE_DIR, "dataset/kannada"),
        "ref_dir": os.path.join(BASE_DIR, "dataset/marathi"),

        "nllb_src": "kan_Knda",
        "nllb_tgt": "mar_Deva",

        "indic_src": "kan_Knda",
        "indic_tgt": "mar_Deva",

        "google_src": "kn",
        "google_tgt": "mr"
    },
    {
        "name": "mr_kn",

        "src_lang": "mr",
        "tgt_lang": "kn",

        "src_dir": os.path.join(BASE_DIR, "dataset/marathi"),
        "ref_dir": os.path.join(BASE_DIR, "dataset/kannada"),

        "nllb_src": "mar_Deva",
        "nllb_tgt": "kan_Knda",

        "indic_src": "mar_Deva",
        "indic_tgt": "kan_Knda",

        "google_src": "mr",
        "google_tgt": "kn"
    }
]

OUTPUT_BASE_DIR = os.path.join(BASE_DIR, "outputs")
