import os
import glob
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from IndicTransToolkit import IndicProcessor
from tqdm import tqdm
import baselines.preprocess as preprocess
from baselines.hf_compact_patches import apply_hf_patches
from baselines.config import TRANSLATION_DIRECTIONS, OUTPUT_BASE_DIR

apply_hf_patches()

MODEL_NAME = 'ai4bharat/indictrans2-indic-indic-1B'
BATCH_SIZE = 8


def load_model():
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    if torch.backends.mps.is_available():
        device = 'mps'

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    dtype = torch.float16 if device in ['cuda', 'mps'] else torch.float32

    model = AutoModelForSeq2SeqLM.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
        torch_dtype=dtype
    ).to(device)

    model.eval()
    processor = IndicProcessor()
    return tokenizer, model, processor, device


def translate_batch(texts, tokenizer, model, processor, device, src_lang, tgt_lang):
    batch = processor.preprocess_batch(texts, src_lang, tgt_lang)
    inputs = tokenizer(batch, return_tensors='pt', padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=256)

    decoded = tokenizer.batch_decode(outputs, skip_special_tokens=True)
    return processor.postprocess_batch(decoded, lang=tgt_lang)


def process_file(filepath, tokenizer, model, processor, device, direction_config, output_dir):
    content = preprocess.read_file(filepath)
    lines = content.splitlines()

    flat_sentences = []
    structure = []

    for line in lines:
        if not line.strip():
            structure.append(0)
            continue

        src_lang_code = direction_config['src_lang']
        sents = preprocess.split_sentences(line, lang=src_lang_code)
        flat_sentences.extend(sents)
        structure.append(len(sents))

    translations = []
    
    src_code = direction_config['indic_src']
    tgt_code = direction_config['indic_tgt']

    for i in tqdm(range(0, len(flat_sentences), BATCH_SIZE)):
        chunk = flat_sentences[i:i + BATCH_SIZE]
        translations.extend(
            translate_batch(chunk, tokenizer, model, processor, device, src_code, tgt_code)
        )

    rebuilt = []
    idx = 0
    for count in structure:
        if count == 0:
            rebuilt.append("")
        else:
            rebuilt.append(" ".join(translations[idx:idx + count]))
            idx += count

    save_output(filepath, rebuilt, output_dir, direction_config)


def save_output(filepath, lines, output_dir, direction_config):
    os.makedirs(output_dir, exist_ok=True)
    basename = os.path.basename(filepath)
    src_suffix = f"_{direction_config['src_lang']}.txt"
    tgt_suffix = f"_{direction_config['tgt_lang']}.txt"
    
    out_name = basename.replace(src_suffix, tgt_suffix)
    if out_name == basename:
         out_name = os.path.splitext(basename)[0] + tgt_suffix

    out_path = os.path.join(output_dir, out_name)
    preprocess.save_file(out_path, "\n".join(lines))


def run_translation(tokenizer, model, processor, device, direction_config):
    direction_name = direction_config['name']
    src_dir = direction_config['src_dir']
    
    # Output: outputs/{direction}/indictrans
    output_dir = os.path.join(OUTPUT_BASE_DIR, direction_name, 'indictrans')
    
    print(f"--- Running {direction_name} ({direction_config['indic_src']} -> {direction_config['indic_tgt']}) ---")
    print(f"Source: {src_dir}")
    print(f"Output: {output_dir}")

    files = glob.glob(os.path.join(src_dir, '*.txt'))
    if not files:
        print(f"Warning: No files found in {src_dir}")
        return

    for f in files:
        process_file(f, tokenizer, model, processor, device, direction_config, output_dir)


def main():
    tokenizer, model, processor, device = load_model()
    
    for direction in TRANSLATION_DIRECTIONS:
        run_translation(tokenizer, model, processor, device, direction)


if __name__ == "__main__":
    main()