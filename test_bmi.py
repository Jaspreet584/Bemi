import unittest
import os
import sqlite3
import database as db

class TestBMICalculator(unittest.TestCase):
    def setUp(self):
        # Use a separate test database file
        self.test_db = "test_bmi_tracker.db"
        # Ensure it is clean
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        db.init_db(self.test_db)

    def tearDown(self):
        # Clean up database file
        if os.path.exists(self.test_db):
            try:
                os.remove(self.test_db)
            except PermissionError:
                pass

    def test_create_user(self):
        # Valid user creation
        uid = db.create_user("Alice", 25, "Female", db_path=self.test_db)
        self.assertIsNotNone(uid)
        
        users = db.get_users(db_path=self.test_db)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]["name"], "Alice")
        self.assertEqual(users[0]["age"], 25)
        self.assertEqual(users[0]["gender"], "Female")

    def test_duplicate_user_raises_value_error(self):
        db.create_user("Alice", 25, "Female", db_path=self.test_db)
        with self.assertRaises(ValueError):
            db.create_user("Alice", 30, "Male", db_path=self.test_db)

    def test_invalid_user_inputs(self):
        # Empty name
        with self.assertRaises(ValueError):
            db.create_user("", 25, "Female", db_path=self.test_db)
            
        # Age too large
        with self.assertRaises(ValueError):
            db.create_user("Bob", 150, "Male", db_path=self.test_db)
            
        # Age negative
        with self.assertRaises(ValueError):
            db.create_user("Bob", -5, "Male", db_path=self.test_db)
            
        # Invalid gender
        with self.assertRaises(ValueError):
            db.create_user("Bob", 30, "Unknown", db_path=self.test_db)

    def test_update_user(self):
        uid = db.create_user("Alice", 25, "Female", db_path=self.test_db)
        db.update_user(uid, "Alicia", 26, "Female", db_path=self.test_db)
        
        user = db.get_user(uid, db_path=self.test_db)
        self.assertEqual(user["name"], "Alicia")
        self.assertEqual(user["age"], 26)

    def test_delete_user_cascade(self):
        uid = db.create_user("Alice", 25, "Female", db_path=self.test_db)
        # Add a measurement
        db.add_measurement(uid, 60.0, 1.7, 20.76, "Test log", db_path=self.test_db)
        
        # Verify measurement exists
        records = db.get_measurements(uid, db_path=self.test_db)
        self.assertEqual(len(records), 1)
        
        # Delete user
        db.delete_user(uid, db_path=self.test_db)
        
        # Verify user is gone
        user = db.get_user(uid, db_path=self.test_db)
        self.assertIsNone(user)
        
        # Verify measurements are deleted (cascade constraint test)
        records = db.get_measurements(uid, db_path=self.test_db)
        self.assertEqual(len(records), 0)

    def test_measurements_crud(self):
        uid = db.create_user("Alice", 25, "Female", db_path=self.test_db)
        
        # Add measurements
        mid1 = db.add_measurement(uid, 65.0, 1.7, 22.49, "Morning weight", db_path=self.test_db)
        mid2 = db.add_measurement(uid, 64.0, 1.7, 22.15, "Evening weight", db_path=self.test_db)
        
        records = db.get_measurements(uid, db_path=self.test_db)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["weight"], 65.0)
        self.assertEqual(records[1]["weight"], 64.0)
        
        # Delete measurement
        db.delete_measurement(mid1, db_path=self.test_db)
        records_after = db.get_measurements(uid, db_path=self.test_db)
        self.assertEqual(len(records_after), 1)
        self.assertEqual(records_after[0]["id"], mid2)

    def test_user_stats(self):
        uid = db.create_user("Bob", 40, "Male", db_path=self.test_db)
        
        # Log multiple measurements
        db.add_measurement(uid, 80.0, 1.8, 24.69, "Start", db_path=self.test_db)
        db.add_measurement(uid, 78.0, 1.8, 24.07, "Week 1", db_path=self.test_db)
        db.add_measurement(uid, 75.0, 1.8, 23.15, "Week 2", db_path=self.test_db)
        
        stats = db.get_user_stats(uid, db_path=self.test_db)
        self.assertIsNotNone(stats)
        
        self.assertEqual(stats["count"], 3)
        self.assertEqual(stats["min_bmi"], 23.15)
        self.assertEqual(stats["max_bmi"], 24.69)
        self.assertEqual(stats["avg_bmi"], round((24.69 + 24.07 + 23.15) / 3, 2))
        self.assertEqual(stats["first_weight"], 80.0)
        self.assertEqual(stats["latest_weight"], 75.0)
        self.assertEqual(stats["weight_change"], -5.0)
        self.assertEqual(stats["first_bmi"], 24.69)
        self.assertEqual(stats["latest_bmi"], 23.15)
        self.assertEqual(stats["bmi_change"], round(23.15 - 24.69, 2))

if __name__ == "__main__":
    unittest.main()
