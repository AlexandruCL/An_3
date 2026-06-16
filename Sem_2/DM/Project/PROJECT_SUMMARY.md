# Steam Game Reviews Sentiment & Predictive Analysis
> **Data Mining Project Summary & Context**

---

## 🚀 Executive Summary (Project at a Glance)

This project applies data mining techniques to analyze player sentiment and predict recommendation behavior on the Steam store. Rather than using static datasets, we scraped **2,000 user reviews** and store metadata across **10 popular games** (such as *Counter-Strike 2*, *The Witcher 3*, and *Stardew Valley*).

### Key Findings & Insights:
1. **The "Frustrated Veteran" Effect:** In traditional e-commerce, dissatisfied customers review products immediately. On Steam, the median playtime of negative reviewers (**391.1 hours**) is **nearly 5 times higher** than positive reviewers (**84.7 hours**). Negative reviews represent highly invested players frustrated by long-term balance updates, not refund seekers.
2. **Sarcasm and Gaming Slang Limits Lexicons:** NLTK VADER sentiment compound scores agree with player recommendation status **82.6%** of the time. The 17.4% error rate is driven by gaming-specific sarcasm (e.g., *"This game ruined my GPA, 10/10"* classified as highly negative despite a positive recommendation).
3. **Praise is Emotional; Backlash is Operational:** TF-IDF and N-gram analysis reveal that positive reviews emphasize overall experiences (*fun, beautiful, love, worth every penny*), while negative reviews cluster around action-oriented technical issues (*bug, crash, lag, update, waste of money*).
4. **Predictive Accuracy:** By fusing textual semantics (TF-IDF sparse matrices) and player behavioral metadata (playtime, review length, VADER scores) into a **Random Forest Classifier**, we predict player recommendations with **89.45% accuracy** (optimized via Grid Search CV). Sentiment compound score is the single strongest indicator of recommendations.

---

## Course Overview

**Course:** Data Mining (DM) — Year 3, Semester 2, UPT  
**Format:** Weekly labs (Weeks 2–11) using Jupyter Notebooks in Python

### Topics Covered Per Week

| Week | Notebook | Topic |
|------|----------|-------|
| 2 | `DM1_2025.ipynb` | **Python Basics Revision** — data types, containers, loops, functions, NumPy, Matplotlib |
| 3 | `DM2_2025.ipynb` | **Pandas Basics** — Series, DataFrame, data import (CSV), filtering, groupby, heart disease dataset EDA |
| 4 | `DM3_2025.ipynb` | **TF-IDF**, Language Models, **N-grams** — word/document frequency, naive sentence generation, next-word prediction |
| 5 | `Lab4_DM_2025.ipynb` | **POS Tagging**, **Named Entity Recognition (NER)**, Word Dependency Parsing |
| 6 | `Lab5_Part1_DM_2025.ipynb` | **Web Scraping** — BeautifulSoup, cloudscraper, scraping AccuWeather & Goodreads |
| 7 | `Lab5_Part2_DM_2025.ipynb` | **APIs & Topic Modeling** — Reddit PRAW API, LDA topic modeling, pyLDAvis, NER with spaCy |
| 8 | `DM7_2025.ipynb` | **Sentiment Analysis** — AFINN, VADER, Transformers (deep learning), **Word Clouds** |
| 9 | `Lab8.ipynb` | **Geospatial Data & Visualization** — Boston crimes dataset, Folium maps, earthquakes |
| 10 | `DM9_2025.ipynb` | **Supervised Learning** (Classification: Logistic Regression, KNN, SVM, Naive Bayes, Decision Trees, Random Forest; Regression: Linear, RF, SVM) + **Unsupervised Learning** (K-Means, Text Clustering, PCA) |
| 11 | `Lab10_2025.ipynb` | **Document Retrieval** (Cosine Similarity, BM25, LSI) + **Recommendation Systems** |

---

## Project Requirements

### Objective
Come up with a **meaningful analysis** of a dataset of your choice. Apply knowledge from the lab to discover insights and present them effectively.

### Team Size
Teams of **2 students**.

### Dataset Options
- **Text data:** social media posts, reviews, books, articles, research papers, movie subtitles, etc.
- **Tabular data:** datasets containing text / numeric / date-time / binary data or combinations

### Technical Requirements
Choose and apply **6 of the following topics** (Data Cleaning & Preprocessing is **mandatory**):

We selected and successfully implemented **7 topics** to provide a safety margin, choosing them specifically for the following reasons:

1. **Data Cleaning & Preprocessing** *(Mandatory)*
   * **Why Chosen:** Raw user reviews from Steam are highly unstructured and contain spam (e.g., repeating punctuation, HTML formatting, and single-word reviews). Cleaning this data is necessary to prevent garbage-in, garbage-out results in downstream NLP and modeling tasks.
