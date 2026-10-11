import sys
import os
import gui

def main():
    # Define database file name
    db_path = "bmi_tracker.db"
    
    print("Starting Bemi BMI Calculator & Analyzer...")
    print(f"Database file: {os.path.abspath(db_path)}")
    
    # Initialize and run the Tkinter application
    app = gui.BMITrackerApp(db_path=db_path)
    app.mainloop()

if __name__ == "__main__":
    main()
