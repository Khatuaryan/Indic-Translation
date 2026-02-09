# Baseline Translation Models

This directory contains the baseline translation models and evaluation scripts for Indic language translation (Kannada ↔ Marathi).

## Models Implemented
- **Google Translate API**
- **IndicTrans2 (AI4Bharat)**
- **Meta NLLB (No Language Left Behind)**

## Dataset Information

**Note:** The dataset used in this baseline is a sample of a much larger dataset.

>   **Full Dataset Access:**
>   If you wish to access the entire open-source dataset, please visit:
>   [https://ar5iv.labs.arxiv.org/html/2001.09907](https://ar5iv.labs.arxiv.org/html/2001.09907)

## Setup

### Prerequisites

- Python 3.10+
- [Git LFS](https://git-lfs.com/) (required for model weights)

### Installation

1.  Navigate to the project root (if you haven't already):
    ```bash
    cd Indic-Translation
    ```

2.  Create and activate a virtual environment (recommended):
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: `IndicTransToolkit` is installed directly from GitHub as per `requirements.txt`.*

### Configuration

#### Google Translate
To use the Google Translate baseline, you must provide a valid service account JSON key.
1.  Place your `google-key.json` file in the project root (parent directory of `Baseline`).
2.  **Important**: Ensure this file is ignored by git.

## Usage

**Note:** All commands below assume you are inside the `Baseline` directory or running from the project root with adjusted paths. The scripts are designed to be flexible, but staying consistent helps.

If you are in the `Baseline` directory:
```bash
cd Baseline
```

### Running Models

**1. Google Translate Baseline:**
```bash
python models/base_google.py
```

**2. IndicTrans2 Baseline:**
```bash
python models/base_indictrans.py
```

**3. Meta NLLB Baseline:**
```bash
python models/base_meta.py
```

### Evaluation

After running the baselines, translation outputs are saved in the `outputs/` directory.

To evaluate all generated translations:
```bash
python models/base_evaluate.py
```
This will generate evaluation reports (e.g., `evaluation_report.txt`) in the respective output folders.

## Directory Structure

-   `models/`: Contains the main scripts for models (`base_*.py`) and evaluation (`base_evaluate.py`).
-   `config.py`: Central configuration for translation directions and paths.
-   `dataset/`: Contains source and reference files for translation.
-   `outputs/`: (Generated) Stores translation results and evaluation reports.
