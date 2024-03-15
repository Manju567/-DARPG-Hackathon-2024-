import nltk
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import docx2txt

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'f7LoVX2E5miXCmITBXZwlh_O8jzzQz9U'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testDB.db'
db = SQLAlchemy(app)

# Define database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    report_text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='Pending')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Initialize NLTK resources
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Provided departments
departments = ["infra",
    "healthcare",
    "education",
    "env",
    "publicsaf"
]

# Function to preprocess text
def preprocess_text(text):
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    tokens = nltk.word_tokenize(text)
    tokens = [word.lower() for word in tokens if word.isalnum() and word.lower() not in stop_words]
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return ' '.join(tokens)

# Load training data for each department
department_training_data = {}

for department in departments:
    text = docx2txt.process(f"{department}.docx")
    department_training_data[department] = preprocess_text(text)

# Train the classifier
tfidf_vectorizer = TfidfVectorizer(max_features=1000)
tfidf_matrix = tfidf_vectorizer.fit_transform(list(department_training_data.values()))
labels = list(department_training_data.keys())
classifier = RandomForestClassifier(n_estimators=100, random_state=42)
classifier.fit(tfidf_matrix, labels)

# Define officials dictionary
officials = {
    'infra': 'pulakuntasomeshkumar8@gmail.com',
    'healthcare': '9921004531@klu.ac.in',
    'education': '99210041966@klu.ac.in',
    'env': '99210041843@klu.ac.in',
    'publicsaf': '9921004588@klu.ac.in'
}

# Define sender email
sender_email = "chandu.prudhivi04@gmail.com"  # Update with your email
sender_password = 'fegr blqz escn anzj'  # Update with your email password

# Define routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        report_text = request.form['report']
        user_id = session['user_id']
        category = predict_category(report_text)
        new_report = Report(user_id=user_id, report_text=report_text, category=category)
        db.session.add(new_report)
        db.session.commit()
        send_email(category, report_text)
        return redirect(url_for('dashboard'))

    user_id = session['user_id']
    user_reports = Report.query.filter_by(user_id=user_id).all()
    return render_template('dashboard.html', user_reports=user_reports)

# Function to predict category
def predict_category(report_text):
    preprocessed_text = preprocess_text(report_text)
    tfidf_matrix = tfidf_vectorizer.transform([preprocessed_text])
    category = classifier.predict(tfidf_matrix)
    return category[0]

# Function to send email
def send_email(category, report_text):
    receiver_email = officials.get(category, None)
    if receiver_email:
        subject = f"Grievance Report - {category}"
        body = f"Dear Official,\n\nYou have received a new grievance report:\n\n{report_text}\n\nSincerely,\nThe Grievance System"

        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())

if __name__ == '__main__':
    app.run(debug=True)
