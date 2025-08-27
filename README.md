---
# SmartTextEval 🎓📝  
An Intelligent Writing Evaluation Interface

SmartTextEval is a Django-based web platform that provides **automated writing evaluation** for students. It combines **real-time grammar and spelling correction** with **behavioral analysis** through typing activity tracking. It includes **separate dashboards for students and teachers**, and supports **exercise creation**, **session tracking**, and **pedagogical feedback**.

---

## 🎯 Objectives

- Enable real-time **spelling and grammar correction** (in French)
- Track **typing behavior** (keylogging for pedagogical purposes)
- Provide **role-based dashboards** for students and teachers
- Offer **feedback and scores** based on writing quality
- Allow **teachers to create custom exercises** and follow student progression

---

## 🎬 Demo Video

<video src="demo_final.mp4" controls width="700"></video>

> If the video doesn’t play on GitHub, upload it to [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases) or a platform like [Streamable](https://streamable.com) and replace the source link.

---

## 🛠️ Tech Stack

- **Backend**: Django (Python)
- **Frontend**: HTML5, CSS3, Bootstrap, JavaScript (AJAX)
- **Text Correction**:
  - [spaCy](https://spacy.io/) for NLP processing
  - [LanguageTool](https://languagetool.org/) for grammar/style checks
  - [pyspellchecker](https://pyspellchecker.readthedocs.io/) for spelling
- **Database**: SQLite (development phase)
- **Authentication**: Django CustomUser with role management

---

## ✨ Key Features

### 🔍 Linguistic Correction
- Automatic detection of spelling, grammar, and conjugation errors
- Text quality scoring system
- Real-time educational feedback and suggestions

### 🎯 Typing Event Tracking
- Real-time recording of keystrokes and cursor position
- Session ID and timestamp capture
- Full reconstruction of the student’s writing process

### 👩‍🏫 Teacher Interface
- Secure login and access control
- Simple exercise creation
- Viewing and evaluation of student submissions

### 👨‍🎓 Student Dashboard
- Rich text editor with auto-correction
- Access to custom exercises
- Saving and reviewing written texts

---

## 📦 Project Architecture

```

SmartTextEval/
├── manage.py
├── db.sqlite3
├── myproject/                # Main Django project settings
│   ├── settings.py
│   └── urls.py
├── templates/                # Global templates
│   └── base.html
├── accounts/                 # Authentication and roles
│   ├── apps.py
│   ├── urls.py
│   ├── views.py
│   └── templates/
│       ├── registration/
│       │   ├── login.html
│       │   ├── signup_choice.html
│       │   ├── student_signup.html
│       │   └── professor_signup.html
│       └── accounts/
│           ├── professor_dashboard.html
│           └── student_dashboard.html
├── text_analysis/           # NLP logic and correction engine
│   └── templates/
│       └── text_analysis/
│           ├── add_exercise.html
│           └── home.html

````

---

## 🚀 Getting Started

### 🔗 Requirements

Install dependencies:

```bash
pip install -r requirements.txt
python -m spacy download fr_core_news_sm
````

### ▶️ Run the app

```bash
python manage.py runserver
```

Open in your browser: [http://127.0.0.1:8000](http://127.0.0.1:8000)


### ▶️ Run again analysis

python manage.py reanalyze_empty

---


## 🧠 Writing Behavior Analysis & JSON Export

You can view the full history of typing events and saved texts from students at:

👉 [http://127.0.0.1:8000/text-analysis/events/](http://127.0.0.1:8000/text-analysis/events/)

This page allows you to:
- 🔁 **Replay the writing process**, including cursor movements and keystrokes
- 📦 **Download the full dataset in JSON format** for further analysis or research
---

## 🔒 Security Notes

* `DEBUG = True` is enabled (disable in production)
* CSRF protection temporarily deactivated for development testing
* Authentication based on Django's role-aware CustomUser model

---

## 🧠 Future Improvements

* Advanced behavioral analytics (e.g. writing pauses, backspaces)
* Dynamic session tracking tied to users
* Visual dashboards for teachers (progress charts)
* Export student reports (CSV, PDF)
* Integrated XML editor for teacher exercises
* Deployment hardening (HTTPS, strict role permissions)

---

## 📚 Authors

* **Imane Hibaoui**
* **Mohamed Najem**
* **Hoang Nguyen Vu**

**Supervisors**: François Bouchet - Léo Nebel
---

Université Sorbonne — M1 Informatique 2024–2025

---

## 🔗 References

* [spaCy](https://spacy.io/)
* [LanguageTool](https://languagetool.org/)
* [PySpellChecker](https://pyspellchecker.readthedocs.io/)
* [Django Docs](https://docs.djangoproject.com/en/5.2/)

```
