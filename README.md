# 🔍 SearchTogether

This is a project for the **"Metody w Nauce Obliczeniowej i Technice"** course (2024/2025) at **AGH University of Science and Technology** in Kraków.

The goal of this project is to build a simple **search engine** with a built-in **web interface** for debugging and testing. It uses **Latent Semantic Indexing (LSI)** based on **Singular Value Decomposition (SVD)** and **IDF weighting** to improve search results.

The search engine comes with some sample data - relatedly to its name it contains content from Wikipedia related to **Adrian Zandberg** and his article's neighbours (and their neighbours too).

---

## 🗂️ Repo Structure

- **`scrapping/`** – Scripts for downloading and pre-processing Wikipedia data
- **`website/`** – The frontend and main search logic
- **`scrapping/bots/`** – Small proof-of-concept bot used to build the early dataset
- **`website/assets/`** – Datasets (CSV) and pre-processed data files (Parquet) for faster performance

---

## 🕸 Scraping Pipeline

### 🔧 Assumptions

To run the full data pipeline, we assume:

- You have downloaded the most recent Wikipedia dump:
  `enwiki-latest-pages-articles-multistream.xml.bz2`
- You’ve placed this file in the `scrapping/` folder.
- You’ve run the [`WikiExtractor`](https://github.com/attardi/wikiextractor) like so:

```bash
python -m wikiextractor.WikiExtractor --json -o extracted enwiki-latest-pages-articles-multistream.xml.bz2
```

This generates a folder called `extracted/` with JSON-formatted articles.

---

### 🧱 Script Overview

1. **`backlinks.py`**
   Finds titles of relevant Wikipedia articles (starting from Zandberg's and expanding to neighbours). Saves them in `titles.json`.

2. **`makecsv.py`**
   Searches through all extracted articles and builds a CSV containing:

   - Title
   - Link
   - Article content

> 💡 A smaller dataset is also included (gathered using the bot in `/bots`). It was used for testing, to avoid stressing Wikipedia's servers too much.

---

## 🌐 Website App (Frontend)

The frontend is built using **[NiceGUI](https://nicegui.io/)**, a Python-based GUI library with **Vue.js**-powered styling.

### 🧪 UI Features

The main interface includes:

- A **search bar (obviously)**
- A **results section**
- A **settings menu** for:

  - Enabling/disabling **IDF weighting**
  - Adjusting the **k-factor** for dimensionality reduction in LSI
  - Selecting between different **search methods**

### 🔍 Available Search Modes

| Mode              | Description                                                               |
| ----------------- | ------------------------------------------------------------------------- |
| **Basic**         | Compares bag-of-words using correlation                                   |
| **Normalized**    | Uses normalized vectors for comparison                                    |
| **Noise Reduced** | Applies low-rank approximation (LSI via SVD) to improve semantic matching |

### ▶️ How to Run

To launch the app:

1. Install requirements:

```bash
pip install -r requirements.txt
```

2. Start the app from the `website/` folder:

```bash
python main.py
```

---

## 📦 Datasets & Assets

All preprocessed datasets and matrix files are stored in the `assets/` folder:

- **`terms.parquet`** – list of all terms
- **`bag.parquet`** – bag-of-words representation
- **`idf.parquet`** – IDF scores for terms
- **`temp/`** – smaller Polish dataset for demo/testing

---

## 🧠 Backend (How the Search Works)

Here’s a high-level look at the backend search pipeline (from `scripts.py`):

### 🧬 `search()` function (Simplified Explanation)

```python
def search(query, idf, searchtype, samplek, howmanyresults):
```

#### What it does:

1. **Loads the data** from CSV and cleans the article text and search query using `clear_text`
2. **Prepares term data**:

   - Tries to load from `terms.parquet`
   - If not available, it builds from scratch and saves

3. **Builds a bag-of-words matrix** (or loads it if it already exists).
4. **Optionally applies IDF**:

   - If enabled, loads from `idf.parquet` or calculates and saves it.

5. **Runs the selected search algorithm**:

   - `dumb`: Basic bag-of-words search
   - `dumbvec`: Bag-of-words using vector math
   - `smart`: LSI-based search using SVD and dimensionality reduction

6. **Returns the final search results** nicely formatted.

---

## 🧪 Sample Output

> todo - add screenshots

---
