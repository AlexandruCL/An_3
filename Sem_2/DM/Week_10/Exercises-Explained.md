# DM9 2025 — Laboratory Exercises Explained

This document provides a detailed walkthrough of the four exercises in the **DM9_2025.ipynb** notebook.  
All exercises assume the full lab notebook has already been executed so that prerequisite variables (`x`, `kmeans`, `vectorizer`, `df`, etc.) are available in memory.

---

## Exercise 1 — Confusion Matrix (Conceptual)

### Goal

Provide a clear, conceptual explanation of what a **confusion matrix** is and the metrics that can be derived from it.

### Background

A confusion matrix is a table used to evaluate the performance of a classification model.  
It compares the **actual** (true) labels of a dataset against the labels **predicted** by the model.

For a binary classification problem, the matrix has the following structure:

|                      | Predicted Positive | Predicted Negative |
|----------------------|--------------------|--------------------|
| **Actual Positive**  | TP (True Positive) | FN (False Negative)|
| **Actual Negative**  | FP (False Positive)| TN (True Negative) |

### Key Terms

| Term | Definition |
|------|-----------|
| **True Positive (TP)** | The model correctly predicted the positive class. |
| **True Negative (TN)** | The model correctly predicted the negative class. |
| **False Positive (FP)** | The model incorrectly predicted positive when the actual class was negative (Type I error). |
| **False Negative (FN)** | The model incorrectly predicted negative when the actual class was positive (Type II error). |

### Derived Metrics

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| **Accuracy** | `(TP + TN) / (TP + TN + FP + FN)` | Overall proportion of correct predictions. |
| **Precision** | `TP / (TP + FP)` | Of all predicted positives, how many are truly positive? |
| **Recall (Sensitivity)** | `TP / (TP + FN)` | Of all actual positives, how many were correctly identified? |
| **F1 Score** | `2 × (Precision × Recall) / (Precision + Recall)` | Harmonic mean of precision and recall — balances both. |
| **Specificity** | `TN / (TN + FP)` | Of all actual negatives, how many were correctly identified? |

### Why It Matters

- **Accuracy alone can be misleading**, especially on imbalanced datasets. A model predicting "negative" for everything on a 95 %/5 % dataset would have 95 % accuracy but 0 % recall.  
- The confusion matrix reveals *where* the model fails — whether it produces too many false positives or too many false negatives — which is critical for applications like medical diagnosis or fraud detection.

### Libraries Used

- `sklearn.metrics.confusion_matrix` — computes the matrix.  
- `sklearn.metrics.ConfusionMatrixDisplay` — renders a visual plot.  
- `sklearn.metrics.classification_report` — prints precision, recall, F1, and support per class.

---

## Exercise 2 — UCI Dataset ML Pipeline

### Goal

The exercise has **5 explicit requirements**:

