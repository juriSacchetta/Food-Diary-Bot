"""
Database manager for food diary bot using SQLite
"""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class DatabaseManager:
    def __init__(self, db_path: str = "data/food_diary.db"):
        self.db_path = db_path
        Path("data").mkdir(exist_ok=True)
        self.init_db()
    
    def get_connection(self):
        """Create a database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        """Initialize database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create meals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                meal_type TEXT DEFAULT 'meal',
                ingredients TEXT,
                message TEXT NOT NULL,
                photo_path TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Migration: Add meal_type and ingredients columns if they don't exist
        cursor.execute("PRAGMA table_info(meals)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'meal_type' not in columns:
            cursor.execute("ALTER TABLE meals ADD COLUMN meal_type TEXT DEFAULT 'meal'")
        
        if 'ingredients' not in columns:
            cursor.execute("ALTER TABLE meals ADD COLUMN ingredients TEXT")
        
        conn.commit()
        conn.close()
    
    def add_meal(
        self, 
        user_id: int, 
        username: Optional[str], 
        message: str, 
        photo_path: Optional[str] = None,
        meal_type: str = 'meal',
        ingredients: Optional[str] = None
    ) -> int:
        """Add a new meal entry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO meals (user_id, username, meal_type, ingredients, message, photo_path)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, username, meal_type, ingredients, message, photo_path))
        
        meal_id = cursor.lastrowid if cursor.lastrowid else 0
        conn.commit()
        conn.close()
        
        return meal_id
    
    def get_all_meals(self, user_id: Optional[int] = None) -> List[Tuple]:
        """Get all meals, optionally filtered by user_id"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute("""
                SELECT id, user_id, username, message, photo_path, timestamp
                FROM meals
                WHERE user_id = ?
                ORDER BY timestamp DESC
            """, (user_id,))
        else:
            cursor.execute("""
                SELECT id, user_id, username, message, photo_path, timestamp
                FROM meals
                ORDER BY timestamp DESC
            """)
        
        meals = cursor.fetchall()
        conn.close()
        
        return meals
    
    def get_meals_by_date_range(
        self, 
        user_id: int, 
        start_date: str, 
        end_date: str
    ) -> List[Tuple]:
        """Get meals within a date range"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, user_id, username, message, photo_path, timestamp
            FROM meals
            WHERE user_id = ? AND DATE(timestamp) BETWEEN ? AND ?
            ORDER BY timestamp DESC
        """, (user_id, start_date, end_date))
        
        meals = cursor.fetchall()
        conn.close()
        
        return meals
    
    def delete_meal(self, meal_id: int, user_id: int) -> bool:
        """Delete a meal entry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM meals
            WHERE id = ? AND user_id = ?
        """, (meal_id, user_id))
        
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted
    
    def get_stats(self, user_id: int) -> Dict[str, Any]:
        """Get statistics for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total meals
        cursor.execute("""
            SELECT COUNT(*) FROM meals WHERE user_id = ?
        """, (user_id,))
        total_meals = cursor.fetchone()[0]
        
        # Meals today
        cursor.execute("""
            SELECT COUNT(*) FROM meals 
            WHERE user_id = ? AND DATE(timestamp) = DATE('now')
        """, (user_id,))
        meals_today = cursor.fetchone()[0]
        
        # Meals this week
        cursor.execute("""
            SELECT COUNT(*) FROM meals 
            WHERE user_id = ? AND DATE(timestamp) >= DATE('now', '-7 days')
        """, (user_id,))
        meals_this_week = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_meals": total_meals,
            "meals_today": meals_today,
            "meals_this_week": meals_this_week
        }
