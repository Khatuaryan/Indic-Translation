import os
import glob
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from tqdm import tqdm
import Baseline.setup.preprocess as preprocess
from Baseline.setup.config import TRANSLATION_DIRECTIONS, OUTPUT_BASE_DIR

# Constants
MODEL_NAME = 'facebook/nllb-200-distilled-600M'
BATCH_SIZE = 8  # Reduced for stability

def load_model():
    """
    Load NLLB-200 model and tokenizer.
    Supports CUDA, MPS (Apple Silicon), and CPU.
    """
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    if torch.backends.mps.is_available():
        device = 'mps'

    print(f"Loading {MODEL_NAME} on {device}...")
    
    # Use FP16 for MPS/CUDA to save memory and speed up
    dtype = torch.float16 if device in ['cuda', 'mps'] else torch.float32
    
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(
        MODEL_NAME, 
        torch_dtype=dtype
    ).to(device)
    model.eval()
    
    return tokenizer, model, device

def translate_batch(texts, tokenizer, model, device, src_lang, tgt_lang):
    """
    Translate a batch of sentences using NLLB-200.
    """
    # NLLB expects source language to be set in tokenizer
    tokenizer.src_lang = src_lang
    
    inputs = tokenizer(
        texts, 
        return_tensors='pt', 
        padding=True, 
        truncation=True, 
        max_length=512
    ).to(device)

    # Force target language token index as the first generated token
    forced_bos_token_id = tokenizer.lang_code_to_id[tgt_lang]

    with torch.no_grad():
        generated_tokens = model.generate(
            **inputs, 
            forced_bos_token_id=forced_bos_token_id, 
            max_length=512,
            num_beams=1, # Greedy search for speed
            do_sample=False
        )

    translations = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
    return translations

def process_file(filepath, tokenizer, model, device, direction_config, output_dir):
    """
    Read file, split into sentences, translate batch-wise, and save.
    """
    content = preprocess.read_file(filepath)
    lines = content.splitlines()

    flat_sentences = []
    structure = []  # To keep track of how many sentences per line/paragraph

    # Pre-process: flatten structure for batching
    for line in lines:
        if not line.strip():
            structure.append(0)
            continue
        
        src_lang_code = direction_config['src_lang']
        sents = preprocess.split_sentences(line, lang=src_lang_code)
        flat_sentences.extend(sents)
        structure.append(len(sents))

    if not flat_sentences:
        save_output(filepath, [""] * len(lines), output_dir, direction_config)
        return

    # Translate in batches
    translations = []
    
    src_code = direction_config['nllb_src']
    tgt_code = direction_config['nllb_tgt']
    
    for i in tqdm(range(0, len(flat_sentences), BATCH_SIZE), desc=f"Translating {os.path.basename(filepath)}"):
        chunk = flat_sentences[i:i + BATCH_SIZE]
        translations.extend(translate_batch(chunk, tokenizer, model, device, src_code, tgt_code))

    # Reconstruct document structure
    rebuilt_lines = []
    idx = 0
    for count in structure:
        if count == 0:
            rebuilt_lines.append("")
        else:
            # Join sentences with space (standard for reconstructed text)
            rebuilt_lines.append(" ".join(translations[idx:idx + count]))
            idx += count

    save_output(filepath, rebuilt_lines, output_dir, direction_config)

def save_output(filepath, lines, output_dir, direction_config):
    """
    Save the translated lines to the output directory.
    """
    os.makedirs(output_dir, exist_ok=True)
    basename = os.path.basename(filepath)
    src_suffix = f"_{direction_config['src_lang']}.txt"
    tgt_suffix = f"_{direction_config['tgt_lang']}.txt"
    
    out_name = basename.replace(src_suffix, tgt_suffix)
    if out_name == basename:
         out_name = os.path.splitext(basename)[0] + tgt_suffix
        
    out_path = os.path.join(output_dir, out_name)
    preprocess.save_file(out_path, "\n".join(lines))

def run_translation(tokenizer, model, device, direction_config):
    direction_name = direction_config['name']
    src_dir = direction_config['src_dir']
    
    # Output: outputs/{direction}/meta
    output_dir = os.path.join(OUTPUT_BASE_DIR, direction_name, 'meta')
    
    print(f"--- Running {direction_name} ({direction_config['nllb_src']} -> {direction_config['nllb_tgt']}) ---")
    print(f"Source: {src_dir}")
    print(f"Output: {output_dir}")

    files = glob.glob(os.path.join(src_dir, '*.txt'))
    if not files:
        print(f"Warning: No files found in {src_dir}")
        return

    print(f"Found {len(files)} files to translate.")
    for f in files:
        process_file(f, tokenizer, model, device, direction_config, output_dir)
        
    print(f"Translation complete for {direction_name}.")

def main():
    tokenizer, model, device = load_model()
    
    for direction in TRANSLATION_DIRECTIONS:
        run_translation(tokenizer, model, device, direction)

if __name__ == "__main__":
    main()
