# Indic Translation Project

## Overview
This project focuses on Indic language translation, specifically between Kannada (kn), Marathi (mr), and English (en).

The repository is organized into multiple components:

-   **[Baseline Models](./Baseline/README.md)**: Contains baseline translation models (Google Translate, IndicTrans2, Meta NLLB) and evaluation scripts.
-   **[Glossary Creation](./Glossary/)**: Scripts and resources for creating glossaries for English, Marathi, and Kannada. *(Documentation in progress)*

## Quick Start

This repository is a collection of independent sub-projects. You can clone the entire repository and navigate to the specific project you need.

### Option 1: Full Repository Setup (Recommended)
Use this if you plan to explore multiple components or want the complete codebase.

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd Indic-Translation
    ```

2.  **Navigate to a sub-project:**
    *   For Translation Models: `cd Baseline`
    *   For Glossary Tools: `cd Glossary`

### Option 2: Single Sub-project Setup (Advanced)
If you only need a specific component (e.g., just the `Baseline` models) and want to save disk space, you can use a sparse checkout.

1.  **Initialize a new repository:**
    ```bash
    mkdir Indic-Translation && cd Indic-Translation
    git init
    git remote add origin <repository_url>
    ```

2.  **Enable sparse checkout and download only the desired folder:**
    ```bash
    git config core.sparseCheckout true
    # Replace 'Baseline/' with the directory you want (e.g., 'Glossary/')
    echo "Baseline/" >> .git/info/sparse-checkout
    git pull origin main
    ```

3.  **Navigate to the folder:**
    ```bash
    cd Baseline
    ```

### Next Steps

Once you have navigated to your desired sub-project, you **must** follow its specific documentation for setup and usage.

*   **[Read Baseline Documentation](./Baseline/README.md)**
*   *(Glossary documentation coming soon)*

## Project Structure

-   **`Baseline/`**: Core translation models and evaluation logic.  
    *(Self-contained environment for running translation experiments)*
-   **`Glossary/`**: Glossary generation tools.
-   `requirements.txt`: Common dependencies (check sub-projects for specific requirements).

