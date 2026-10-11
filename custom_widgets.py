import tkinter as tk
import math

class BMIGauge(tk.Canvas):
    """
    A custom-drawn semi-circular gauge that displays BMI values 
    and points to the current BMI category.
    """
    def __init__(self, parent, width=320, height=180, bg="#252538", **kwargs):
        super().__init__(parent, width=width, height=height, bg=bg, highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.bg_color = bg
        
        # Center of the dial
        self.cx = width / 2
        self.cy = height - 30
        self.radius = min(width / 2 - 20, height - 40)
        
        # Define ranges
        # BMI range mapped to angle 180 (left) to 0 (right)
        # We display BMI from 10 to 40
        self.min_bmi = 10.0
        self.max_bmi = 40.0
        
        self.draw_base_gauge()
        
    def draw_base_gauge(self):
        """Draws the static background arc and category labels."""
        self.delete("all")
        
        # Draw the colored arc segments
        # angles are in degrees: 180 is left, 0 is right.
        # Underweight (< 18.5) -> Normal (18.5 - 25) -> Overweight (25 - 30) -> Obese (30 - 40)
        # Map values to angles:
        # bmi 10 -> 180 deg
        # bmi 18.5 -> 180 - (8.5/30 * 180) = 180 - 51 = 129 deg
        # bmi 25 -> 180 - (15/30 * 180) = 180 - 90 = 90 deg
        # bmi 30 -> 180 - (20/30 * 180) = 180 - 120 = 60 deg
        # bmi 40 -> 0 deg
        
        # Arc coordinates
        bbox = (self.cx - self.radius, self.cy - self.radius, 
                self.cx + self.radius, self.cy + self.radius)
        
        # Draw background thickness
        width = 24
        
        # Underweight (10 to 18.5) -> Arc angle starts at 180, span is -51 (i.e. goes to 129)
        self.create_arc(bbox, start=180, extent=-51, outline="#89dceb", width=width, style="arc")
        # Normal (18.5 to 25) -> starts at 129, span is -39 (goes to 90)
        self.create_arc(bbox, start=129, extent=-39, outline="#a6e3a1", width=width, style="arc")
        # Overweight (25 to 30) -> starts at 90, span is -30 (goes to 60)
        self.create_arc(bbox, start=90, extent=-30, outline="#f9e2af", width=width, style="arc")
        # Obese (30 to 40) -> starts at 60, span is -60 (goes to 0)
        self.create_arc(bbox, start=60, extent=-60, outline="#f38ba8", width=width, style="arc")
        
        # Draw center pivot point
        self.create_oval(self.cx - 8, self.cy - 8, self.cx + 8, self.cy + 8, fill="#cdd6f4", outline="#313244")
        
        # Draw static category text labels
        # Underweight (Left)
        self.create_text(self.cx - self.radius + 15, self.cy + 15, text="Under", fill="#a6adc8", font=("Arial", 9))
        # Normal (Top-Left)
        self.create_text(self.cx - 40, self.cy - self.radius + 8, text="Normal", fill="#a6adc8", font=("Arial", 9))
        # Overweight (Top-Right)
        self.create_text(self.cx + 40, self.cy - self.radius + 8, text="Over", fill="#a6adc8", font=("Arial", 9))
        # Obese (Right)
        self.create_text(self.cx + self.radius - 15, self.cy + 15, text="Obese", fill="#a6adc8", font=("Arial", 9))

    def update_gauge(self, bmi):
        """Redraws the gauge and needle pointing to the given BMI value."""
        self.draw_base_gauge()
        
        if bmi is None:
            # Draw no-value state
            self.create_text(self.cx, self.cy - 30, text="--.-", fill="#cdd6f4", font=("Arial", 28, "bold"))
            self.create_text(self.cx, self.cy - 5, text="No Data Selected", fill="#a6adc8", font=("Arial", 11, "bold"))
            return
            
        # Clamp BMI
        clamped_bmi = max(self.min_bmi, min(self.max_bmi, bmi))
        
        # Calculate angle (in radians for trig)
        # bmi 10 -> 180 degrees (pi radians)
        # bmi 40 -> 0 degrees (0 radians)
        ratio = (clamped_bmi - self.min_bmi) / (self.max_bmi - self.min_bmi)
        angle_deg = 180 - (ratio * 180)
        angle_rad = math.radians(angle_deg)
        
        # Needle end point
        needle_len = self.radius - 15
        nx = self.cx + needle_len * math.cos(angle_rad)
        ny = self.cy - needle_len * math.sin(angle_rad)
        
        # Draw shadow needle
        self.create_line(self.cx, self.cy + 1, nx + 1, ny + 1, fill="#11111b", width=4, arrow="last")
        # Draw actual needle
        self.create_line(self.cx, self.cy, nx, ny, fill="#cba6f7", width=3, arrow="last")
        
        # Determine category and color
        if bmi < 18.5:
            cat = "Underweight"
            color = "#89dceb"
        elif bmi < 25:
            cat = "Normal Weight"
            color = "#a6e3a1"
        elif bmi < 30:
            cat = "Overweight"
            color = "#f9e2af"
        else:
            cat = "Obese"
            color = "#f38ba8"
            
        # Draw large text showing BMI
        self.create_text(self.cx, self.cy - 30, text=f"{bmi:.1f}", fill="#cdd6f4", font=("Arial", 28, "bold"))
        self.create_text(self.cx, self.cy - 5, text=cat, fill=color, font=("Arial", 12, "bold"))


class TrendGraph(tk.Canvas):
    """
    A custom-drawn line chart that plots historical BMI/Weight data 
    and handles mouse hovering with an interactive tooltip card.
    """
    def __init__(self, parent, width=550, height=280, bg="#252538", **kwargs):
        super().__init__(parent, width=width, height=height, bg=bg, highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        
        # Padding around the graph plot area
        self.pad_left = 50
        self.pad_right = 30
        self.pad_top = 30
        self.pad_bottom = 40
        
        self.plot_w = width - self.pad_left - self.pad_right
        self.plot_h = height - self.pad_top - self.pad_bottom
        
        self.data_points = []  # List of dicts: {x, y, date, weight, bmi, notes}
        self.hovered_idx = None
        
        # Bind hover/motion events
        self.bind("<Motion>", self.on_mouse_move)
        self.bind("<Leave>", self.on_mouse_leave)
        
        # Initial draw (empty state)
        self.draw_empty()

    def draw_empty(self):
        """Draw placeholder message when no data is loaded."""
        self.delete("all")
        self.create_text(
            self.width / 2, self.height / 2, 
            text="No historical measurements logged yet.\nGo to the Calculator tab to record your BMI.",
            fill="#a6adc8", font=("Arial", 11), justify="center"
        )

    def set_data(self, measurements):
        """
        Populate data and redraw the graph.
        measurements: list of dicts from get_measurements (keys: weight, height, bmi, recorded_at, notes)
        """
        self.delete("all")
        self.data_points = []
        self.hovered_idx = None
        
        if not measurements:
            self.draw_empty()
            return
            
        n = len(measurements)
        
        # Find min/max values to scale Y-axis
        bmis = [m['bmi'] for m in measurements]
        min_bmi = min(bmis)
        max_bmi = max(bmis)
        
        # Add 10% padding to Y range, ensure at least some range
        y_range = max_bmi - min_bmi
        if y_range == 0:
            y_range = 4.0  # fallback range
            y_min = min_bmi - 2.0
            y_max = min_bmi + 2.0
        else:
            y_min = max(0.0, min_bmi - y_range * 0.15)
            y_max = max_bmi + y_range * 0.15
            
        # Draw Grid & Y-Axis labels
        grid_lines = 4
        for i in range(grid_lines + 1):
            val = y_min + (y_max - y_min) * (i / grid_lines)
            y_pos = self.pad_top + self.plot_h - (i / grid_lines) * self.plot_h
            
            # Grid line
            self.create_line(self.pad_left, y_pos, self.width - self.pad_right, y_pos, fill="#313244", dash=(2, 2))
            # Y label
            self.create_text(self.pad_left - 10, y_pos, text=f"{val:.1f}", fill="#a6adc8", font=("Arial", 8), anchor="e")

        # Map X-coordinates
        # If only 1 measurement, put it in the middle of X
        # Otherwise space them equally
        coords = []
        for i, m in enumerate(measurements):
            if n == 1:
                x_pos = self.pad_left + self.plot_w / 2
            else:
                x_pos = self.pad_left + (i / (n - 1)) * self.plot_w
                
            y_ratio = (m['bmi'] - y_min) / (y_max - y_min)
            y_pos = self.pad_top + self.plot_h - (y_ratio * self.plot_h)
            
            coords.append((x_pos, y_pos, m))
            
        # Draw trend line
        if len(coords) > 1:
            line_coords = []
            for x, y, _ in coords:
                line_coords.extend([x, y])
            self.create_line(line_coords, fill="#89b4fa", width=3, capstyle="round", joinstyle="round")
            
        # Draw data points and save click/hover zones
        for i, (x, y, m) in enumerate(coords):
            # Draw point dot (blue circle)
            pt_id = self.create_oval(x - 5, y - 5, x + 5, y + 5, fill="#1e1e2e", outline="#89b4fa", width=2)
            
            # Save mapping info
            self.data_points.append({
                'x': x,
                'y': y,
                'pt_id': pt_id,
                'date': m['recorded_at'],
                'weight': m['weight'],
                'height': m['height'],
                'bmi': m['bmi'],
                'notes': m['notes'] or ""
            })
            
            # X-Axis Labels (Date)
            # To prevent overlapping date texts, we skip printing intermediate dates if there are too many
            show_date = False
            if n <= 5:
                show_date = True
            elif n <= 10 and i % 2 == 0:
                show_date = True
            elif n > 10 and (i == 0 or i == n-1 or i == n // 2):
                show_date = True
                
            if show_date:
                # Format date to MM-DD or keep as is
                date_str = m['recorded_at']
                # If date is YYYY-MM-DD, display as MM/DD for simplicity
                if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
                    date_str = date_str[5:10].replace('-', '/')
                    
                self.create_text(x, self.height - self.pad_bottom + 15, text=date_str, fill="#a6adc8", font=("Arial", 8))

        # Bottom Border
        self.create_line(self.pad_left, self.height - self.pad_bottom, self.width - self.pad_right, self.height - self.pad_bottom, fill="#45475a", width=1)
        # Left Border
        self.create_line(self.pad_left, self.pad_top, self.pad_left, self.height - self.pad_bottom, fill="#45475a", width=1)

    def on_mouse_move(self, event):
        """Detect if mouse is hovering over a data point and trigger tooltip redraw."""
        if not self.data_points:
            return
            
        mx, my = event.x, event.y
        closest_idx = None
        min_dist = 10.0  # maximum hover radius in pixels
        
        for idx, pt in enumerate(self.data_points):
            dist = math.hypot(mx - pt['x'], my - pt['y'])
            if dist < min_dist:
                min_dist = dist
                closest_idx = idx
                
        if closest_idx != self.hovered_idx:
            self.hovered_idx = closest_idx
            self.redraw_hover_effects()

    def on_mouse_leave(self, event):
        """Remove highlights and tooltips when mouse leaves canvas."""
        if self.hovered_idx is not None:
            self.hovered_idx = None
            self.redraw_hover_effects()

    def redraw_hover_effects(self):
        """Cleans and redraws the hover highlight point and tooltip card."""
        # Clean previous tooltip items
        self.delete("tooltip")
        
        # Reset all dots outlines
        for idx, pt in enumerate(self.data_points):
            self.itemconfig(pt['pt_id'], fill="#1e1e2e", outline="#89b4fa", width=2)
            
        if self.hovered_idx is None:
            return
            
        # Apply hover styling to active point
        pt = self.data_points[self.hovered_idx]
        self.itemconfig(pt['pt_id'], fill="#cba6f7", outline="#cba6f7", width=4)
        
        # Draw tooltip card
        # Text details
        tip_text = (
            f"Date: {pt['date']}\n"
            f"Weight: {pt['weight']:.1f} kg\n"
            f"BMI: {pt['bmi']:.2f}\n"
        )
        if pt['notes']:
            # Wrap notes if too long
            note = pt['notes']
            if len(note) > 20:
                note = note[:17] + "..."
            tip_text += f"Note: {note}"
        else:
            tip_text = tip_text.strip()
            
        # Draw tooltip rectangle box
        # Decide if tooltip should appear to the left or right of the point to avoid edge clipping
        box_w = 140
        box_h = 75 if pt['notes'] else 60
        
        if pt['x'] + box_w + 15 > self.width:
            tx1 = pt['x'] - box_w - 10
        else:
            tx1 = pt['x'] + 10
            
        if pt['y'] - box_h / 2 < 10:
            ty1 = 10
        elif pt['y'] + box_h / 2 > self.height - 10:
            ty1 = self.height - box_h - 10
        else:
            ty1 = pt['y'] - box_h / 2
            
        tx2 = tx1 + box_w
        ty2 = ty1 + box_h
        
        # Tooltip card background and outline
        self.create_rectangle(tx1, ty1, tx2, ty2, fill="#11111b", outline="#cba6f7", width=1.5, tags="tooltip")
        
        # Tooltip text
        self.create_text(
            tx1 + 10, ty1 + 10, 
            text=tip_text, fill="#cdd6f4", font=("Arial", 9), 
            anchor="nw", justify="left", tags="tooltip"
        )