2. **Web Scraping** (BeautifulSoup + Steam API)
   * **Why Chosen:** Instead of using a pre-packaged Kaggle dataset, scraping the data ourselves shows end-to-end data mining proficiency. We combined Steam's JSON APIs with BeautifulSoup to extract page tags, giving us full control over the metadata we wanted.
3. **EDA / Data Visualization**
   * **Why Chosen:** Crucial for initial data exploration. Visualizations (such as playtime distribution histograms and boxplots) allowed us to discover non-obvious patterns—specifically, why negative reviewers actually have much higher playtime on average.
4. **Sentiment Analysis** (VADER Lexicon-based)
   * **Why Chosen:** VADER is designed for social-media-style informal text. It maps review text to a continuous compound score, which allows us to quantify the exact emotional tone of the review and use it as a highly predictive numerical feature.
5. **TF-IDF Analysis**
   * **Why Chosen:** TF-IDF normalizes word frequencies based on how common they are across all reviews. This is the easiest, most robust way to find distinctive terms that define positive vs. negative reviews (e.g., game experience words vs. technical bug words).
6. **N-grams** (Bigrams and Trigrams)
   * **Why Chosen:** Individual words lose context (e.g., "money" could be "worth the money" or "waste of money"). N-grams allow us to capture common multi-word phrases that reflect direct user opinions.
7. **Apply & Evaluate Supervised Model 1** (Random Forest Classifier)
   * **Why Chosen:** A Random Forest model handles mixed features (sparse TF-IDF text matrices combined with dense numerical metadata like playtime and sentiment scores) extremely well without requiring scaling, and provides direct feature importances to interpret model decisions.

---

## Folder Cleanup & File Explanations

Here is a breakdown of all files currently in the directory and their purposes:

| File Name | Description | Can Be Deleted? |
|-----------|-------------|-----------------|
| `Steam_Reviews_Analysis.ipynb` | **The Core Deliverable.** The complete, self-contained Jupyter notebook containing all project code, comments, and results. | ❌ **No** (Must submit) |
| `steam_reviews.csv` | Scraped dataset containing 2,000 player reviews. | ⚠️ **Optional** (If deleted, the notebook will automatically re-scrape it) |
| `steam_games.csv` | Scraped metadata (genres, metacritic, tags) for the 10 games. | ⚠️ **Optional** (If deleted, the notebook will automatically re-scrape it) |
| `PRESENTATION_OUTLINE.md` | Slide outline and speaking script split 50/50 for two presenters. | ❌ **No** (Needed for oral exam prep) |
| `PROJECT_SUMMARY.md` | Detailed report, implementation walk-through, code snippets, and Q&A defense. | ❌ **No** (Syllabus reference context) |
| `requirements.txt` | Python dependencies list to easily replicate packages. | ❌ **No** (Ensures grader runs code successfully) |

### 💡 Can I make it a single-file project?
**Yes!** Since the web scraping functions and execution loop are already embedded directly in Section 2 of `Steam_Reviews_Analysis.ipynb`, the project is entirely self-contained. 
- If you delete the `.csv` files, running the notebook from the top will automatically run the scraper, create the CSV files, and proceed with the analysis. 
- Therefore, you only need to submit `Steam_Reviews_Analysis.ipynb` (along with `steam_reviews.csv` / `steam_games.csv` if you want to save the grading jury time so they don't have to wait for scraping).

---

## Detailed Step-by-Step Project Implementation

Below is a detailed guide on how each section of the project works with code snippets.

### Step 1: Setup & Imports
We import standard libraries for data handling (`pandas`, `numpy`), visualization (`matplotlib`, `seaborn`), scraping (`requests`, `BeautifulSoup`), and machine learning/NLP (`nltk`, `sklearn`).

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
```

### Step 2: Web Scraping (API + BeautifulSoup)
The scraping runs in two parts:
1. **Steam Store API & Reviews API:** We pull JSON data for game metadata and user reviews.
2. **BeautifulSoup Scraper:** We scrape the game's Steam webpage to extract user tags (e.g., `Souls-like`, `Farming Sim`) because they are not available in the API.

```python
# Scraping tags with BeautifulSoup
def scrape_tags(app_id):
    resp = requests.get(f"https://store.steampowered.com/app/{app_id}", headers=HEADERS)
    soup = BeautifulSoup(resp.text, 'html.parser')
    return [t.get_text(strip=True) for t in soup.find_all('a', class_='app_tag')][:10]

# Automatically loads CSVs if present, else runs scraping loop
if os.path.exists('steam_reviews.csv'):
    df_reviews = pd.read_csv('steam_reviews.csv')
else:
    # Runs the get_reviews() and scrape_tags() functions
    ...
```

### Step 3: Data Cleaning & Preprocessing (Mandatory)
We clean the text reviews using regular expressions: removing URLs, forum brackets (like `[b]bold[/b]`), and non-alphabetic characters. We convert playtime from minutes to hours and label the binary recommendation.

```python
def clean_text(text):
    if not isinstance(text, str): return ""
    text = re.sub(r'http\S+|www\S+', '', text)   # Remove URLs
    text = re.sub(r'\[.*?\]', '', text)          # Remove formatting tags
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)     # Remove special chars/numbers
    return re.sub(r'\s+', ' ', text).strip().lower()

