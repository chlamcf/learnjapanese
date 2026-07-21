# Japanese Vocabulary & Kanji Quiz App

天気がいいから、散歩しましょう！
(The weather is nice, let's take a walk!)

A full-stack Flask web app for practicing Japanese vocabulary and kanji using
flashcard-style quizzes with spaced repetition (SM-2).

## Features
- CRUD management of vocabulary/kanji (word, reading, meaning, category)
- Multiple-choice quiz mode with session score tracking
- Quiz history stored per attempt (word_id, correct/incorrect, timestamp)
- Simplified SM-2 spaced repetition: due words are prioritized in quizzes
- Progress chart showing correct/incorrect answers over time

## Tech Stack
- Backend: Python 3 + Flask
- Database: SQLite
- Frontend: HTML + Jinja2 templates + CSS, Chart.js for graphs
- Deployment: Render

## Local Setup
1. Clone the repo and `cd` into it
2. `python -m venv venv && source venv/bin/activate`
3. `pip install -r requirements.txt`
4. `python seed_db.py` (creates database.db and seeds starter words)
5. `python app.py` and visit http://127.0.0.1:5000

- Hint: To have a taste of the quiz without going through too many questions, choose level "N1". The word list for N1 is intentionally kept short for this purpose.

## Screenshots
(To be updated)

## Project Structure
- app.py — routes and CRUD/quiz logic
- sm2.py — spaced repetition algorithm
- schema.sql / seed_db.py — database setup
- templates/ — Jinja2 HTML pages
- static/style.css — styling