1. **Find and import** a dataset from the [UCI Machine Learning Repository](https://archive.ics.uci.edu/) — either for classification or regression.
2. **Create 3 relevant visualizations** for the data (Exploratory Data Analysis).
3. **Split** the dataset into train (80 %) and test (20 %), unless the dataset is already pre-split.
4. **Train 3 different ML models** of your choice on the training data (use the correct model type for the task).
5. **Evaluate all 3 models** on the test data.

### Recommended Dataset

The **Wine** dataset (`sklearn.datasets.load_wine`) is used in the reference solution. It contains 178 samples with 13 chemical features, classified into 3 wine cultivar classes (`class_0`, `class_1`, `class_2`).

### Step 1 — Load the dataset

```python
from sklearn.datasets import load_wine
import pandas as pd

wine = load_wine()
X = pd.DataFrame(wine.data, columns=wine.feature_names)
y = wine.target
```

### Step 2 — Exploratory Data Analysis (3 Visualizations)

#### Visualization 1: Correlation heatmap

Shows pairwise feature correlations — helps identify redundant or strongly related features.

```python
import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(14, 10))
plt.title("Wine Dataset — Feature Correlation Heatmap", fontsize=16)
sns.heatmap(X.corr(), annot=True, fmt=".2f", cmap="coolwarm", linewidths=0.5)
plt.tight_layout()
plt.show()
```

#### Visualization 2: Class distribution bar chart

Shows how balanced/imbalanced the target classes are.

```python
plt.figure(figsize=(8, 5))
pd.Series(y).value_counts().sort_index().plot(kind='bar', color=['#1f77b4', '#ff7f0e', '#2ca02c'])
plt.title("Class Distribution", fontsize=14)
plt.xlabel("Wine Class")
plt.ylabel("Count")
plt.xticks(ticks=[0, 1, 2], labels=wine.target_names, rotation=0)
plt.show()
```

#### Visualization 3: Pairplot of selected features

Scatter plots of key features coloured by class — reveals how separable the classes are in feature space.

```python
plot_df = X[['alcohol', 'flavanoids', 'color_intensity', 'proline']].copy()
plot_df['target'] = y

sns.pairplot(plot_df, hue='target', palette='viridis', diag_kind='kde')
plt.suptitle("Pairplot of Selected Features", y=1.02, fontsize=14)
plt.show()
```

### Step 3 — Train/Test Split (80 % / 20 %)

```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Scale features (important for KNN and SVM)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)
```

- `test_size=0.2` — 80 %/20 % split as required by the exercise.
- `stratify=y` — preserves class proportions in both splits.
- `fit_transform` on train, `transform` on test — avoids data leakage.

### Step 4 — Train 3 Different ML Models

#### Model 1: K-Nearest Neighbors (KNN)

```python
from sklearn.neighbors import KNeighborsClassifier

knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train_scaled, y_train)
y_pred_knn = knn.predict(X_test_scaled)
```

#### Model 2: Random Forest

```python
from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train_scaled, y_train)
y_pred_rf = rf.predict(X_test_scaled)
```

#### Model 3: Support Vector Machine (SVM)

```python
from sklearn.svm import SVC

svm = SVC(kernel='rbf', random_state=42)
svm.fit(X_train_scaled, y_train)
y_pred_svm = svm.predict(X_test_scaled)
```

### Step 5 — Evaluate All 3 Models

```python
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay

models = {
    "KNN": y_pred_knn,
    "Random Forest": y_pred_rf,
    "SVM": y_pred_svm
}

for name, y_pred in models.items():
    print(f"\n{'='*50}")
    print(f"  {name} — Classification Report")
    print(f"{'='*50}")
    print(classification_report(y_test, y_pred, target_names=wine.target_names))

    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=wine.target_names)
    disp.plot(cmap='viridis')
    plt.title(f"{name} — Confusion Matrix")
    plt.show()
```

### Key Observations

- All three models on scaled Wine data typically achieve > 90 % accuracy; KNN and SVM often reach ≥ 97 %.
- The **confusion matrices** show per-class errors — which cultivar gets misclassified and as what.
- The **correlation heatmap** reveals that some features (e.g. `flavanoids` and `total_phenols`) are highly correlated, suggesting potential for dimensionality reduction.
- The **pairplot** visually confirms that `class_0` is often linearly separable from the other two, while `class_1` and `class_2` overlap more.

### Libraries Used

| Library | Purpose |
|---------|---------|
| `sklearn.datasets` | Load the Wine dataset |
| `sklearn.model_selection` | Train/test split |
| `sklearn.preprocessing` | Feature scaling (StandardScaler) |
| `sklearn.neighbors` | K-Nearest Neighbors classifier |
| `sklearn.ensemble` | Random Forest classifier |
| `sklearn.svm` | Support Vector Machine classifier |
| `sklearn.metrics` | Classification report & confusion matrix |
| `pandas` | DataFrame for EDA |
| `matplotlib.pyplot` | Plotting |
| `seaborn` | Heatmap, pairplot |

---

## Exercise 3 — Iris K-Means Cluster Visualization

### Goal

Using the Iris dataset and the K-Means model already fitted in the lab:

1. Create a 2D scatter plot of **petal length vs petal width**, coloured by cluster label.  
2. Create a 2D scatter plot of **petal width vs sepal width**, coloured by cluster label.  
3. Determine which plot shows better cluster separation.

### Prerequisites (from the lab)

The notebook defines:
- `x` — the Iris feature matrix (NumPy array, shape `(150, 4)`).  
  - Column 0: sepal length  
  - Column 1: sepal width  
  - Column 2: petal length  
  - Column 3: petal width  
- `kmeans` — a fitted `KMeans` object with `kmeans.labels_` available.

### Code Walkthrough

```python
import matplotlib.pyplot as plt

# --- Plot 1: Petal Length vs Petal Width ---
plt.figure(figsize=(12, 7))
plt.title("K-Means Clusters: Petal Length vs Petal Width")
plt.xlabel("Petal Length (cm)")
plt.ylabel("Petal Width (cm)")
plt.scatter(x[:, 2], x[:, 3], c=kmeans.labels_, cmap='viridis', s=50)
plt.colorbar(label='Cluster')
plt.show()
```

- `x[:, 2]` selects petal length (column index 2).  
- `x[:, 3]` selects petal width (column index 3).  
- `c=kmeans.labels_` colours each point by its cluster assignment.

```python
# --- Plot 2: Petal Width vs Sepal Width ---
plt.figure(figsize=(12, 7))
plt.title("K-Means Clusters: Petal Width vs Sepal Width")
plt.xlabel("Petal Width (cm)")
plt.ylabel("Sepal Width (cm)")
plt.scatter(x[:, 3], x[:, 1], c=kmeans.labels_, cmap='viridis', s=50)
plt.colorbar(label='Cluster')
plt.show()
```

- `x[:, 1]` selects sepal width (column index 1).

### Answer

The **petal length vs petal width** plot shows clearly better cluster separation.  
This is because petal dimensions are far more discriminative for the three Iris species than sepal dimensions — Iris setosa in particular has noticeably smaller petals, making it trivially separable, while the other two species also differ more in petal measurements than in sepal measurements.

### Libraries Used

- `matplotlib.pyplot` — scatter plots.  
- `sklearn.cluster.KMeans` — already fitted in the lab.

---

## Exercise 4 — Text K-Means + PCA Visualization (New Categories)

### Goal

Choose **at least 3 different categories** from `fetch_20newsgroups` (or another text corpus) and repeat the full text clustering pipeline demonstrated in the lab:

1. Fetch and clean the text data.  
2. Vectorize with TF-IDF.  
3. Cluster with K-Means.  
4. Reduce to 2D with PCA.  
5. Visualize.

### Categories Chosen

The reference solution uses:

| Category | Topic |
|----------|-------|
| `sci.space` | Space & astronomy |
| `rec.autos` | Automobiles |
| `talk.politics.guns` | Gun politics |

These are deliberately diverse topics to maximise cluster separability.

### Pipeline Steps

#### 1. Fetch the data

```python
from sklearn.datasets import fetch_20newsgroups

categories_ex4 = ['sci.space', 'rec.autos', 'talk.politics.guns']
dataset_ex4 = fetch_20newsgroups(
    subset='all', categories=categories_ex4,
    shuffle=True, random_state=42
)
```

#### 2. Text preprocessing

A cleaning function strips numbers, punctuation, and English stopwords, then lowercases:

```python
import re, string, nltk
from nltk.corpus import stopwords

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'\d+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = text.strip()
    tokens = text.split()
    stop_words = set(stopwords.words('english'))
    tokens = [w for w in tokens if w not in stop_words]
    return ' '.join(tokens)

corpus_ex4 = [preprocess_text(doc) for doc in dataset_ex4.data]
```

#### 3. TF-IDF vectorization

```python
from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer_ex4 = TfidfVectorizer(sublinear_tf=True, min_df=5, max_df=0.95)
X_ex4 = vectorizer_ex4.fit_transform(df_ex4['cleaned'])
```

- `sublinear_tf=True` applies `1 + log(tf)` scaling — dampens the effect of very high term frequencies.  
- `min_df=5` ignores terms appearing in fewer than 5 documents.  
- `max_df=0.95` ignores terms appearing in more than 95 % of documents.

#### 4. K-Means clustering

```python
from sklearn.cluster import KMeans

kmeans_ex4 = KMeans(n_clusters=3, random_state=42, n_init=10)
clusters_ex4 = kmeans_ex4.fit_predict(X_ex4)
```

- `n_clusters=3` matches the number of chosen categories.  
- `fit_predict` fits the model and returns cluster labels in one step.

#### 5. Top keywords per cluster

```python
def get_top_keywords_ex4(n_terms):
    df_grouped = pd.DataFrame(X_ex4.todense()).groupby(clusters_ex4).mean()
    terms = vectorizer_ex4.get_feature_names_out()
    for i, r in df_grouped.iterrows():
        print(f'\nCluster {i}')
        print(','.join([terms[t] for t in np.argsort(r)[-n_terms:]]))

get_top_keywords_ex4(10)
```

This groups the TF-IDF matrix by cluster label, computes the mean TF-IDF score per term, and prints the top-n highest-scoring terms per cluster. The keywords should clearly reflect the three chosen topics.

#### 6. PCA dimensionality reduction

```python
from sklearn.decomposition import PCA

pca_ex4 = PCA(n_components=2, random_state=42)
pca_vecs_ex4 = pca_ex4.fit_transform(X_ex4.toarray())
```

- PCA projects the high-dimensional TF-IDF vectors down to 2 dimensions for scatter plot visualisation.  
- `.toarray()` converts the sparse TF-IDF matrix to dense, which PCA requires.

#### 7. Scatter plot

```python
import seaborn as sns

df_ex4['x0'] = pca_vecs_ex4[:, 0]
df_ex4['x1'] = pca_vecs_ex4[:, 1]

cluster_map_ex4 = {i: categories_ex4[i].split('.')[-1] for i in range(len(categories_ex4))}
df_ex4['cluster'] = df_ex4['cluster'].map(cluster_map_ex4)

plt.figure(figsize=(12, 7))
plt.title("TF-IDF + KMeans Clustering (sci.space, rec.autos, talk.politics.guns)")
plt.xlabel("X0")
plt.ylabel("X1")
sns.scatterplot(data=df_ex4, x='x0', y='x1', hue='cluster', palette='viridis')
plt.show()
```

### Expected Outcome

The scatter plot should show **three distinct clusters** corresponding to the three newsgroup categories. Some overlap is normal due to shared vocabulary between topics, but the clusters should be visually identifiable.

### Libraries Used

| Library | Purpose |
|---------|---------|
| `sklearn.datasets.fetch_20newsgroups` | Fetch text corpus |
| `sklearn.feature_extraction.text.TfidfVectorizer` | TF-IDF vectorization |
| `sklearn.cluster.KMeans` | Unsupervised clustering |
| `sklearn.decomposition.PCA` | Dimensionality reduction to 2D |
| `pandas` | DataFrame manipulation |
| `numpy` | Array operations |
| `nltk` | Stopwords for text cleaning |
| `re`, `string` | Text preprocessing |
| `matplotlib.pyplot`, `seaborn` | Visualization |

---

## Summary

| Exercise | Type | Key Technique | Output |
|----------|------|---------------|--------|
| 1 | Conceptual | Confusion matrix theory | Written explanation |
| 2 | Supervised | KNN on Wine dataset | Classification report + confusion matrix plot |
| 3 | Unsupervised | K-Means on Iris | Two 2D scatter plots, comparison answer |
| 4 | Unsupervised + NLP | TF-IDF → K-Means → PCA on 20newsgroups | Cluster keywords + 2D scatter plot |
