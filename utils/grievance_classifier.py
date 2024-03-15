import nltk
import docx2txt
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

class GrievanceClassifier:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000)
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)

    def preprocess_text(self, text):
        tokens = nltk.word_tokenize(text.lower())
        tokens = [word for word in tokens if word.isalnum() and word not in self.stop_words]
        tokens = [self.lemmatizer.lemmatize(word) for word in tokens]
        return ' '.join(tokens)

    def train_classifier(self, reports, labels):
        preprocessed_reports = [self.preprocess_text(report) for report in reports]
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(preprocessed_reports)
        self.classifier.fit(tfidf_matrix, labels)

    def categorize_reports(self, reports):
        preprocessed_reports = [self.preprocess_text(report) for report in reports]
        tfidf_matrix = self.tfidf_vectorizer.transform(preprocessed_reports)
        categories = self.classifier.predict(tfidf_matrix)
        return categories
