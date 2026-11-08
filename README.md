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

### Prerequisites

- Python 3 installed and available in your terminal.
- Git installed, or download and extract the repository ZIP from GitHub.

Check your Python installation:

Windows PowerShell:

```powershell
python --version
```

macOS / Linux:

```bash
python3 --version
```

If Python is not recognized, install it from [python.org](https://www.python.org/downloads/). On Windows, enable “Add python.exe to PATH” if the installer offers that option, then close and reopen your terminal.

### 1. Clone the repository

```bash
git clone [https://github.com/chlamcf/learnjapanese.git](https://github.com/chlamcf/learnjapanese.git)
cd learnjapanese
```

If you downloaded the ZIP instead, extract it and open a terminal in the project folder containing `app.py` and `requirements.txt`.

### 2. Create a virtual environment and install dependencies

#### Windows PowerShell

Run these commands one at a time:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Note:** These commands use `python` rather than `py`, so the Python launcher is not required. They also use the virtual environment’s Python directly, so activation and PowerShell execution-policy changes are unnecessary.

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3. Initialize the database

From the project’s root directory, run the seed script to create `database.db` and seed the starter words.

#### Windows PowerShell

```powershell
.\.venv\Scripts\python.exe seed_db.py
```

#### macOS / Linux

```bash
python seed_db.py
```

### 4. Start the application

#### Windows PowerShell

```powershell
.\.venv\Scripts\python.exe app.py
```

#### macOS / Linux

```bash
python app.py
```

Open http://127.0.0.1:5000/ in your browser. Keep the terminal running while using the application. Press `Ctrl+C` to stop the server.

### Troubleshooting

- `python` is not recognized on Windows: Install Python, ensure it is added to `PATH`, and reopen your terminal.
- `py` is not recognized: Use the `python` commands above; this setup does not require `py`.
- A setup command fails: Stop and resolve that error before running the next command.
- Restarting the app later: Open a terminal in the project folder and repeat Step 4. On macOS/Linux, first reactivate the environment with `source .venv/bin/activate`.

- Hint: To have a taste of the quiz without going through too many questions, choose level "N1". The word list for N1 is intentionally kept short for this purpose.

## Testing

- The spaced-repetition logic in sm2.py is covered by a unittest-based test suite in test_sm2.py, which tests both sm2_update and quality_from_correctness.
- To run the test: `python -m unittest test_sm2.py -v`

## Project Structure
- app.py — routes and CRUD/quiz logic
- sm2.py — spaced repetition algorithm
- schema.sql / seed_db.py — database setup
- templates/ — Jinja2 HTML pages
- static/style.css — styling
