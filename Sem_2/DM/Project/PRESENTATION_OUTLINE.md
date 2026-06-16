# Steam Game Reviews — Presentation Outline & Script (7 Minutes Max)

This presentation is designed for a team of two. The slides and speaking parts are split equally so that both presenters receive credit for technical rigor, analytical insights, and presentation clarity.

---

## Slide 1: Introduction & Project Overview (0:00 - 0:45)
*Visuals: Sleek title slide featuring logos of major Steam games (Witcher 3, CS2, Cyberpunk) with a subtitle: "Decoding Gamer Sentiment."*

* **Speaker:** **Presenter A (0:00 - 0:25)**
  > "Hello everyone. Today, my colleague [Teammate Name] and I are excited to share our analysis of player reviews on Steam. Our goal was to uncover non-obvious patterns in how gamers express their satisfaction and to see if we could build a machine learning model to predict their recommendations based on text and play patterns."
* **Speaker:** **Presenter B (0:25 - 0:45)**
  > "We selected 10 major games across various genres, including Counter-Strike 2, Dota 2, and Stardew Valley. By applying a combination of scraping, natural language processing, and supervised classification, we analyzed how gamer feedback differs from traditional product reviews. Let's start with how we gathered the data."

---

## Slide 2: Data Acquisition & Web Scraping (0:45 - 1:45)
*Visuals: A simple flowchart displaying the two-pronged scraping approach: (1) Steam Reviews API -> 2,000 reviews, (2) Steam Store HTML -> BeautifulSoup tag extraction.*

* **Speaker:** **Presenter A (0:45 - 1:45)**
  > "To gather our dataset, we used a two-pronged web scraping approach. 
  > First, we leveraged the Steam Reviews API, pulling 200 English reviews per game, resulting in 2,000 reviews. This API gave us valuable metrics like playtime, review text, recommendation status, and community helpfulness votes.
  > Second, to contextualize these reviews, we scraped the Steam store pages using BeautifulSoup. We successfully bypassed access controls and extracted user-defined tags like 'Souls-like' or 'Farming Sim' and matched them with the reviews.
  > This gave us a rich, multi-dimensional dataset containing both text and player activity metrics."

---

## Slide 3: Preprocessing & Data Cleaning (1:45 - 2:45)
*Visuals: A before/after code-free visual representation of a raw review text transitioning to clean tokens. Highlight columns engineered: playtime_hours, review_length, recommendation.*

* **Speaker:** **Presenter B (1:45 - 2:45)**
  > "Raw Steam reviews are notorious for containing URLs, forum formatting, and non-alphabetic spam. 
  > To clean this, we implemented a custom cleaning pipeline: we removed URLs, square bracket tags, and special characters, and lowercased the text. We then removed reviews that had fewer than 10 characters after cleaning to eliminate noise like '10/10' or single-word spam.
  > Furthermore, we engineered new features: we converted playtime from minutes to hours, calculated review lengths, and mapped recommendation boolean values to categorical labels. This left us with 1,986 high-quality, preprocessed reviews ready for modeling."

---

## Slide 4: EDA: The "Frustrated Veteran" Insight (2:45 - 3:45)
*Visuals: (1) Bar chart showing positive vs negative reviews per game. (2) A boxplot comparing playtime distributions for positive vs negative recommendations.*

* **Speaker:** **Presenter A (2:45 - 3:45)**
  > "During our Exploratory Data Analysis, we uncovered a fascinating, non-obvious pattern. While 87.9% of all reviews were positive, the playtime distribution told a different story.
  > If we look at this boxplot, the median playtime for players leaving positive reviews was 84.7 hours. However, the median playtime for players leaving *negative* reviews was 391.1 hours!
  > This is what we call the 'Frustrated Veteran' phenomenon. Unlike normal products where you write a bad review after 5 minutes of use, gamers often play a game for hundreds of hours before leaving a negative review. This typically happens when long-term updates disappoint the community or multiplayer systems become toxic, making these reviews highly critical and valuable to developers."

---

## Slide 5: Sentiment Analysis & Gamer Sarcasm (3:45 - 4:45)
*Visuals: Boxplot of VADER compound score vs. actual recommendation, highlighting the 82.6% agreement rate and examples of sarcastic reviews.*

* **Speaker:** **Presenter B (3:45 - 4:45)**
  > "Next, we applied VADER sentiment analysis to calculate compound sentiment scores for each review. 
  > VADER's compound scores aligned with the actual player recommendations 82.6% of the time, which is quite high. But why the 17.4% disagreement?
  > When we investigated the mismatches, we found that gaming culture relies heavily on irony and sarcasm. For example, a positive review stating 'This game ruined my life and destroyed my social circle, 10/10' is classified by VADER as highly negative due to words like 'ruined' and 'destroyed', even though the player recommended it. This shows that standard lexicons struggle to capture the community-specific nuance of gaming jargon."

---

## Slide 6: TF-IDF & N-grams (4:45 - 5:45)
*Visuals: Side-by-side horizontal bar charts showing top 15 TF-IDF terms and top Bigrams/Trigrams for positive vs negative reviews.*

* **Speaker:** **Presenter A (4:45 - 5:45)**
  > "To understand the vocabulary differences, we computed TF-IDF scores and N-grams for positive and negative reviews.
  > Positive reviews heavily feature words like 'great', 'fun', 'love', and 'beautiful', focusing on emotional attachment. Their bigrams and trigrams emphasize the gameplay loop, such as 'worth every penny' and 'best game ever'.
  > Negative reviews, on the other hand, show strong clusters of technical terms like 'bug', 'crash', 'fps', and 'issue'. Their bigrams highlight frustrations like 'waste of money' or 'can't recommend'.
  > Interestingly, we also ran TF-IDF on individual games and successfully extracted game-specific concepts, such as 'cheaters' for Counter-Strike 2, 'toxic' for Dota 2, and 'story' for Witcher 3."

---

## Slide 7: Predictive Modeling & Hyperparameter Tuning (5:45 - 6:45)
*Visuals: Random Forest confusion matrix (89.45% accuracy) and a feature importance bar chart showing the dominant features. Include a small callout for GridSearchCV.*

* **Speaker:** **Presenter B (5:45 - 6:45)**
  > "Finally, we combined our text and metadata features to train a Random Forest Classifier to predict whether a review was positive or negative. We merged TF-IDF features with numeric variables like playtime, review length, and VADER sentiment scores.
  > On an 80/20 train-test split, our baseline model achieved an accuracy of 89.70%. To ensure optimal generalization and avoid overfitting, we performed hyperparameter tuning using GridSearchCV across tree depths and counts. The tuned model stabilized at 89.45% accuracy, giving us highly reliable predictive performance.
  > Looking at the feature importance chart, the VADER compound sentiment score was by far the strongest predictor, followed by playtime hours and review length. This proves that despite gamer sarcasm, the underlying emotional intensity remains the single best indicator of whether a player will recommend a title."

---

## Slide 8: Conclusions & Wrap-up (6:45 - 7:00)
*Visuals: Final slide summarizing achievements and thanking the jury.*

* **Speaker:** **Presenter A (6:45 - 6:52)**
  > "In conclusion, our data mining workflow successfully extracted and analyzed a rich Steam dataset, revealing how gamer behavior deviates from traditional consumers."
* **Speaker:** **Presenter B (6:52 - 7:00)**
  > "Thank you for your time, and we are now open to any questions you may have."
