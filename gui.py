import tkinter as tk
from tkinter import ttk, messagebox
import database as db
from custom_widgets import BMIGauge, TrendGraph
import datetime

# Color Palette Design Tokens
THEME = {
    "bg": "#11111b",          # Deep dark background
    "surface": "#181825",     # Dark violet panel background
    "card": "#252538",        # Card surface background
    "accent": "#cba6f7",      # Pastel Lavender accent
    "text": "#cdd6f4",        # Soft white text
    "text_muted": "#a6adc8",  # Cool grey text
    "border": "#313244",      # Dark border gray
    "active": "#45475a",      # Focus/hover gray
    "accent_hover": "#b4befe" # Lighter violet hover
}

class BMITrackerApp(tk.Tk):
    def __init__(self, db_path="bmi_tracker.db"):
        super().__init__()
        self.db_path = db_path
        self.title("Bemi - BMI Monitor & Health Analyzer")
        self.geometry("950x600")
        self.configure(bg=THEME["bg"])
        self.resizable(False, False)
        
        # Initialize DB
        db.init_db(self.db_path)
        
        # Application State
        self.current_user = None
        self.users = []
        self.unit_system = tk.StringVar(value="Metric")  # Metric or Imperial
        self.selected_tab = "Calculator"
        
        self.setup_styles()
        self.create_layout()
        
        # Load user list and select the first user
        self.load_users()
        
    def setup_styles(self):
        """Configure ttk styles for Treeview and dropdowns to fit dark theme."""
        style = ttk.Style(self)
        style.theme_use("default")
        
        # Treeview styling
        style.configure("Treeview", 
                        background=THEME["card"], 
                        foreground=THEME["text"], 
                        rowheight=28, 
                        fieldbackground=THEME["card"],
                        borderwidth=0,
                        font=("Arial", 9))
        
        style.map("Treeview", 
                  background=[("selected", THEME["accent"])], 
                  foreground=[("selected", "#11111b")])
        
        style.configure("Treeview.Heading", 
                        background=THEME["border"], 
                        foreground=THEME["text"], 
                        relief="flat", 
                        font=("Arial", 10, "bold"),
                        padding=5)
        
        style.map("Treeview.Heading", background=[("active", THEME["active"])])
        
        # Remove borders
        style.layout("Treeview", [('style.treearea', {'sticky': 'nswe'})])
        
        # OptionMenu configuration
        self.option_add("*TCombobox*Listbox.background", THEME["card"])
        self.option_add("*TCombobox*Listbox.foreground", THEME["text"])
        self.option_add("*TCombobox*Listbox.selectBackground", THEME["accent"])
        self.option_add("*TCombobox*Listbox.selectForeground", "#11111b")
        
        style.configure("TCombobox", 
                        fieldbackground=THEME["card"], 
                        background=THEME["border"], 
                        foreground=THEME["text"],
                        arrowcolor=THEME["text"])

    def create_layout(self):
        """Constructs the sidebar profile panel and main dashboard container."""
        # Top title bar (logo area)
        title_frame = tk.Frame(self, bg=THEME["bg"], height=50)
        title_frame.pack(fill="x", side="top", padx=20, pady=10)
        
        title_lbl = tk.Label(title_frame, text="Bemi", fg=THEME["accent"], bg=THEME["bg"], font=("Arial", 20, "bold"))
        title_lbl.pack(side="left")
        
        subtitle_lbl = tk.Label(title_frame, text="• BMI Monitor & Trend Analyzer", fg=THEME["text_muted"], bg=THEME["bg"], font=("Arial", 11, "italic"))
        subtitle_lbl.pack(side="left", padx=10, pady=8)
        
        # Split Layout Container
        main_container = tk.Frame(self, bg=THEME["bg"])
        main_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # 1. Left Panel (Sidebar - User Profiles)
        self.sidebar = tk.Frame(main_container, bg=THEME["surface"], width=280)
        self.sidebar.pack(side="left", fill="y", padx=(0, 15))
        self.sidebar.pack_propagate(False)
        self.build_sidebar()
        
        # 2. Right Panel (Main Content Dashboard)
        self.dashboard = tk.Frame(main_container, bg=THEME["surface"])
        self.dashboard.pack(side="right", fill="both", expand=True)
        
        self.build_dashboard()

    def build_sidebar(self):
        """Fills the sidebar with profile selector and stats summary card."""
        # Header
        lbl = tk.Label(self.sidebar, text="USER PROFILE", fg=THEME["text"], bg=THEME["surface"], font=("Arial", 11, "bold"))
        lbl.pack(anchor="w", padx=20, pady=(20, 10))
        
        # User selector frame
        select_frame = tk.Frame(self.sidebar, bg=THEME["surface"])
        select_frame.pack(fill="x", padx=20, pady=5)
        
        self.user_var = tk.StringVar()
        self.user_dropdown = ttk.Combobox(select_frame, textvariable=self.user_var, state="readonly", font=("Arial", 10))
        self.user_dropdown.pack(fill="x", side="left", expand=True)
        self.user_dropdown.bind("<<ComboboxSelected>>", self.on_user_selected)
        
        # Profile action buttons
        btn_frame = tk.Frame(self.sidebar, bg=THEME["surface"])
        btn_frame.pack(fill="x", padx=20, pady=15)
        
        new_btn = self.create_button(btn_frame, "New Profile", self.open_new_user_dialog, accent=True)
        new_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        edit_btn = self.create_button(btn_frame, "Edit", self.open_edit_user_dialog)
        edit_btn.pack(side="left", padx=2)
        
        del_btn = self.create_button(btn_frame, "Delete", self.delete_current_user)
        del_btn.pack(side="left", padx=(5, 0))
        
        # Separator line
        sep = tk.Frame(self.sidebar, bg=THEME["border"], height=1)
        sep.pack(fill="x", padx=20, pady=10)
        
        # Profile Stats Card
        stats_lbl = tk.Label(self.sidebar, text="PROFILE STATS", fg=THEME["text"], bg=THEME["surface"], font=("Arial", 11, "bold"))
        stats_lbl.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.stats_card = tk.Frame(self.sidebar, bg=THEME["card"], bd=1, relief="flat", highlightbackground=THEME["border"], highlightthickness=1)
        self.stats_card.pack(fill="both", expand=True, padx=20, pady=(5, 20))
        
        self.lbl_profile_name = tk.Label(self.stats_card, text="Select or Create Profile", fg=THEME["accent"], bg=THEME["card"], font=("Arial", 12, "bold"))
        self.lbl_profile_name.pack(anchor="w", padx=15, pady=(15, 10))
        
        self.lbl_profile_meta = tk.Label(self.stats_card, text="Age: -- | Gender: --", fg=THEME["text_muted"], bg=THEME["card"], font=("Arial", 9))
        self.lbl_profile_meta.pack(anchor="w", padx=15, pady=2)
        
        self.lbl_profile_logs = tk.Label(self.stats_card, text="Total Logs: 0", fg=THEME["text_muted"], bg=THEME["card"], font=("Arial", 9))
        self.lbl_profile_logs.pack(anchor="w", padx=15, pady=2)
        
        self.lbl_weight_progress = tk.Label(self.stats_card, text="Weight Progress: --", fg=THEME["text_muted"], bg=THEME["card"], font=("Arial", 9))
        self.lbl_weight_progress.pack(anchor="w", padx=15, pady=2)
        
        # Empty space filler
        lbl_filler = tk.Label(self.stats_card, bg=THEME["card"])
        lbl_filler.pack(fill="both", expand=True)

    def build_dashboard(self):
        """Constructs tab navigation and the corresponding views inside the dashboard."""
        # Tab Header Bar
        self.tab_bar = tk.Frame(self.dashboard, bg=THEME["surface"], height=40)
        self.tab_bar.pack(fill="x", side="top")
        
        self.tab_buttons = {}
        tabs = [("Calculator", "BMI Calculator"), ("History", "Log History"), ("Trends", "Trends & Analytics")]
        
        for tab_id, tab_label in tabs:
            btn = tk.Button(self.tab_bar, text=tab_label, relief="flat", bd=0, padx=15, pady=10,
                            font=("Arial", 10, "bold"), bg=THEME["surface"], fg=THEME["text_muted"],
                            activebackground=THEME["surface"], activeforeground=THEME["accent"])
            btn.config(command=lambda tid=tab_id: self.select_tab(tid))
            btn.pack(side="left")
            self.tab_buttons[tab_id] = btn
            
        # Tab Content Container
        self.content_container = tk.Frame(self.dashboard, bg=THEME["surface"])
        self.content_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create Frames for each tab
        self.tab_frames = {
            "Calculator": tk.Frame(self.content_container, bg=THEME["surface"]),
            "History": tk.Frame(self.content_container, bg=THEME["surface"]),
            "Trends": tk.Frame(self.content_container, bg=THEME["surface"])
        }
        
        # Build contents for each tab
        self.build_calculator_tab()
        self.build_history_tab()
        self.build_trends_tab()
        
        # Select first tab
        self.select_tab("Calculator")

    def select_tab(self, tab_id):
        """Handles switching between tab views and coloring navigation buttons."""
        self.selected_tab = tab_id
        
        # Update tab button styles
        for tid, btn in self.tab_buttons.items():
            if tid == tab_id:
                btn.config(fg=THEME["accent"], bg=THEME["card"])
            else:
                btn.config(fg=THEME["text_muted"], bg=THEME["surface"])
                
        # Toggle frames
        for tid, frame in self.tab_frames.items():
            if tid == tab_id:
                frame.pack(fill="both", expand=True)
            else:
                frame.pack_forget()
                
        # Refresh widgets specific to tab
        if tab_id == "Trends":
            self.refresh_trends()
        elif tab_id == "History":
            self.refresh_history_table()

    # ==================== CALCULATOR TAB ====================
    def build_calculator_tab(self):
        """Constructs layout, input fields, sliders, gauges, and advice cards for Tab 1."""
        frame = self.tab_frames["Calculator"]
        
        # Grid layout for inputs (Left) and visualization (Right)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(0, weight=1)
        
        # Left Grid: Input Fields
        input_container = tk.Frame(frame, bg=THEME["surface"])
        input_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Title
        hdr = tk.Label(input_container, text="Calculate BMI", fg=THEME["text"], bg=THEME["surface"], font=("Arial", 14, "bold"))
        hdr.pack(anchor="w", pady=(0, 15))
        
        # Unit Switcher (Metric/Imperial)
        unit_frame = tk.Frame(input_container, bg=THEME["surface"])
        unit_frame.pack(anchor="w", pady=5)
        
        tk.Label(unit_frame, text="Unit System: ", fg=THEME["text_muted"], bg=THEME["surface"], font=("Arial", 10)).pack(side="left")
        
        # Custom-styled Radio button look
        self.r_metric = tk.Radiobutton(unit_frame, text="Metric (kg/cm)", variable=self.unit_system, value="Metric",
                                       bg=THEME["surface"], fg=THEME["text"], selectcolor=THEME["bg"],
                                       activebackground=THEME["surface"], activeforeground=THEME["accent"],
                                       font=("Arial", 9), command=self.toggle_unit_system)
        self.r_metric.pack(side="left", padx=10)
        
        self.r_imperial = tk.Radiobutton(unit_frame, text="Imperial (lbs/in)", variable=self.unit_system, value="Imperial",
                                         bg=THEME["surface"], fg=THEME["text"], selectcolor=THEME["bg"],
                                         activebackground=THEME["surface"], activeforeground=THEME["accent"],
                                         font=("Arial", 9), command=self.toggle_unit_system)
        self.r_imperial.pack(side="left")
        
        # Inputs Frame
        self.fields_frame = tk.Frame(input_container, bg=THEME["surface"])
        self.fields_frame.pack(fill="x", pady=15)
        
        # Log entry notes frame
        notes_frame = tk.Frame(input_container, bg=THEME["surface"])
        notes_frame.pack(fill="x", pady=5)
        tk.Label(notes_frame, text="Optional Log Note (e.g., 'Morning check', 'Post-run'):", fg=THEME["text_muted"], bg=THEME["surface"], font=("Arial", 9)).pack(anchor="w")
        
        self.entry_notes = tk.Entry(notes_frame, bg=THEME["card"], fg=THEME["text"], relief="flat", highlightbackground=THEME["border"], highlightthickness=1, font=("Arial", 10), insertbackground=THEME["text"])
        self.entry_notes.pack(fill="x", pady=5, ipady=4)
        
        # Log Button
        self.btn_log = self.create_button(input_container, "Log BMI Measurement", self.log_measurement, accent=True)
        self.btn_log.pack(fill="x", pady=15, ipady=4)
        
        # Build inputs inside fields_frame
        self.create_input_fields()
        
        # Right Grid: Results & Custom Gauge
        result_container = tk.Frame(frame, bg=THEME["surface"])
        result_container.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Visual Title
        vis_hdr = tk.Label(result_container, text="Health Status", fg=THEME["text"], bg=THEME["surface"], font=("Arial", 14, "bold"))
        vis_hdr.pack(anchor="w")
        
        # Custom Canvas Gauge
        self.gauge = BMIGauge(result_container, width=320, height=180, bg=THEME["surface"])
        self.gauge.pack(pady=10)
        self.gauge.update_gauge(None) # empty state
        
        # Advice Recommendation Card
        self.advice_card = tk.Frame(result_container, bg=THEME["card"], bd=1, relief="flat", highlightbackground=THEME["border"], highlightthickness=1)
        self.advice_card.pack(fill="both", expand=True, pady=(5, 0))
        
        self.advice_title = tk.Label(self.advice_card, text="Recommendations", fg=THEME["accent"], bg=THEME["card"], font=("Arial", 10, "bold"))
        self.advice_title.pack(anchor="w", padx=15, pady=(10, 5))
        
        self.advice_text = tk.Label(self.advice_card, text="Select a user and type height & weight to calculate BMI and view personalized health recommendations.", 
                                    fg=THEME["text_muted"], bg=THEME["card"], font=("Arial", 9), wraplength=280, justify="left")
        self.advice_text.pack(anchor="nw", padx=15, pady=(0, 15), fill="both", expand=True)

    def create_input_fields(self):
        """Draws current fields based on selected Unit System (Metric vs Imperial)."""
        # Clear fields frame
        for child in self.fields_frame.winfo_children():
            child.destroy()
            
        self.fields = {}
        
        if self.unit_system.get() == "Metric":
            # Weight (kg)
            w_frame = tk.Frame(self.fields_frame, bg=THEME["surface"])
            w_frame.pack(fill="x", pady=5)
            tk.Label(w_frame, text="Weight (kg):", fg=THEME["text"], bg=THEME["surface"], font=("Arial", 10)).pack(anchor="w")
            
            self.fields["weight"] = tk.Entry(w_frame, bg=THEME["card"], fg=THEME["text"], relief="flat", highlightbackground=THEME["border"], highlightthickness=1, font=("Arial", 10), insertbackground=THEME["text"])
            self.fields["weight"].pack(fill="x", pady=3, ipady=4)
            self.fields["weight"].bind("<KeyRelease>", self.on_input_changed)
            
            # Height (cm)
            h_frame = tk.Frame(self.fields_frame, bg=THEME["surface"])
            h_frame.pack(fill="x", pady=5)
            tk.Label(h_frame, text="Height (cm):", fg=THEME["text"], bg=THEME["surface"], font=("Arial", 10)).pack(anchor="w")
            
            self.fields["height"] = tk.Entry(h_frame, bg=THEME["card"], fg=THEME["text"], relief="flat", highlightbackground=THEME["border"], highlightthickness=1, font=("Arial", 10), insertbackground=THEME["text"])
            self.fields["height"].pack(fill="x", pady=3, ipady=4)
            self.fields["height"].bind("<KeyRelease>", self.on_input_changed)
        else:
            # Imperial: Weight (lbs)
            w_frame = tk.Frame(self.fields_frame, bg=THEME["surface"])
            w_frame.pack(fill="x", pady=5)
            tk.Label(w_frame, text="Weight (lbs):", fg=THEME["text"], bg=THEME["surface"], font=("Arial", 10)).pack(anchor="w")
            
            self.fields["weight"] = tk.Entry(w_frame, bg=THEME["card"], fg=THEME["text"], relief="flat", highlightbackground=THEME["border"], highlightthickness=1, font=("Arial", 10), insertbackground=THEME["text"])
            self.fields["weight"].pack(fill="x", pady=3, ipady=4)
            self.fields["weight"].bind("<KeyRelease>", self.on_input_changed)
            
            # Height Feet & Inches
            h_lbl_frame = tk.Frame(self.fields_frame, bg=THEME["surface"])
            h_lbl_frame.pack(fill="x", pady=(5, 0))
            tk.Label(h_lbl_frame, text="Height:", fg=THEME["text"], bg=THEME["surface"], font=("Arial", 10)).pack(anchor="w")
            
            h_inputs = tk.Frame(self.fields_frame, bg=THEME["surface"])
            h_inputs.pack(fill="x", pady=3)
            
            # Feet Input
            self.fields["feet"] = tk.Entry(h_inputs, bg=THEME["card"], fg=THEME["text"], relief="flat", highlightbackground=THEME["border"], highlightthickness=1, font=("Arial", 10), width=10, insertbackground=THEME["text"])
            self.fields["feet"].pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=4)
            self.fields["feet"].bind("<KeyRelease>", self.on_input_changed)
            tk.Label(h_inputs, text="ft", fg=THEME["text_muted"], bg=THEME["surface"]).pack(side="left", padx=(0, 15))
            
            # Inches Input
            self.fields["inches"] = tk.Entry(h_inputs, bg=THEME["card"], fg=THEME["text"], relief="flat", highlightbackground=THEME["border"], highlightthickness=1, font=("Arial", 10), width=10, insertbackground=THEME["text"])
            self.fields["inches"].pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=4)
            self.fields["inches"].bind("<KeyRelease>", self.on_input_changed)
            tk.Label(h_inputs, text="in", fg=THEME["text_muted"], bg=THEME["surface"]).pack(side="left")

    def toggle_unit_system(self):
        """Clears inputs and toggles between metric/imperial layouts."""
        self.create_input_fields()
        self.gauge.update_gauge(None)
        self.reset_advice_card()
        
    def reset_advice_card(self):
        self.advice_title.config(text="Recommendations", fg=THEME["accent"])
        self.advice_text.config(text="Enter valid height & weight to calculate BMI and view suggestions.", fg=THEME["text_muted"])

    def validate_and_calculate(self):
        """Validates current input boxes and calculates numeric BMI value. Returns None if invalid."""
        if not self.current_user:
            return None
            
        try:
            w_str = self.fields["weight"].get().strip()
            if not w_str:
                return None
            weight = float(w_str)
            if weight <= 0 or weight > 1000:
                return None
                
            if self.unit_system.get() == "Metric":
                h_str = self.fields["height"].get().strip()
                if not h_str:
                    return None
                height_cm = float(h_str)
                if height_cm <= 0 or height_cm > 300:
                    return None
                
                # BMI = weight(kg) / height(m)^2
                height_m = height_cm / 100.0
                bmi = weight / (height_m * height_m)
                return round(bmi, 2)
            else:
                ft_str = self.fields["feet"].get().strip()
                in_str = self.fields["inches"].get().strip()
                if not ft_str:
                    return None
                    
                feet = float(ft_str)
                # inches can be empty/0
                inches = float(in_str) if in_str else 0.0
                
                if feet < 0 or feet > 10 or inches < 0 or inches >= 12:
                    return None
                    
                total_inches = (feet * 12) + inches
                if total_inches <= 0:
                    return None
                    
                # BMI = 703 * weight(lbs) / height(inches)^2
                bmi = 703 * weight / (total_inches * total_inches)
                return round(bmi, 2)
        except ValueError:
            return None

    def on_input_changed(self, event):
        """Triggers automatically as user types, updates gauge and advice cards in real-time."""
        bmi = self.validate_and_calculate()
        if bmi is not None:
            self.gauge.update_gauge(bmi)
            self.update_advice_card(bmi)
        else:
            self.gauge.update_gauge(None)
            self.reset_advice_card()

    def update_advice_card(self, bmi):
        """Displays formatted health category recommendations based on calculated BMI."""
        if bmi < 18.5:
            cat = "Underweight"
            color = "#89dceb"
            text = (
                "Your BMI indicates you are underweight. Consider consulting a nutritionist or "
                "healthcare provider to design a balanced meal plan focused on nutrient-dense foods "
                "and strength building to increase healthy mass safely."
            )
        elif bmi < 25:
            cat = "Normal Weight"
            color = "#a6e3a1"
            text = (
                "Great job! A normal BMI indicates a healthy balance. Focus on maintaining your "
                "current weight with regular physical activity (at least 150 minutes of moderate exercise "
                "per week) and a rich, diverse diet."
            )
        elif bmi < 30:
            cat = "Overweight"
            color = "#f9e2af"
            text = (
                "Your BMI falls in the overweight range. Small changes can make a big difference! "
                "Focus on incorporating more whole foods, vegetables, and lean proteins, and engage "
                "in regular cardiovascular and strength exercises."
            )
        else:
            cat = "Obese"
            color = "#f38ba8"
            text = (
                "Your BMI indicates obesity, which can increase risk for health conditions like "
                "hypertension or heart issues. We recommend consulting a medical professional to "
                "establish a safe, progressive fitness and dietary strategy."
            )
            
        self.advice_title.config(text=f"{cat} Suggestions", fg=color)
        self.advice_text.config(text=text, fg=THEME["text"])

    def log_measurement(self):
        """Saves current measurement data to the database and refreshes all tabs."""
        if not self.current_user:
            messagebox.showwarning("No Profile Selected", "Please select or create a user profile first.")
            return
            
        bmi = self.validate_and_calculate()
        if bmi is None:
            messagebox.showerror("Invalid Input", "Please enter valid numeric values for height and weight.")
            return
            
        try:
            # Get weight and height values in kilograms and meters for standard DB saving
            w_input = float(self.fields["weight"].get().strip())
            
            if self.unit_system.get() == "Metric":
                h_input_cm = float(self.fields["height"].get().strip())
                weight_kg = w_input
                height_m = h_input_cm / 100.0
            else:
                feet = float(self.fields["feet"].get().strip())
                inches = float(self.fields["inches"].get().strip()) if self.fields["inches"].get().strip() else 0.0
                total_inches = (feet * 12) + inches
                
                # Conversions: 1 lbs = 0.45359237 kg, 1 inch = 0.0254 m
                weight_kg = w_input * 0.45359237
                height_m = total_inches * 0.0254
                
            notes = self.entry_notes.get().strip()
            
            # Save to database
            db.add_measurement(self.current_user["id"], weight_kg, height_m, bmi, notes, db_path=self.db_path)
            
            # Clear notes
            self.entry_notes.delete(0, tk.END)
            
            # Trigger sidebar stats update
            self.load_user_profile_stats()
            
            # Refresh current selected tab view
            self.select_tab(self.selected_tab)
            
            messagebox.showinfo("Success", "BMI measurement successfully saved to history!")
        except Exception as e:
            messagebox.showerror("Error Logging Data", f"An error occurred: {str(e)}")

    # ==================== HISTORY TAB ====================
    def build_history_tab(self):
        """Constructs scrollable Treeview logs table and controls for Tab 2."""
        frame = self.tab_frames["History"]
        
        # Header layout
        hdr_frame = tk.Frame(frame, bg=THEME["surface"])
        hdr_frame.pack(fill="x", pady=(0, 10))
        
        lbl = tk.Label(hdr_frame, text="Measurement Log History", fg=THEME["text"], bg=THEME["surface"], font=("Arial", 14, "bold"))
        lbl.pack(side="left")
        
        del_btn = self.create_button(hdr_frame, "Delete Selected Record", self.delete_selected_record)
        del_btn.pack(side="right")
        
        # Grid frame for tree and scrollbar
        grid_frame = tk.Frame(frame, bg=THEME["surface"])
        grid_frame.pack(fill="both", expand=True)
        
        # Treeview Columns
        columns = ("date", "weight_kg", "height_m", "bmi", "notes")
        self.tree = ttk.Treeview(grid_frame, columns=columns, show="headings")
        
        self.tree.heading("date", text="Date")
        self.tree.heading("weight_kg", text="Weight (kg)")
        self.tree.heading("height_m", text="Height (m)")
        self.tree.heading("bmi", text="BMI")
        self.tree.heading("notes", text="Note")
        
        self.tree.column("date", width=120, anchor="center")
        self.tree.column("weight_kg", width=100, anchor="center")
        self.tree.column("height_m", width=100, anchor="center")
        self.tree.column("bmi", width=100, anchor="center")
        self.tree.column("notes", width=250, anchor="w")
        
        # Scrollbar
        sb = tk.Scrollbar(grid_frame, orient="vertical", command=self.tree.yview, bg=THEME["surface"], troughcolor=THEME["bg"])
        self.tree.configure(yscrollcommand=sb.set)
        
        sb.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

    def refresh_history_table(self):
        """Loads and lists the logged data for the current active user."""
        # Clear items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not self.current_user:
            return
            
        records = db.get_measurements(self.current_user["id"], db_path=self.db_path)
        # Reverse to show newest first in the logs table
        for r in reversed(records):
            self.tree.insert("", "end", iid=str(r["id"]), values=(
                r["recorded_at"],
                f"{r['weight']:.1f}",
                f"{r['height']:.2f}",
                f"{r['bmi']:.2f}",
                r["notes"] or ""
            ))

    def delete_selected_record(self):
        """Deletes selected measurement in history and updates UI."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a log record from the table to delete.")
            return
            
        record_id = int(selected[0])
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this historical measurement?"):
            db.delete_measurement(record_id, db_path=self.db_path)
            self.load_user_profile_stats()
            self.refresh_history_table()

    # ==================== TRENDS TAB ====================
    def build_trends_tab(self):
        """Constructs Canvas trend chart layout and analytics metrics grid for Tab 3."""
        frame = self.tab_frames["Trends"]
        
        # Split layout: top statistics metrics, bottom graph
        metrics_frame = tk.Frame(frame, bg=THEME["surface"])
        metrics_frame.pack(fill="x", pady=(0, 10))
        
        # Custom stat cards layout
        self.stat_widgets = {}
        stats_def = [
            ("weight_chg", "WEIGHT PROGRESS", "No Data"),
            ("bmi_chg", "BMI DELTA", "No Data"),
            ("avg_bmi", "AVERAGE BMI", "No Data"),
            ("limits", "MIN / MAX BMI", "No Data")
        ]
        
        for i, (key, title, val) in enumerate(stats_def):
            metrics_frame.columnconfigure(i, weight=1)
            card = tk.Frame(metrics_frame, bg=THEME["card"], bd=1, relief="flat", highlightbackground=THEME["border"], highlightthickness=1)
            card.grid(row=0, column=i, sticky="nsew", padx=5, pady=5)
            
            lbl_title = tk.Label(card, text=title, fg=THEME["text_muted"], bg=THEME["card"], font=("Arial", 8, "bold"))
            lbl_title.pack(anchor="w", padx=10, pady=(10, 2))
            
            lbl_val = tk.Label(card, text=val, fg=THEME["accent"], bg=THEME["card"], font=("Arial", 13, "bold"))
            lbl_val.pack(anchor="w", padx=10, pady=(0, 10))
            
            self.stat_widgets[key] = lbl_val
            
        # Chart widget
        chart_hdr = tk.Label(frame, text="BMI Trend Over Time", fg=THEME["text"], bg=THEME["surface"], font=("Arial", 11, "bold"))
        chart_hdr.pack(anchor="w", pady=(10, 5))
        
        self.chart = TrendGraph(frame, width=580, height=250, bg=THEME["card"])
        self.chart.pack(fill="both", expand=True)

    def refresh_trends(self):
        """Loads stats and populates the Canvas line chart with user readings."""
        if not self.current_user:
            self.chart.draw_empty()
            self.clear_stat_cards()
            return
            
        records = db.get_measurements(self.current_user["id"], db_path=self.db_path)
        stats = db.get_user_stats(self.current_user["id"], db_path=self.db_path)
        
        # Update chart data
        self.chart.set_data(records)
        
        # Update stats text cards
        if not stats:
            self.clear_stat_cards()
            return
            
        # Weight Progress
        w_chg = stats["weight_change"]
        sign = "+" if w_chg > 0 else ""
        color = "#f38ba8" if w_chg > 0 else ("#a6e3a1" if w_chg < 0 else THEME["accent"])
        self.stat_widgets["weight_chg"].config(text=f"{sign}{w_chg:.1f} kg", fg=color)
        
        # BMI Delta
        b_chg = stats["bmi_change"]
        sign_b = "+" if b_chg > 0 else ""
        color_b = "#f38ba8" if b_chg > 0 else ("#a6e3a1" if b_chg < 0 else THEME["accent"])
        self.stat_widgets["bmi_chg"].config(text=f"{sign_b}{b_chg:.2f}", fg=color_b)
        
        # Avg BMI
        self.stat_widgets["avg_bmi"].config(text=f"{stats['avg_bmi']:.1f}")
        
        # Limits
        self.stat_widgets["limits"].config(text=f"{stats['min_bmi']:.1f} / {stats['max_bmi']:.1f}")

    def clear_stat_cards(self):
        for key in self.stat_widgets:
            self.stat_widgets[key].config(text="No Data", fg=THEME["accent"])

    # ==================== DATA & PROFILE CONTROLLERS ====================
    def load_users(self):
        """Fetches and populates profile combobox list from SQLite."""
        self.users = db.get_users(db_path=self.db_path)
        names = [u["name"] for u in self.users]
        self.user_dropdown.config(values=names)
        
        if self.users:
            # Select first user by default
            self.user_dropdown.current(0)
            self.on_user_selected(None)
        else:
            self.user_var.set("")
            self.current_user = None
            self.update_sidebar_empty_state()
            self.gauge.update_gauge(None)
            self.reset_advice_card()
            self.refresh_history_table()
            self.refresh_trends()

    def on_user_selected(self, event):
        """Triggered on dropdown change; shifts active profile reference and updates cards."""
        sel_idx = self.user_dropdown.current()
        if sel_idx >= 0:
            self.current_user = self.users[sel_idx]
            self.load_user_profile_stats()
            # Force gauge update on switch
            self.on_input_changed(None)
            
            # Refresh depending on active tab
            self.select_tab(self.selected_tab)

    def load_user_profile_stats(self):
        """Loads and binds statistics details in the sidebar user card."""
        if not self.current_user:
            self.update_sidebar_empty_state()
            return
            
        user = db.get_user(self.current_user["id"], db_path=self.db_path)
        self.current_user = user # update fresh
        
        self.lbl_profile_name.config(text=user["name"])
        self.lbl_profile_meta.config(text=f"Age: {user['age']} | Gender: {user['gender']}")
        
        # Get count and progress
        records = db.get_measurements(user["id"], db_path=self.db_path)
        stats = db.get_user_stats(user["id"], db_path=self.db_path)
        
        self.lbl_profile_logs.config(text=f"Total Logs: {len(records)}")
        
        if stats:
            w_chg = stats["weight_change"]
            sign = "+" if w_chg > 0 else ""
            color = "#f38ba8" if w_chg > 0 else ("#a6e3a1" if w_chg < 0 else THEME["accent"])
            self.lbl_weight_progress.config(text=f"Progress: {sign}{w_chg:.1f} kg", fg=color)
        else:
            self.lbl_weight_progress.config(text="Progress: No Data", fg=THEME["text_muted"])

    def update_sidebar_empty_state(self):
        self.lbl_profile_name.config(text="No Profiles Found", fg=THEME["text_muted"])
        self.lbl_profile_meta.config(text="Age: -- | Gender: --")
        self.lbl_profile_logs.config(text="Total Logs: 0")
        self.lbl_weight_progress.config(text="Weight Progress: --", fg=THEME["text_muted"])

    def open_new_user_dialog(self):
        """Spawns TopLevel modal frame to add a new profile to the system."""
        UserDialog(self, title="Create New Profile", callback=self.save_new_user)

    def save_new_user(self, name, age, gender):
        try:
            user_id = db.create_user(name, age, gender, db_path=self.db_path)
            self.load_users()
            # Select the newly created user in combobox
            for i, u in enumerate(self.users):
                if u["id"] == user_id:
                    self.user_dropdown.current(i)
                    self.on_user_selected(None)
                    break
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))

    def open_edit_user_dialog(self):
        """Spawns TopLevel modal populated with active user values to modify info."""
        if not self.current_user:
            messagebox.showwarning("Select Profile", "Please select a user profile to edit.")
            return
        UserDialog(self, title="Edit Profile", user_data=self.current_user, callback=self.save_edit_user)

    def save_edit_user(self, name, age, gender):
        try:
            db.update_user(self.current_user["id"], name, age, gender, db_path=self.db_path)
            self.load_users()
            # Keep selected user
            for i, u in enumerate(self.users):
                if u["id"] == self.current_user["id"]:
                    self.user_dropdown.current(i)
                    self.on_user_selected(None)
                    break
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))

    def delete_current_user(self):
        """Prompts validation and deletes current active profile from database."""
        if not self.current_user:
            messagebox.showwarning("Select Profile", "Please select a user profile to delete.")
            return
            
        confirm = messagebox.askyesno(
            "Confirm Delete", 
            f"Are you sure you want to delete profile '{self.current_user['name']}'?\n"
            "This will delete ALL their logged measurements permanently!"
        )
        if confirm:
            db.delete_user(self.current_user["id"], db_path=self.db_path)
            self.load_users()

    # ==================== UTILITY DRAW HELPERS ====================
    def create_button(self, parent, text, command, accent=False):
        """Helper creator for styled modern flat buttons with interactive hovers."""
        bg = THEME["accent"] if accent else THEME["border"]
        fg = "#11111b" if accent else THEME["text"]
        hover = THEME["accent_hover"] if accent else THEME["active"]
        
        btn = tk.Button(
            parent, text=text, command=command, bg=bg, fg=fg,
            activebackground=hover, activeforeground=fg, relief="flat",
            font=("Arial", 9, "bold" if accent else "normal"), bd=0, padx=8, pady=4
        )
        btn.bind("<Enter>", lambda e: btn.config(bg=hover))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))
        return btn


class UserDialog(tk.Toplevel):
    """Modal dialog window for creating or editing user profiles."""
    def __init__(self, parent, title, user_data=None, callback=None):
        super().__init__(parent)
        self.callback = callback
        self.user_data = user_data
        
        self.title(title)
        self.geometry("320x340")
        self.configure(bg=THEME["surface"])
        self.resizable(False, False)
        
        # Modal setup
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        
        # Center in parent
        self.update_idletasks()
        px = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        py = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{px}+{py}")
        
    def create_widgets(self):
        # Header
        lbl_hdr = tk.Label(self, text="PROFILE DETAILS", fg=THEME["accent"], bg=THEME["surface"], font=("Arial", 12, "bold"))
        lbl_hdr.pack(pady=(20, 15))
        
        # Name Entry
        lbl_name = tk.Label(self, text="Name:", fg=THEME["text"], bg=THEME["surface"], font=("Arial", 10))
        lbl_name.pack(anchor="w", padx=25, pady=(5, 2))
        
        self.entry_name = tk.Entry(self, bg=THEME["card"], fg=THEME["text"], relief="flat", highlightbackground=THEME["border"], highlightthickness=1, font=("Arial", 10), insertbackground=THEME["text"])
        self.entry_name.pack(fill="x", padx=25, pady=3, ipady=4)
        
        # Age Entry
        lbl_age = tk.Label(self, text="Age (years):", fg=THEME["text"], bg=THEME["surface"], font=("Arial", 10))
        lbl_age.pack(anchor="w", padx=25, pady=(8, 2))
        
        self.entry_age = tk.Entry(self, bg=THEME["card"], fg=THEME["text"], relief="flat", highlightbackground=THEME["border"], highlightthickness=1, font=("Arial", 10), insertbackground=THEME["text"])
        self.entry_age.pack(fill="x", padx=25, pady=3, ipady=4)
        
        # Gender Selector
        lbl_gender = tk.Label(self, text="Gender:", fg=THEME["text"], bg=THEME["surface"], font=("Arial", 10))
        lbl_gender.pack(anchor="w", padx=25, pady=(8, 2))
        
        self.gender_var = tk.StringVar(value="Male")
        self.gender_cb = ttk.Combobox(self, textvariable=self.gender_var, values=["Male", "Female", "Other"], state="readonly", font=("Arial", 10))
        self.gender_cb.pack(fill="x", padx=25, pady=3)
        
        # Actions button frame
        btn_frame = tk.Frame(self, bg=THEME["surface"])
        btn_frame.pack(fill="x", padx=25, pady=(25, 0))
        
        save_btn = tk.Button(btn_frame, text="Save Profile", bg=THEME["accent"], fg="#11111b", activebackground=THEME["accent_hover"], relief="flat", font=("Arial", 10, "bold"), bd=0, command=self.on_save)
        save_btn.pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=5)
        
        cancel_btn = tk.Button(btn_frame, text="Cancel", bg=THEME["border"], fg=THEME["text"], activebackground=THEME["active"], relief="flat", font=("Arial", 10), bd=0, command=self.destroy)
        cancel_btn.pack(side="right", fill="x", expand=True, padx=(5, 0), ipady=5)
        
        # Populate if editing
        if self.user_data:
            self.entry_name.insert(0, self.user_data["name"])
            self.entry_age.insert(0, str(self.user_data["age"]))
            self.gender_var.set(self.user_data["gender"])
            
    def on_save(self):
        name = self.entry_name.get().strip()
        age_str = self.entry_age.get().strip()
        gender = self.gender_var.get()
        
        if not name:
            messagebox.showerror("Error", "Name is required.", parent=self)
            return
            
        try:
            age = int(age_str)
            if age <= 0 or age > 120:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid age between 1 and 120.", parent=self)
            return
            
        if self.callback:
            self.callback(name, age, gender)
        self.destroy()
