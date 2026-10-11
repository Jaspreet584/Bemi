import sqlite3
import os

def get_connection(db_path="bmi_tracker.db"):
    """Establish a connection to the SQLite database and enable foreign keys."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path="bmi_tracker.db"):
    """Initialize the database tables if they do not exist."""
    conn = get_connection(db_path)
    try:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            age INTEGER NOT NULL,
            gender TEXT CHECK(gender IN ('Male', 'Female', 'Other')) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        conn.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            weight REAL NOT NULL, -- in kilograms
            height REAL NOT NULL, -- in meters
            bmi REAL NOT NULL,
            notes TEXT,
            recorded_at DATE DEFAULT (date('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)
        conn.commit()
    finally:
        conn.close()

def create_user(name, age, gender, db_path="bmi_tracker.db"):
    """Create a new user profile. Returns user ID or raises ValueError."""
    name = name.strip()
    if not name:
        raise ValueError("Name cannot be empty.")
    if age <= 0 or age > 120:
        raise ValueError("Please enter a valid age (1-120).")
    if gender not in ('Male', 'Female', 'Other'):
        raise ValueError("Invalid gender selection.")
        
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, age, gender) VALUES (?, ?, ?)",
            (name, age, gender)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError(f"User with name '{name}' already exists.")
    finally:
        conn.close()

def update_user(user_id, name, age, gender, db_path="bmi_tracker.db"):
    """Update user details."""
    name = name.strip()
    if not name:
        raise ValueError("Name cannot be empty.")
    if age <= 0 or age > 120:
        raise ValueError("Please enter a valid age (1-120).")
    if gender not in ('Male', 'Female', 'Other'):
        raise ValueError("Invalid gender selection.")

    conn = get_connection(db_path)
    try:
        conn.execute(
            "UPDATE users SET name = ?, age = ?, gender = ? WHERE id = ?",
            (name, age, gender, user_id)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise ValueError(f"User with name '{name}' already exists.")
    finally:
        conn.close()

def delete_user(user_id, db_path="bmi_tracker.db"):
    """Delete a user profile and all their measurements."""
    conn = get_connection(db_path)
    try:
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
    finally:
        conn.close()

def get_users(db_path="bmi_tracker.db"):
    """Get all user profiles."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY name COLLATE NOCASE")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_user(user_id, db_path="bmi_tracker.db"):
    """Get a single user profile."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def add_measurement(user_id, weight, height, bmi, notes="", recorded_at=None, db_path="bmi_tracker.db"):
    """Log a BMI measurement."""
    if weight <= 0 or height <= 0:
        raise ValueError("Weight and height must be positive values.")
    
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        if recorded_at:
            cursor.execute(
                "INSERT INTO measurements (user_id, weight, height, bmi, notes, recorded_at) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, weight, height, bmi, notes, recorded_at)
            )
        else:
            cursor.execute(
                "INSERT INTO measurements (user_id, weight, height, bmi, notes) VALUES (?, ?, ?, ?, ?)",
                (user_id, weight, height, bmi, notes)
            )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def get_measurements(user_id, db_path="bmi_tracker.db"):
    """Retrieve all measurements for a user sorted by date and ID ascending."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM measurements WHERE user_id = ? ORDER BY recorded_at ASC, id ASC",
            (user_id,)
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def delete_measurement(measurement_id, db_path="bmi_tracker.db"):
    """Delete a specific measurement record."""
    conn = get_connection(db_path)
    try:
        conn.execute("DELETE FROM measurements WHERE id = ?", (measurement_id,))
        conn.commit()
    finally:
        conn.close()

def get_user_stats(user_id, db_path="bmi_tracker.db"):
    """Calculate and retrieve statistics for a user."""
    measurements = get_measurements(user_id, db_path)
    if not measurements:
        return None
        
    bmis = [m['bmi'] for m in measurements]
    weights = [m['weight'] for m in measurements]
    
    avg_bmi = sum(bmis) / len(bmis)
    min_bmi = min(bmis)
    max_bmi = max(bmis)
    
    # Calculate changes (latest - earliest)
    weight_change = weights[-1] - weights[0]
    bmi_change = bmis[-1] - bmis[0]
    
    return {
        'count': len(measurements),
        'avg_bmi': round(avg_bmi, 2),
        'min_bmi': round(min_bmi, 2),
        'max_bmi': round(max_bmi, 2),
        'first_weight': round(weights[0], 2),
        'latest_weight': round(weights[-1], 2),
        'weight_change': round(weight_change, 2),
        'first_bmi': round(bmis[0], 2),
        'latest_bmi': round(bmis[-1], 2),
        'bmi_change': round(bmi_change, 2)
    }
