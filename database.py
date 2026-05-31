import sqlite3
import pandas as pd
from datetime import datetime

DB_FILE = "fittrack.db"

def init_db():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # User Profile Table
    c.execute('''CREATE TABLE IF NOT EXISTS user_profile (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    gender TEXT,
                    birth_date TEXT,
                    height REAL,
                    current_weight REAL,
                    target_weight REAL,
                    activity_level TEXT,
                    deepseek_api_key TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')

    # Weight Logs Table
    c.execute('''CREATE TABLE IF NOT EXISTS weight_logs (
                    id INTEGER PRIMARY KEY,
                    date TEXT,
                    weight REAL,
                    body_fat REAL,
                    muscle_rate REAL,
                    note TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')

    # Food Logs Table
    c.execute('''CREATE TABLE IF NOT EXISTS food_logs (
                    id INTEGER PRIMARY KEY,
                    date TEXT,
                    time TEXT,
                    food_name TEXT,
                    calories REAL,
                    protein REAL,
                    carbs REAL,
                    fat REAL,
                    note TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')

    # Exercise Logs Table
    c.execute('''CREATE TABLE IF NOT EXISTS exercise_logs (
                    id INTEGER PRIMARY KEY,
                    date TEXT,
                    exercise_type TEXT,
                    duration_minutes INTEGER,
                    calories_burned REAL,
                    note TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')

    # Daily Metrics Table (Sleep, Water, Mood)
    c.execute('''CREATE TABLE IF NOT EXISTS daily_metrics (
                    id INTEGER PRIMARY KEY,
                    date TEXT UNIQUE,
                    sleep_hours REAL,
                    water_ml INTEGER,
                    mood_score INTEGER,
                    stress_level INTEGER,
                    note TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')

    conn.commit()
    conn.close()

# --- User Profile Operations ---
def get_user_profile():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT * FROM user_profile ORDER BY id DESC LIMIT 1", conn)
    conn.close()
    return df.iloc[0] if not df.empty else None

def save_user_profile(name, gender, birth_date, height, current_weight, target_weight, activity_level, deepseek_api_key):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO user_profile 
                 (id, name, gender, birth_date, height, current_weight, target_weight, activity_level, deepseek_api_key) 
                 VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?)''', 
              (name, gender, birth_date, height, current_weight, target_weight, activity_level, deepseek_api_key))
    conn.commit()
    conn.close()

# --- Weight Operations ---
def add_weight_log(date, weight, body_fat=None, muscle_rate=None, note=""):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Check if entry exists for this date, if so update it, otherwise insert
    # Simplification: Allow multiple entries or just one per day? strict MVP says logs. Let's allowing inserting.
    c.execute("INSERT INTO weight_logs (date, weight, body_fat, muscle_rate, note) VALUES (?, ?, ?, ?, ?)",
              (date, weight, body_fat, muscle_rate, note))
    conn.commit()
    conn.close()

def get_weight_history(limit=30):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql(f"SELECT * FROM weight_logs ORDER BY date DESC LIMIT {limit}", conn)
    conn.close()
    return df

# --- Food Operations ---
def add_food_log(date, time, food_name, calories, protein, carbs, fat, note=""):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''INSERT INTO food_logs (date, time, food_name, calories, protein, carbs, fat, note) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (date, time, food_name, calories, protein, carbs, fat, note))
    conn.commit()
    conn.close()

def get_food_logs(date):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT * FROM food_logs WHERE date = ?", conn, params=(date,))
    conn.close()
    return df

# --- Exercise Operations ---
def add_exercise_log(date, exercise_type, duration, calories, note=""):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''INSERT INTO exercise_logs (date, exercise_type, duration_minutes, calories_burned, note) 
                 VALUES (?, ?, ?, ?, ?)''',
              (date, exercise_type, duration, calories, note))
    conn.commit()
    conn.close()

def get_exercise_logs(date):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT * FROM exercise_logs WHERE date = ?", conn, params=(date,))
    conn.close()
    return df

# --- Daily Metrics Operations ---
def update_daily_metrics(date, sleep=None, water=None, mood=None, stress=None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Try to get existing
    c.execute("SELECT * FROM daily_metrics WHERE date = ?", (date,))
    row = c.fetchone()
    
    if row:
        # Update existing fields only if new values provided
        if sleep is not None: c.execute("UPDATE daily_metrics SET sleep_hours = ? WHERE date = ?", (sleep, date))
        if water is not None: c.execute("UPDATE daily_metrics SET water_ml = ? WHERE date = ?", (water, date))
        if mood is not None: c.execute("UPDATE daily_metrics SET mood_score = ? WHERE date = ?", (mood, date))
        if stress is not None: c.execute("UPDATE daily_metrics SET stress_level = ? WHERE date = ?", (stress, date))
    else:
        # Insert new
        c.execute('''INSERT INTO daily_metrics (date, sleep_hours, water_ml, mood_score, stress_level) 
                     VALUES (?, ?, ?, ?, ?)''',
                  (date, sleep, water, mood, stress))
    
    conn.commit()
    conn.close()

def get_daily_metrics(date):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT * FROM daily_metrics WHERE date = ?", conn, params=(date,))
    conn.close()
    return df.iloc[0] if not df.empty else None