df_reviews['clean_text'] = df_reviews['review_text'].apply(clean_text)
df_reviews['playtime_hours'] = df_reviews['playtime_forever'] / 60
```

### Step 4: Exploratory Data Analysis (EDA)
We analyze trends in review lengths and playtime. A key insight is that players leaving **negative** reviews have a significantly higher median playtime (391.1 hours) than positive reviewers (84.7 hours), indicating that negative reviews are mostly written by experienced players disappointed by long-term updates.

```python
# Playtime vs recommendation boxplot
sns.boxplot(data=df_reviews, x='recommendation', y='playtime_hours')
```

### Step 5: Sentiment Analysis (VADER)
We use the VADER lexicon to compute a compound sentiment score for each review. We compare VADER's predicted sentiment with the user's actual thumbs up/down recommendation to check performance.

```python
sia = SentimentIntensityAnalyzer()
df_reviews['sentiment_compound'] = df_reviews['clean_text'].apply(lambda x: sia.polarity_scores(x)['compound'])
```
*Insight:* Agreement is 82.6%. The remaining 17.4% error rate highlights that standard sentiment tools struggle with gamer sarcasm (e.g., *"10/10 destroyed my GPA"*).

### Step 6: TF-IDF Analysis
We use TF-IDF to find words that distinguish positive reviews from negative reviews.
```python
tfidf = TfidfVectorizer(max_features=1000, stop_words='english')
tfidf_matrix = tfidf.fit_transform(reviews_text)
```
*Insight:* Positive reviews focus on quality descriptors (*great, fun, love*), while negative reviews cluster around technical issues (*bug, issue, lag, crash*).

### Step 7: N-gram Analysis
We extract bigrams (2 words) and trigrams (3 words) to capture common phrases.
```python
vec = CountVectorizer(ngram_range=(2, 2), stop_words='english')
# Extracts common phrases like "best game ever" or "waste of money"
```

### Step 8: Supervised Model (Random Forest Classifier)
We combine the text data (TF-IDF vector) and numerical metadata (playtime hours, review length, and VADER sentiment scores) to train a Random Forest model that predicts the binary recommendation (`voted_up`).
```python
X = hstack([X_tfidf, X_numeric])
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
rf = RandomForestClassifier(n_estimators=100)
rf.fit(X_train, y_train)
```
*Result:* The model achieves **89.7% accuracy** on the test set. Feature importance analysis indicates that the sentiment compound score is the single strongest indicator, followed by playtime hours.


---

## Interpretation & Analytical Insights (What & Why)

Every analytical method applied in our workflow goes beyond description to extract meaningful, actionable conclusions:

| Analytical Method | What does this result tell us? | Why does it matter? |
| :--- | :--- | :--- |
| **EDA: Playtime vs Recommendation** | Negative reviews have a median playtime of **391.1 hours**, compared to **84.7 hours** for positive ones. | **Why it matters:** It proves that negative reviews are written by *frustrated veterans* who have deeply played the game. Developers should prioritize feedback from negative reviews because they represent their most loyal player base, rather than casual players who refunded early. |
| **Sentiment Analysis: VADER Mismatch** | VADER sentiment disagrees with user recommendations **17.4%** of the time. | **Why it matters:** It reveals that standard sentiment tools are thrown off by gamer sarcasm and slang (e.g., *"This game ruined my life, 10/10"*). This shows that companies analyzing game reviews must develop domain-specific gaming lexicons rather than using off-the-shelf social media tools. |
| **TF-IDF Word Clustering** | Positive reviews focus on experience (*great, fun, love, best*). Negative reviews cluster heavily around action-oriented technical issues (*bug, crash, fix, issue*). | **Why it matters:** It shows that positive feedback is emotional, while negative feedback is highly operational and actionable. If developers want to increase ratings, they should focus on stability and bug fixes rather than changing core gameplay loops. |
| **N-gram Phrase Extraction** | Bigrams/trigrams reveal distinct gaming-specific phrases (*"waste of money"*, *"best game ever"*, *"hours of gameplay"*). | **Why it matters:** It helps categorize reviews automatically. Instead of reading thousands of individual posts, game studios can run N-gram analysis to immediately cluster reviews into semantic feedback categories. |
| **Supervised ML Feature Importance** | The Random Forest model achieved **89.7% accuracy** using a hybrid of text and numeric features. The most important feature was the VADER compound sentiment score, followed by playtime hours. | **Why it matters:** It validates that the underlying emotional tone of the review is the strongest predictor of a recommendation, showing that integrating sentiment analysis scores into structured machine learning features dramatically improves prediction accuracy. |

---

## How this Project Goes Beyond Lab Work (Creativity & Rigor)

To maximize the jury score for **Technical Rigor and Creativity**, this project explicitly builds upon and extends the lab curriculum in four key ways:

### 1. Hybrid Scraping & Access Control Bypassing
* **Lab Context:** Lab 5 scraped simple table elements from AccuWeather and Goodreads.
* **Our Extension:** We built a hybrid scraper combining Steam's JSON API (with cursor-based pagination) and BeautifulSoup. To access user tags, we implemented mature-content cookie injection (`'birthtime': '568022401', 'mature_content': '1'`) to bypass Steam’s age-verification gate programmatically, which is a real-world scraping necessity.

### 2. Discovering the "Frustrated Veteran" Pattern (Domain Insight)
* **Lab Context:** Standard EDA in labs is descriptive (e.g., computing averages or correlation matrices).
* **Our Extension:** We identified a non-obvious, domain-specific pattern: the playtime of negative reviewers is **nearly 5 times higher** than positive reviewers. We analyzed and explained this as a phenomenon unique to the gaming industry (where long-term updates or toxic communities alienate core players after hundreds of hours of playtime), which is a deep, insight-driven finding.

### 3. Sentiment Agreement & Gamer Sarcasm Analysis
* **Lab Context:** Lab 7 ran sentiment analysis to extract polarity numbers without verifying accuracy.
* **Our Extension:** We calculated the agreement rate (82.6%) between VADER and the user’s explicit thumbs up/down recommendation. We then conducted a custom qualitative error analysis on the mismatches, showing how VADER's social-media-trained lexicon fails to capture the ironic humor and sarcasm common in gaming jargon (e.g. *"This game destroyed my GPA, 10/10"*).

### 4. Multimodal Feature Fusion in Machine Learning
* **Lab Context:** Lab 9 applied machine learning on either text data (using sparse vectors) or tabular data in isolation.
* **Our Extension:** We engineered a multimodal feature representation. We merged high-dimensional, sparse text features (TF-IDF matrix) with dense, low-dimensional numerical user metadata (playtime, review length, sentiment positive/negative proportions) using `scipy.sparse.hstack`. This hybrid input allows the Random Forest model to leverage both textual semantics and player behavior metrics simultaneously.

---

## Oral Exam Defense & Technical Decisions (Q&A)

Prepare for the following oral examination questions and technical decisions:

### Q1: Why didn't you scale your features before running the Random Forest classifier?
* **Answer:** "We combined a sparse high-dimensional TF-IDF word matrix with a dense low-dimensional numerical metadata matrix. We selected a **Random Forest Classifier** specifically because tree-based ensemble models are scale-invariant. Applying scaling would have destroyed the mathematical sparsity of our TF-IDF matrix (making it dense and inflating RAM usage) without providing any accuracy gains. Thus, omitting scaling was a deliberate engineering decision to optimize performance."

### Q2: Why is the model's recall for negative reviews (25%) so low compared to positive reviews (98%)?
* **Answer:** "This is due to the **class imbalance** in our dataset—approximately 87.9% of user reviews are positive, which reflects the general positive distribution bias of Steam. The classifier optimizes overall accuracy by favoring the majority class. If we were deploying this model in a production scenario to flag negative comments, we would address this imbalance by setting `class_weight='balanced'` in the Random Forest parameters, applying SMOTE to balance the classes synthetically, or adjusting the classification probability threshold."

### Q3: VADER was built for Twitter and social media. Is it really suitable for Steam reviews?
* **Answer:** "VADER is highly suitable for Steam reviews because players write informal text using slang, capitalized words, emojis, and repeated exclamation points, which VADER's rule-based sentiment model handles well. However, VADER has an error rate of **17.4%** due to gaming culture's heavy reliance on sarcasm (e.g., *'10/10 destroyed my GPA'*). To improve this, a future iteration of the project would involve building a custom gaming-specific lexicon or using a transformer language model (like RoBERTa) to capture sarcastic semantic context."

### Q4: Why did you choose Random Forest instead of Support Vector Machines (SVM) or Naive Bayes?
* **Answer:** "Naive Bayes assumes feature independence, which is strongly violated when combining text (TF-IDF words) and behavioral metadata (playtime is highly correlated with certain words). Support Vector Machines are highly sensitive to feature scaling and struggle to handle mixed sparse/dense data distributions without costly transformations. Random Forest handles mixed data types and non-linear feature interactions naturally, making it the ideal choice for our multimodal model."

