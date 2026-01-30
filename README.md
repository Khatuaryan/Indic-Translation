# Indic Translation: Kannada ↔ Marathi

This project implements bidirectional translation between Kannada (kn) and Marathi (mr) using multiple baseline models:
- Google Translate API
- IndicTrans2 (AI4Bharat)
- Meta NLLB (No Language Left Behind)

It includes scripts for processing datasets, running translations, and evaluating results using BLEU, CHRF, and WER metrics.

## Setup

### Prerequisites

- Python 3.9+
- [Git LFS](https://git-lfs.com/) (required for model weights)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd Indic-Translation
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: `IndicTransToolkit` is installed directly from GitHub as per `requirements.txt`.*

### Configuration

#### Google Translate
To use the Google Translate baseline, you must provide a valid service account JSON key.
1. Place your `google-key.json` file in the project root.
2. **Important**: Ensure this file is ignored by git (it is added to `.gitignore` by default).

## Usage

### Running Baselines

The baselines are located in the `baselines/` directory. Each script supports bidirectional translation based on the configurations defined in `baselines/config.py`.

**1. Google Translate Baseline:**
```bash
python baselines/base_google.py
```

**2. IndicTrans2 Baseline:**
```bash
python baselines/base_indictrans.py
```

**3. Meta NLLB Baseline:**
```bash
python baselines/base_meta.py
```

### Evaluation

After running the baselines, translation outputs are saved in the `outputs/` directory structure:
`outputs/<direction>/<model>/`

To evaluate all generated translations:
```bash
python baselines/base_evaluate.py
```
This will generate evaluation reports (e.g., `evaluation_report.txt`) in the respective output folders.

## Project Structure

- `baselines/`: Contains the main scripts for models and evaluation.
  - `config.py`: Central configuration for translation directions and paths.
  - `base_*.py`: Model-specific translation scripts.
  - `base_evaluate.py`: Evaluation script using SacreBLEU and JiWER.
- `dataset/`: Contains source and reference files for translation.
- `outputs/`: (Generated) Stores translation results and evaluation reports.
- `requirements.txt`: Python package dependencies.
