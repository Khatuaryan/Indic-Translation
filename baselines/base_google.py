import os
import glob
import time
from google.cloud import translate_v2 as translate
import baselines.preprocess as preprocess
from baselines.config import TRANSLATION_DIRECTIONS, OUTPUT_BASE_DIR

from baselines.config import BASE_DIR
GOOGLE_KEY_PATH = os.path.join(BASE_DIR, 'google-key.json')


def setup_google_client():
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_KEY_PATH
    return translate.Client()


def translate_batch(client, texts, src, target):
    idx_map = [i for i, t in enumerate(texts) if t.strip()]
    valid_texts = [texts[i] for i in idx_map]

    if not valid_texts:
        return texts

    results = []
    BATCH_SIZE = 100

    for i in range(0, len(valid_texts), BATCH_SIZE):
        chunk = valid_texts[i:i + BATCH_SIZE]
        response = client.translate(
            chunk,
            source_language=src,
            target_language=target
        )
        results.extend(response)
        time.sleep(0.1)  # avoid throttling

    output = list(texts)
    for idx, res in zip(idx_map, results):
        output[idx] = res['translatedText']

    return output


def process_file(client, filepath, direction_config, output_dir):
    content = preprocess.read_file(filepath)
    lines = content.splitlines()

    flat_sentences = []
    structure = []

    for line in lines:
        if not line.strip():
            structure.append(0)
            continue

        # Use 'kn' for split logic if src is Kannada, else generic or add logic to preprocess
        # For simplicity, assuming 'kn' works or default behavior is acceptable for basic split
        # Ideally preprocess.split_sentences should takelang arg derived from config
        src_lang_code = direction_config['src_lang']
        sents = preprocess.split_sentences(line, lang=src_lang_code)
        flat_sentences.extend(sents)
        structure.append(len(sents))

    translated = translate_batch(
        client, 
        flat_sentences, 
        src=direction_config['google_src'], 
        target=direction_config['google_tgt']
    )

    rebuilt_lines = []
    idx = 0
    for count in structure:
        if count == 0:
            rebuilt_lines.append("")
        else:
            rebuilt_lines.append(" ".join(translated[idx:idx + count]))
            idx += count

    save_output(filepath, rebuilt_lines, output_dir, direction_config)


def save_output(filepath, lines, output_dir, direction_config):
    os.makedirs(output_dir, exist_ok=True)
    basename = os.path.basename(filepath)
    # Generic replacement: replace src_lang with tgt_lang in filename if present
    src_suffix = f"_{direction_config['src_lang']}.txt"
    tgt_suffix = f"_{direction_config['tgt_lang']}.txt"
    
    out_name = basename.replace(src_suffix, tgt_suffix)
    if out_name == basename:
         out_name = os.path.splitext(basename)[0] + tgt_suffix

    out_path = os.path.join(output_dir, out_name)
    preprocess.save_file(out_path, "\n".join(lines))


def run_translation(client, direction_config):
    direction_name = direction_config['name']
    src_dir = direction_config['src_dir']
    
    # Construct output directory: outputs/{direction}/google
    output_dir = os.path.join(OUTPUT_BASE_DIR, direction_name, 'google')
    
    print(f"--- Running {direction_name} ({direction_config['src_lang']} -> {direction_config['tgt_lang']}) ---")
    print(f"Source: {src_dir}")
    print(f"Output: {output_dir}")

    files = glob.glob(os.path.join(src_dir, '*.txt'))
    if not files:
        print(f"Warning: No files found in {src_dir}")
        return

    for f in files:
        process_file(client, f, direction_config, output_dir)


def main():
    client = setup_google_client()
    
    for direction in TRANSLATION_DIRECTIONS:
        run_translation(client, direction)


if __name__ == "__main__":
    main()