import os
import glob
import pandas as pd
from jiwer import wer, cer
import sacrebleu
import baselines.preprocess as preprocess
from baselines.config import TRANSLATION_DIRECTIONS, OUTPUT_BASE_DIR

# Map internal model keys to folder names
MODEL_FOLDERS = {
    'Google': 'google',
    'IndicTrans2': 'indictrans',
    'Meta AI': 'meta',
}

def compute_metrics(reference_text, hypothesis_text):
    reference_text = preprocess.normalize_text(reference_text)
    hypothesis_text = preprocess.normalize_text(hypothesis_text)

    return {
        'WER': round(wer(reference_text, hypothesis_text), 4),
        'CER': round(cer(reference_text, hypothesis_text), 4),
        'chrF': round(
            sacrebleu.corpus_chrf([hypothesis_text], [[reference_text]]).score,
            2
        ),
        'BLEU': round(
            sacrebleu.corpus_bleu([hypothesis_text], [[reference_text]]).score,
            2
        )
    }


def evaluate_model(model_name, output_dir, ref_dir):
    rows = []
    # Match output files to reference files
    # output filenames have changed suffix (e.g. _mr.txt -> _kn.txt)
    # We should iterate over output files and find corresponding reference
    
    # Actually, simpler to iterate over reference files and construct expected output filename
    # BUT, our save_output logic replaces suffix.
    # Ref dir contains target language files.
    
    ref_files = glob.glob(os.path.join(ref_dir, '*.txt'))

    for ref_path in ref_files:
        fname = os.path.basename(ref_path)
        hyp_path = os.path.join(output_dir, fname)

        if not os.path.exists(hyp_path):
            continue

        ref_text = preprocess.read_file(ref_path)
        hyp_text = preprocess.read_file(hyp_path)

        if len(ref_text) < 10 or len(hyp_text) < 10:
             # Basic length check, lowered threshold
            continue

        metrics = compute_metrics(ref_text, hyp_text)

        rows.append({
            'Model': model_name,
            'File': fname,
            **metrics
        })

    return rows


def run_evaluation(direction_config):
    direction_name = direction_config['name']
    ref_dir = direction_config['ref_dir']
    
    # Base output dir for this direction: outputs/{direction}
    direction_output_base = os.path.join(OUTPUT_BASE_DIR, direction_name)
    
    print(f"--- Evaluating {direction_name} ---")
    print(f"Reference Dir: {ref_dir}")

    all_rows = []

    for model_display_name, model_folder in MODEL_FOLDERS.items():
        model_output_dir = os.path.join(direction_output_base, model_folder)
        
        if not os.path.exists(model_output_dir):
            print(f"Skipping {model_display_name}: Directory not found ({model_output_dir})")
            continue
            
        print(f"Evaluating {model_display_name}...")
        rows = evaluate_model(model_display_name, model_output_dir, ref_dir)
        all_rows.extend(rows)

    if not all_rows:
        print(f"No results found for {direction_name}")
        return

    df = pd.DataFrame(all_rows)
    df = df.sort_values(by=['Model', 'File'])
    
    report_file = os.path.join(direction_output_base, 'eval_report.csv')
    df.to_csv(report_file, index=False)
    print(f"Saved evaluation report to {report_file}")


def main():
    for direction in TRANSLATION_DIRECTIONS:
        run_evaluation(direction)


if __name__ == "__main__":
    main()