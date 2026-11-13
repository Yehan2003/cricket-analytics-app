import customtkinter as ctk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class CricAnalyticsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Cric Analytics - Commercial Pro Edition")
        self.geometry("1650x980")
        
        # --- 1. TOP HEADER BAR ---
        self.frame_top = ctk.CTkFrame(self, height=70, fg_color="#1a1a1a")
        self.frame_top.pack(fill="x", padx=10, pady=10)
        
        self.lbl_logo = ctk.CTkLabel(self.frame_top, text="🏏 CRIC ANALYTICS", font=("Arial", 16, "bold"), text_color="#00ffcc")
        self.lbl_logo.pack(side="left", padx=20)
        
        self.lbl_status = ctk.CTkLabel(self.frame_top, text="● LIVE", font=("Arial", 12, "bold"), text_color="#ff3333")
        self.lbl_status.pack(side="left", padx=10)
        
        # Extras & Wicket Buttons
        self.btn_wicket = ctk.CTkButton(self.frame_top, text="WICKET", fg_color="#cc0000", hover_color="#990000", width=85, font=("Arial", 11, "bold"))
        self.btn_wicket.pack(side="right", padx=5)
        
        self.btn_legbye = ctk.CTkButton(self.frame_top, text="LEG BYE", fg_color="#3399ff", hover_color="#1a75ff", width=85, font=("Arial", 11, "bold"))
        self.btn_legbye.pack(side="right", padx=5)

        self.btn_bye = ctk.CTkButton(self.frame_top, text="BYE", fg_color="#3399ff", hover_color="#1a75ff", width=75, font=("Arial", 11, "bold"))
        self.btn_bye.pack(side="right", padx=5)

        self.btn_noball = ctk.CTkButton(self.frame_top, text="NO BALL", fg_color="#ff3333", hover_color="#cc0000", width=85, font=("Arial", 11, "bold"))
        self.btn_noball.pack(side="right", padx=5)

        self.btn_wide = ctk.CTkButton(self.frame_top, text="WIDE", fg_color="#ffcc00", text_color="black", hover_color="#cca300", width=75, font=("Arial", 11, "bold"))
        self.btn_wide.pack(side="right", padx=5)

        # --- 2. METRICS CARDS BAR (Powerplay සහ Extras සමඟ යාවත්කාලීන විය) ---
        self.frame_metrics = ctk.CTkFrame(self, height=90, fg_color="#1f1f1f")
        self.frame_metrics.pack(fill="x", padx=10, pady=5)
        
        # 1. Runs Card
        self.card_runs = ctk.CTkFrame(self.frame_metrics, fg_color="#2d2d2d", width=170, height=70)
        self.card_runs.pack(side="left", padx=8, pady=10)
        ctk.CTkLabel(self.card_runs, text="RUNS / WICKETS", font=("Arial", 9), text_color="#888").pack(anchor="w", padx=8, pady=2)
        ctk.CTkLabel(self.card_runs, text="74 / 2", font=("Arial", 16, "bold"), text_color="#00ffcc").pack(anchor="w", padx=8)

        # 2. Overs Card
        self.card_overs = ctk.CTkFrame(self.frame_metrics, fg_color="#2d2d2d", width=150, height=70)
        self.card_overs.pack(side="left", padx=8, pady=10)
        ctk.CTkLabel(self.card_overs, text="OVERS", font=("Arial", 9), text_color="#888").pack(anchor="w", padx=8, pady=2)
        ctk.CTkLabel(self.card_overs, text="11.4 / 20", font=("Arial", 16, "bold"), text_color="white").pack(anchor="w", padx=8)

        # 3. Run Rate Card
        self.card_rrr = ctk.CTkFrame(self.frame_metrics, fg_color="#2d2d2d", width=150, height=70)
        self.card_rrr.pack(side="left", padx=8, pady=10)
        ctk.CTkLabel(self.card_rrr, text="RUN RATE", font=("Arial", 9), text_color="#888").pack(anchor="w", padx=8, pady=2)
        ctk.CTkLabel(self.card_rrr, text="6.34", font=("Arial", 16, "bold"), text_color="#ffcc00").pack(anchor="w", padx=8)

        # 4. Powerplay Card (අලුතින් එකතු කරන ලදී)
        self.card_pp = ctk.CTkFrame(self.frame_metrics, fg_color="#2d2d2d", width=150, height=70)
        self.card_pp.pack(side="left", padx=8, pady=10)
        ctk.CTkLabel(self.card_pp, text="POWERPLAY", font=("Arial", 9), text_color="#888").pack(anchor="w", padx=8, pady=2)
        ctk.CTkLabel(self.card_pp, text="PP 1 (1-6)", font=("Arial", 16, "bold"), text_color="#00bfff").pack(anchor="w", padx=8)

        # 5. Extras Card (අලුතින් එකතු කරන ලදී)
        self.card_extras = ctk.CTkFrame(self.frame_metrics, fg_color="#2d2d2d", width=150, height=70)
        self.card_extras.pack(side="left", padx=8, pady=10)
        ctk.CTkLabel(self.card_extras, text="EXTRAS", font=("Arial", 9), text_color="#888").pack(anchor="w", padx=8, pady=2)
        ctk.CTkLabel(self.card_extras, text="8 (w:4, nb:2, b:2)", font=("Arial", 13, "bold"), text_color="#ff9999").pack(anchor="w", padx=8)

        # Recent Balls Indicator
        self.card_recent = ctk.CTkFrame(self.frame_metrics, fg_color="#2d2d2d", width=260, height=70)
        self.card_recent.pack(side="right", padx=8, pady=10)
        ctk.CTkLabel(self.card_recent, text="RECENT BALLS", font=("Arial", 9), text_color="#888").pack(anchor="w", padx=8, pady=2)
        
        balls_frame = ctk.CTkFrame(self.card_recent, fg_color="transparent")
        balls_frame.pack(anchor="w", padx=8)
        for b in ["4", "1", "1", "2", "3", "W"]:
            color = "#cc0000" if b == "W" else "#007acc"
            lbl_b = ctk.CTkButton(balls_frame, text=b, width=26, height=26, fg_color=color, corner_radius=13, font=("Arial", 9, "bold"))
            lbl_b.pack(side="left", padx=2)

        # --- 3. MAIN DASHBOARD CONTENT AREA ---
        self.frame_main = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_main.pack(fill="both", expand=True, padx=10, pady=5)
        
        # A. Left Panel: Scorecard Table & Player Management
        self.left_panel = ctk.CTkFrame(self.frame_main, width=440, fg_color="#1a1a1a")
        self.left_panel.pack(side="left", fill="y", padx=5)
        
        ctk.CTkLabel(self.left_panel, text="LIVE SCORECARDS & PLAYERS", font=("Arial", 12, "bold"), text_color="white").pack(anchor="w", padx=15, pady=8)
        
        # Professional Structured Table Box
        table_frame = ctk.CTkFrame(self.left_panel, fg_color="#252526", corner_radius=8)
        table_frame.pack(padx=15, pady=5, fill="x")
        
        h_frame = ctk.CTkFrame(table_frame, fg_color="#333333", height=30)
        h_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(h_frame, text="BATTERS", font=("Arial", 9, "bold"), text_color="white", width=140, anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(h_frame, text="R", font=("Arial", 9, "bold"), text_color="#00ffcc", width=35).pack(side="left")
        ctk.CTkLabel(h_frame, text="B", font=("Arial", 9, "bold"), text_color="#ccc", width=35).pack(side="left")
        ctk.CTkLabel(h_frame, text="4s", font=("Arial", 9, "bold"), text_color="#ccc", width=35).pack(side="left")
        ctk.CTkLabel(h_frame, text="6s", font=("Arial", 9, "bold"), text_color="#ccc", width=35).pack(side="left")

        b1_f = ctk.CTkFrame(table_frame, fg_color="transparent")
        b1_f.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(b1_f, text="> R. Harold (P)", font=("Arial", 9), text_color="#00ffcc", width=140, anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(b1_f, text="24", font=("Arial", 9), text_color="white", width=35).pack(side="left")
        ctk.CTkLabel(b1_f, text="18", font=("Arial", 9), text_color="white", width=35).pack(side="left")
        ctk.CTkLabel(b1_f, text="3", font=("Arial", 9), text_color="white", width=35).pack(side="left")
        ctk.CTkLabel(b1_f, text="1", font=("Arial", 9), text_color="white", width=35).pack(side="left")

        b2_f = ctk.CTkFrame(table_frame, fg_color="transparent")
        b2_f.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(b2_f, text="  Ravidu C.", font=("Arial", 9), text_color="white", width=140, anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(b2_f, text="16", font=("Arial", 9), text_color="white", width=35).pack(side="left")
        ctk.CTkLabel(b2_f, text="16", font=("Arial", 9), text_color="white", width=35).pack(side="left")
        ctk.CTkLabel(b2_f, text="1", font=("Arial", 9), text_color="white", width=35).pack(side="left")
        ctk.CTkLabel(b2_f, text="1", font=("Arial", 9), text_color="white", width=35).pack(side="left")

        bowl_f = ctk.CTkFrame(table_frame, fg_color="#2d2d2d", corner_radius=5)
        bowl_f.pack(fill="x", padx=5, pady=8)
        ctk.CTkLabel(bowl_f, text="Bowler: T. Guruge (2.4-0-18-1 | Econ: 6.75)", font=("Arial", 9, "bold"), text_color="#ffcc00").pack(anchor="w", padx=8, pady=5)

        # Player Management Section
        ctk.CTkLabel(self.left_panel, text="PLAYER MANAGEMENT", font=("Arial", 11, "bold"), text_color="#ffcc00").pack(anchor="w", padx=15, pady=10)
        
        self.entry_new_batter = ctk.CTkEntry(self.left_panel, placeholder_text="Enter New Batsman Name (On Wicket)", width=410)
        self.entry_new_batter.pack(padx=15, pady=5)

        self.combo_bowler = ctk.CTkComboBox(self.left_panel, values=["Select New Bowler", "T. Gamage", "S. Kavin", "M. Theekshana"], width=410)
        self.combo_bowler.pack(padx=15, pady=5)

        # B. Center Panel: Wagon Wheel & Pitch Map with Over/Around Wicket Options
        self.center_panel = ctk.CTkFrame(self.frame_main, fg_color="#1a1a1a")
        self.center_panel.pack(side="left", fill="both", expand=True, padx=5)
        
        ctk.CTkLabel(self.center_panel, text="PITCH & GROUND MAPPING SYSTEM", font=("Arial", 12, "bold"), text_color="white").pack(pady=10)
        
        maps_sub = ctk.CTkFrame(self.center_panel, fg_color="transparent")
        maps_sub.pack(expand=True)
        
        # 1. Wagon Wheel Canvas
        wagon_frame = ctk.CTkFrame(maps_sub, fg_color="#1a1a1a")
        wagon_frame.pack(side="left", padx=15)
        ctk.CTkLabel(wagon_frame, text="WAGON WHEEL (SHOT DIRECTION)", font=("Arial", 9, "bold"), text_color="#00ffcc").pack(pady=2)
        
        self.canvas_wagon = ctk.CTkCanvas(wagon_frame, width=280, height=280, bg="#1e3a1e", highlightthickness=1, highlightbackground="#444")
        self.canvas_wagon.pack()
        self.canvas_wagon.create_oval(15, 15, 265, 265, outline="white", width=2)
        self.canvas_wagon.create_oval(85, 85, 195, 195, outline="white", width=1, dash=(3,3))
        self.canvas_wagon.create_rectangle(130, 110, 150, 170, fill="#c2b280", outline="white")
        self.canvas_wagon.create_line(140, 115, 140, 165, fill="black", width=2)

        # 2. Pitch Map Canvas & Over/Around Wicket Selection
        pitch_frame = ctk.CTkFrame(maps_sub, fg_color="#1a1a1a")
        pitch_frame.pack(side="left", padx=15)
        ctk.CTkLabel(pitch_frame, text="PITCH MAP & BOWLING SIDE", font=("Arial", 9, "bold"), text_color="#ffcc00").pack(pady=2)
        
        self.canvas_pitch = ctk.CTkCanvas(pitch_frame, width=180, height=230, bg="#d4c596", highlightthickness=1, highlightbackground="#444")
        self.canvas_pitch.pack()
        self.canvas_pitch.create_rectangle(30, 10, 150, 60, fill="#ff9999", outline="#333") # Short
        self.canvas_pitch.create_rectangle(30, 60, 150, 110, fill="#ffcc66", outline="#333") # Good Length
        self.canvas_pitch.create_rectangle(30, 110, 150, 160, fill="#66b3ff", outline="#333") # Full Length
        self.canvas_pitch.create_rectangle(30, 160, 150, 210, fill="#99ff99", outline="#333") # Yorker
        self.canvas_pitch.create_rectangle(75, 185, 105, 210, fill="#ffffff", outline="black")

        # Over/Around Wicket Options
        side_frame = ctk.CTkFrame(pitch_frame, fg_color="transparent")
        side_frame.pack(pady=8)
        
        self.var_side = ctk.StringVar(value="Over")
        self.rb_over = ctk.CTkRadioButton(side_frame, text="Over the Wicket", variable=self.var_side, value="Over", font=("Arial", 9))
        self.rb_over.pack(side="left", padx=5)
        
        self.rb_around = ctk.CTkRadioButton(side_frame, text="Around the Wicket", variable=self.var_side, value="Around", font=("Arial", 9))
        self.rb_around.pack(side="left", padx=5)

        # C. Right Panel: Tagging, Wicket Type & Fielder Position
        self.right_panel = ctk.CTkFrame(self.frame_main, width=380, fg_color="#1a1a1a")
        self.right_panel.pack(side="right", fill="y", padx=5)
        
        ctk.CTkLabel(self.right_panel, text="BALL TAGGING & WICKET INFO", font=("Arial", 12, "bold"), text_color="white").pack(anchor="w", padx=15, pady=10)
        
        # Runs Buttons (0 to 10)
        ctk.CTkLabel(self.right_panel, text="SELECT RUNS (0 to 10):", font=("Arial", 10, "bold"), text_color="#00ffcc").pack(anchor="w", padx=15, pady=2)
        runs_grid = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        runs_grid.pack(padx=15, pady=5)
        for i, r in enumerate(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]):
            ctk.CTkButton(runs_grid, text=r, width=45, height=32, fg_color="#007acc", font=("Arial", 10, "bold")).grid(row=i//4, column=i%4, padx=3, pady=3)

        # Shot Type List
        ctk.CTkLabel(self.right_panel, text="SELECT SHOT TYPE:", font=("Arial", 10, "bold"), text_color="#ccc").pack(anchor="w", padx=15, pady=5)
        modern_shots = ["Cover Drive", "Straight Drive", "Pull Shot", "Sweep", "Reverse Sweep", "Hook Shot", "Scoop Shot", "Cut Shot", "Defensive Push"]
        self.combo_shot = ctk.CTkComboBox(self.right_panel, values=modern_shots, width=350)
        self.combo_shot.pack(padx=15, pady=2)
        
        # Wicket Type
        ctk.CTkLabel(self.right_panel, text="WICKET TYPE:", font=("Arial", 10, "bold"), text_color="#ff6666").pack(anchor="w", padx=15, pady=5)
        self.combo_out = ctk.CTkComboBox(self.right_panel, values=["None", "Caught", "Bowled", "LBW", "Run Out", "Stumped", "Hit Wicket"], width=350)
        self.combo_out.pack(padx=15, pady=2)

        # Fielder / Position
        ctk.CTkLabel(self.right_panel, text="FIELDER / POSITION (If Out):", font=("Arial", 10, "bold"), text_color="#ffcc00").pack(anchor="w", padx=15, pady=5)
        self.combo_fielder = ctk.CTkComboBox(self.right_panel, values=["Select Fielder Position", "Wicket Keeper", "Slip", "Gully", "Point", "Cover", "Mid Off", "Mid On", "Square Leg", "Long Off", "Long On"], width=350)
        self.combo_fielder.pack(padx=15, pady=2)

        # Save Button
        self.btn_save = ctk.CTkButton(self.right_panel, text="💾 SAVE BALL & TRIM CLIP", fg_color="#00b33c", hover_color="#00802b", height=45, font=("Arial", 12, "bold"))
        self.btn_save.pack(fill="x", padx=15, pady=15)

if __name__ == "__main__":
    app = CricAnalyticsApp()
    app.mainloop()