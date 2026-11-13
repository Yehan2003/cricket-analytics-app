import os
import json
import sqlite3
import cv2
from datetime import datetime
from PIL import Image, ImageTk
import customtkinter as ctk
from tkinter import messagebox, ttk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- 1. SYSTEM BASE DIRECTORY SETUP ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MATCHES_DIR = os.path.join(BASE_DIR, "matches")
os.makedirs(MATCHES_DIR, exist_ok=True)

def init_system(db_path):
    """Initialize database for the specific match"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS ball_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        inning INTEGER,
                        over_ball TEXT,
                        batsman TEXT,
                        bowler TEXT,
                        runs INTEGER,
                        extras_type TEXT,
                        shot_type TEXT,
                        wicket_type TEXT,
                        fielder TEXT,
                        ball_height TEXT,
                        bowling_side TEXT,
                        wagon_x REAL,
                        wagon_y REAL,
                        pitch_x REAL,
                        pitch_y REAL,
                        clip_path TEXT
                    )''')
    conn.commit()
    conn.close()

def safe_name(value):
    """Sanitize string values for folder naming"""
    value = value.strip()
    return "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in value).replace(" ", "_")

def create_match_folder(team1, team2, venue, match_format):
    """Create dedicated match directory, info file, and database"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{timestamp}_{safe_name(team1)}_vs_{safe_name(team2)}"
    match_dir = os.path.join(MATCHES_DIR, folder_name)
    os.makedirs(match_dir, exist_ok=True)

    # Create sub-folders for 4 innings (Supports Test matches)
    for inning_number in range(1, 5):
        os.makedirs(os.path.join(match_dir, f"inning_{inning_number}"), exist_ok=True)

    db_path = os.path.join(match_dir, "match_analytics.db")

    match_info = {
        "team1": team1,
        "team2": team2,
        "venue": venue,
        "format": match_format,
        "created_at": timestamp
    }

    with open(os.path.join(match_dir, "match_info.json"), "w", encoding="utf-8") as file:
        json.dump(match_info, file, indent=4)

    init_system(db_path)
    return match_dir, db_path

# ==========================================================
# WINDOW 3: COMPREHENSIVE MULTI-INNING SMART REPORT
# ==========================================================
def open_report_window(parent, db_path):
    if hasattr(parent, "report_win") and parent.report_win.winfo_exists():
        parent.report_win.focus()
        return

    parent.report_win = ctk.CTkToplevel(parent)
    parent.report_win.title("Comprehensive Multi-Inning Match & Visual Analytics Report")
    parent.report_win.geometry("1550x980")
    
    main_frame = ctk.CTkFrame(parent.report_win, fg_color="#1a1a1a")
    main_frame.pack(fill="both", expand=True, padx=15, pady=15)
    
    ctk.CTkLabel(main_frame, text="📊 COMPREHENSIVE MULTI-INNING MATCH & VISUAL ANALYTICS REPORT", font=("Arial", 18, "bold"), text_color="#00ffcc").pack(pady=10)
    
    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    existing_innings = [1, 2, 3, 4]

    for inn in existing_innings:
        tab_frame = ctk.CTkFrame(notebook, fg_color="#222222")
        notebook.add(tab_frame, text=f"   🏏 INNING {inn} REPORT   ")
        
        scroll_tab = ctk.CTkScrollableFrame(tab_frame, fg_color="#222222")
        scroll_tab.pack(fill="both", expand=True, padx=5, pady=5)
        
        # --- BATTING SECTION ---
        ctk.CTkLabel(scroll_tab, text=f"🔥 Inning {inn}: Batting Scorecard & Smart Insights", font=("Arial", 14, "bold"), text_color="#ffcc00").pack(anchor="w", padx=15, pady=(10, 5))
        
        bat_frame = ctk.CTkFrame(scroll_tab, fg_color="#2b2b2b", height=160)
        bat_frame.pack(fill="x", padx=15, pady=5)
        
        bat_tree = ttk.Treeview(bat_frame, columns=("Batter", "Runs", "Balls", "Dots", "4s", "6s", "SR", "FavShot"), show="headings", height=4)
        bat_tree.heading("Batter", text="Batsman Name")
        bat_tree.heading("Runs", text="Runs")
        bat_tree.heading("Balls", text="Balls")
        bat_tree.heading("Dots", text="Dots")
        bat_tree.heading("4s", text="4s")
        bat_tree.heading("6s", text="6s")
        bat_tree.heading("SR", text="SR")
        bat_tree.heading("FavShot", text="Most Played Shot")
        bat_tree.pack(fill="both", expand=True, padx=8, pady=8)

        cursor.execute("""
            SELECT batsman, SUM(runs), COUNT(id), 
                   SUM(CASE WHEN runs=0 THEN 1 ELSE 0 END),
                   SUM(CASE WHEN runs=4 THEN 1 ELSE 0 END), 
                   SUM(CASE WHEN runs=6 THEN 1 ELSE 0 END)
            FROM ball_logs WHERE inning=? GROUP BY batsman
        """, (inn,))
        for r in cursor.fetchall():
            b_name = r[0]
            runs, balls, dots = r[1], r[2], r[3]
            sr = round((runs / balls) * 100, 2) if balls > 0 else 0.0
            
            cursor.execute("SELECT shot_type, COUNT(*) as cnt FROM ball_logs WHERE inning=? AND batsman=? GROUP BY shot_type ORDER BY cnt DESC LIMIT 1", (inn, b_name))
            shot_res = cursor.fetchone()
            fav_shot = shot_res[0] if shot_res else "Standard Play"
            bat_tree.insert("", "end", values=(b_name, runs, balls, dots, r[4], r[5], sr, fav_shot))

        # --- BOWLING SECTION ---
        ctk.CTkLabel(scroll_tab, text=f"🛡️ Inning {inn}: Bowling Figures & Pitch Analysis", font=("Arial", 14, "bold"), text_color="#00bfff").pack(anchor="w", padx=15, pady=(15, 5))
        
        bowl_frame = ctk.CTkFrame(scroll_tab, fg_color="#2b2b2b", height=160)
        bowl_frame.pack(fill="x", padx=15, pady=5)
        
        bowl_tree = ttk.Treeview(bowl_frame, columns=("Bowler", "Balls", "Runs", "Wickets", "Econ", "PitchZone"), show="headings", height=4)
        bowl_tree.heading("Bowler", text="Bowler Name")
        bowl_tree.heading("Balls", text="Balls")
        bowl_tree.heading("Runs", text="Runs Conceded")
        bowl_tree.heading("Wickets", text="Wickets")
        bowl_tree.heading("Econ", text="Economy")
        bowl_tree.heading("PitchZone", text="Primary Pitch Zone")
        bowl_tree.pack(fill="both", expand=True, padx=8, pady=8)

        cursor.execute("""
            SELECT bowler, COUNT(id), SUM(runs), 
                   SUM(CASE WHEN wicket_type NOT IN ('None', 'Run Out') THEN 1 ELSE 0 END)
            FROM ball_logs WHERE inning=? GROUP BY bowler
        """, (inn,))
        for r in cursor.fetchall():
            bowl_name = r[0]
            balls_bowled, runs_given = r[1], r[2]
            overs = balls_bowled / 6.0
            econ = round(runs_given / overs, 2) if overs > 0 else 0.0
            
            cursor.execute("SELECT AVG(pitch_y) FROM ball_logs WHERE inning=? AND bowler=?", (inn, bowl_name))
            py_res = cursor.fetchone()
            avg_py = py_res[0] if py_res and py_res[0] else 100
            
            if avg_py < 50: pitch_zone = "Full Length / Yorker"
            elif avg_py < 110: pitch_zone = "Good Length Area"
            else: pitch_zone = "Short / Back of Length"
                
            bowl_tree.insert("", "end", values=(bowl_name, balls_bowled, runs_given, r[3], econ, pitch_zone))

        # --- VISUAL MAPPING SECTION ---
        ctk.CTkLabel(scroll_tab, text=f"📍 Inning {inn}: Visual Wagon Wheel & Pitch Map Analysis", font=("Arial", 14, "bold"), text_color="#ff6666").pack(anchor="w", padx=15, pady=(15, 5))
        
        maps_container = ctk.CTkFrame(scroll_tab, fg_color="#1f1f1f")
        maps_container.pack(fill="x", padx=15, pady=5)
        
        w_sub = ctk.CTkFrame(maps_container, fg_color="transparent")
        w_sub.pack(side="left", padx=40, pady=15)
        ctk.CTkLabel(w_sub, text="WAGON WHEEL SHOTS PLOT", font=("Arial", 11, "bold"), text_color="#00ffcc").pack(pady=4)
        canvas_w = ctk.CTkCanvas(w_sub, width=240, height=240, bg="#1e3a1e", highlightthickness=1, highlightbackground="#444")
        canvas_w.pack()
        
        canvas_w.create_oval(15, 15, 225, 225, outline="white", width=2)
        canvas_w.create_oval(65, 65, 175, 175, outline="white", width=1, dash=(3,3))
        canvas_w.create_rectangle(110, 90, 130, 150, fill="#c2b280", outline="white")
        
        cursor.execute("SELECT wagon_x, wagon_y, runs FROM ball_logs WHERE inning=?", (inn,))
        for wx, wy, r_val in cursor.fetchall():
            if wx and wy:
                color = "yellow" if r_val >= 4 else ("cyan" if r_val > 0 else "gray")
                canvas_w.create_line(120, 120, wx, wy, fill=color, width=1)
                canvas_w.create_oval(wx-3, wy-3, wx+3, wy+3, fill=color, outline="black")

        p_sub = ctk.CTkFrame(maps_container, fg_color="transparent")
        p_sub.pack(side="left", padx=40, pady=15)
        ctk.CTkLabel(p_sub, text="PITCH MAP ZONES PLOT", font=("Arial", 11, "bold"), text_color="#ffcc00").pack(pady=4)
        canvas_p = ctk.CTkCanvas(p_sub, width=160, height=210, bg="#d4c596", highlightthickness=1, highlightbackground="#444")
        canvas_p.pack()
        
        canvas_p.create_rectangle(15, 10, 145, 55, fill="#ff9999", outline="#333")
        canvas_p.create_rectangle(15, 55, 145, 105, fill="#ffcc66", outline="#333")
        canvas_p.create_rectangle(15, 105, 145, 155, fill="#66b3ff", outline="#333")
        canvas_p.create_rectangle(15, 155, 145, 200, fill="#99ff99", outline="#333")
        
        cursor.execute("SELECT pitch_x, pitch_y FROM ball_logs WHERE inning=?", (inn,))
        for px, py in cursor.fetchall():
            if px and py:
                canvas_p.create_oval(px-4, py-4, px+4, py+4, fill="red", outline="white", width=1)

    conn.close()

# ==========================================================
# WINDOW 2: COMMERCIAL PRO LIVE DASHBOARD
# ==========================================================
class LiveDashboard(ctk.CTkToplevel):
    def __init__(self, parent, match_data):
        super().__init__(parent)
        self.title("Cric Analytics - Commercial Pro Edition")
        self.geometry("1650x980")
        
        self.match_data = match_data
        self.match_dir = match_data["match_dir"]
        self.db_path = match_data["db_path"]
        self.max_innings = match_data["max_innings"]
        
        self.current_inning = 1  
        self.current_runs = 0
        self.current_wickets = 0
        self.current_balls = 0       
        self.total_deliveries = 0    
        self.extras_count = 0
        self.max_overs = match_data['max_overs']
        self.selected_runs = ctk.IntVar(value=0)
        self.active_extra_type = "None" 
        
        self.batsman_stats = {}
        self.bowler_stats = {}
        
        self.current_batting_squad = list(match_data['squad1'])
        self.bowling_squad = list(match_data['squad2'])
        
        self.wagon_coords = (140, 140)
        self.pitch_coords = (90, 115)
        self.recent_balls_history = []
        self.frame_buffer = []
        
        # --- 1. TOP HEADER BAR ---
        self.frame_top = ctk.CTkFrame(self, height=65, fg_color="#1a1a1a")
        self.frame_top.pack(fill="x", padx=10, pady=5)
        
        self.lbl_logo = ctk.CTkLabel(self.frame_top, text="🏏 CRIC ANALYTICS", font=("Arial", 14, "bold"), text_color="#00ffcc")
        self.lbl_logo.pack(side="left", padx=15)
        
        self.lbl_status = ctk.CTkLabel(self.frame_top, text="● INNING 1 LIVE", font=("Arial", 11, "bold"), text_color="#ff3333")
        self.lbl_status.pack(side="left", padx=5)

        self.btn_end_match = ctk.CTkButton(self.frame_top, text="🏁 END MATCH & REPORT", fg_color="#cc6600", hover_color="#994d00", width=180, height=32, font=("Arial", 10, "bold"), command=self.end_match_and_generate)
        self.btn_end_match.pack(side="left", padx=10)

        self.btn_switch_inning = ctk.CTkButton(self.frame_top, text="🔄 SWITCH INNING", fg_color="#007acc", hover_color="#005999", width=130, height=32, font=("Arial", 10, "bold"), command=self.toggle_inning)
        self.btn_switch_inning.pack(side="left", padx=10)

        self.btn_wicket = ctk.CTkButton(self.frame_top, text="WICKET", fg_color="#cc0000", hover_color="#990000", width=75, height=30, font=("Arial", 10, "bold"), command=lambda: self.set_wicket_action())
        self.btn_wicket.pack(side="right", padx=3)
        
        self.btn_legbye = ctk.CTkButton(self.frame_top, text="LEG BYE", fg_color="#3399ff", hover_color="#1a75ff", width=75, height=30, font=("Arial", 10, "bold"), command=lambda: self.set_extra("LegBye"))
        self.btn_legbye.pack(side="right", padx=3)

        self.btn_bye = ctk.CTkButton(self.frame_top, text="BYE", fg_color="#3399ff", hover_color="#1a75ff", width=60, height=30, font=("Arial", 10, "bold"), command=lambda: self.set_extra("Bye"))
        self.btn_bye.pack(side="right", padx=3)

        self.btn_noball = ctk.CTkButton(self.frame_top, text="NO BALL", fg_color="#ff3333", hover_color="#cc0000", width=75, height=30, font=("Arial", 10, "bold"), command=lambda: self.set_extra("NoBall"))
        self.btn_noball.pack(side="right", padx=3)

        self.btn_wide = ctk.CTkButton(self.frame_top, text="WIDE", fg_color="#ffcc00", text_color="black", hover_color="#cca300", width=65, height=30, font=("Arial", 10, "bold"), command=lambda: self.set_extra("Wide"))
        self.btn_wide.pack(side="right", padx=3)

        # --- 2. METRICS CARDS BAR ---
        self.frame_metrics = ctk.CTkFrame(self, height=80, fg_color="#1f1f1f")
        self.frame_metrics.pack(fill="x", padx=10, pady=3)
        
        self.card_runs = ctk.CTkFrame(self.frame_metrics, fg_color="#2d2d2d", width=150, height=60)
        self.card_runs.pack(side="left", padx=5, pady=8)
        ctk.CTkLabel(self.card_runs, text="RUNS / WICKETS", font=("Arial", 8), text_color="#888").pack(anchor="w", padx=6, pady=1)
        self.lbl_runs_val = ctk.CTkLabel(self.card_runs, text="0 / 0", font=("Arial", 14, "bold"), text_color="#00ffcc")
        self.lbl_runs_val.pack(anchor="w", padx=6)

        self.card_overs = ctk.CTkFrame(self.frame_metrics, fg_color="#2d2d2d", width=130, height=60)
        self.card_overs.pack(side="left", padx=5, pady=8)
        ctk.CTkLabel(self.card_overs, text="OVERS", font=("Arial", 8), text_color="#888").pack(anchor="w", padx=6, pady=1)
        self.lbl_overs_val = ctk.CTkLabel(self.card_overs, text=f"0.0 / {self.max_overs}", font=("Arial", 14, "bold"), text_color="white")
        self.lbl_overs_val.pack(anchor="w", padx=6)

        self.card_rrr = ctk.CTkFrame(self.frame_metrics, fg_color="#2d2d2d", width=130, height=60)
        self.card_rrr.pack(side="left", padx=5, pady=8)
        ctk.CTkLabel(self.card_rrr, text="RUN RATE", font=("Arial", 8), text_color="#888").pack(anchor="w", padx=6, pady=1)
        self.lbl_rr_val = ctk.CTkLabel(self.card_rrr, text="0.00", font=("Arial", 14, "bold"), text_color="#ffcc00")
        self.lbl_rr_val.pack(anchor="w", padx=6)

        self.card_pp = ctk.CTkFrame(self.frame_metrics, fg_color="#2d2d2d", width=130, height=60)
        self.card_pp.pack(side="left", padx=5, pady=8)
        ctk.CTkLabel(self.card_pp, text="POWERPLAY", font=("Arial", 8), text_color="#888").pack(anchor="w", padx=6, pady=1)
        ctk.CTkLabel(self.card_pp, text="PP 1 (1-6)", font=("Arial", 14, "bold"), text_color="#00bfff").pack(anchor="w", padx=6)

        self.card_extras = ctk.CTkFrame(self.frame_metrics, fg_color="#2d2d2d", width=110, height=60)
        self.card_extras.pack(side="left", padx=5, pady=8)
        ctk.CTkLabel(self.card_extras, text="EXTRAS", font=("Arial", 8), text_color="#888").pack(anchor="w", padx=6, pady=1)
        self.lbl_extras_val = ctk.CTkLabel(self.card_extras, text="0", font=("Arial", 12, "bold"), text_color="#ff9999")
        self.lbl_extras_val.pack(anchor="w", padx=6)

        self.card_recent_over = ctk.CTkFrame(self.frame_metrics, fg_color="#2d2d2d", width=260, height=60)
        self.card_recent_over.pack(side="right", padx=5, pady=8)
        ctk.CTkLabel(self.card_recent_over, text="CURRENT OVER (BALL-BY-BALL)", font=("Arial", 9, "bold"), text_color="#ffcc00").pack(anchor="w", padx=6, pady=1)
        
        self.dots_sub_container = ctk.CTkFrame(self.card_recent_over, fg_color="transparent")
        self.dots_sub_container.pack(anchor="w", padx=6, pady=2)
        self.update_mini_dots_ui("-")

        # --- 3. MAIN DASHBOARD CONTENT AREA ---
        self.frame_main = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_main.pack(fill="both", expand=True, padx=10, pady=3)
        
        # Left Panel
        self.left_panel = ctk.CTkFrame(self.frame_main, width=440, fg_color="#1a1a1a")
        self.left_panel.pack(side="left", fill="y", padx=5)
        
        ctk.CTkLabel(self.left_panel, text="LIVE SCORECARDS & PLAYERS", font=("Arial", 13, "bold"), text_color="white").pack(anchor="w", padx=12, pady=6)
        
        table_frame = ctk.CTkFrame(self.left_panel, fg_color="#252526", corner_radius=8)
        table_frame.pack(padx=12, pady=4, fill="x")
        
        h_frame = ctk.CTkFrame(table_frame, fg_color="#333333", height=32)
        h_frame.pack(fill="x", padx=4, pady=4)
        ctk.CTkLabel(h_frame, text="BATTERS", font=("Arial", 11, "bold"), text_color="white", width=130, anchor="w").pack(side="left", padx=4)
        ctk.CTkLabel(h_frame, text="R", font=("Arial", 11, "bold"), text_color="#00ffcc", width=30).pack(side="left")
        ctk.CTkLabel(h_frame, text="B", font=("Arial", 11, "bold"), text_color="#ccc", width=30).pack(side="left")
        ctk.CTkLabel(h_frame, text="4s", font=("Arial", 11, "bold"), text_color="#ccc", width=30).pack(side="left")
        ctk.CTkLabel(h_frame, text="6s", font=("Arial", 11, "bold"), text_color="#ccc", width=30).pack(side="left")

        b1_f = ctk.CTkFrame(table_frame, fg_color="transparent")
        b1_f.pack(fill="x", padx=4, pady=2)
        self.lbl_b1_name = ctk.CTkLabel(b1_f, text="> Striker", font=("Arial", 11, "bold"), text_color="#00ffcc", width=130, anchor="w")
        self.lbl_b1_name.pack(side="left", padx=4)
        self.lbl_b1_r = ctk.CTkLabel(b1_f, text="0", font=("Arial", 11, "bold"), text_color="white", width=30)
        self.lbl_b1_r.pack(side="left")
        self.lbl_b1_b = ctk.CTkLabel(b1_f, text="0", font=("Arial", 11, "bold"), text_color="white", width=30)
        self.lbl_b1_b.pack(side="left")
        self.lbl_b1_4s = ctk.CTkLabel(b1_f, text="0", font=("Arial", 11), text_color="white", width=30)
        self.lbl_b1_4s.pack(side="left")
        self.lbl_b1_6s = ctk.CTkLabel(b1_f, text="0", font=("Arial", 11), text_color="white", width=30)
        self.lbl_b1_6s.pack(side="left")

        b2_f = ctk.CTkFrame(table_frame, fg_color="transparent")
        b2_f.pack(fill="x", padx=4, pady=2)
        self.lbl_b2_name = ctk.CTkLabel(b2_f, text="  Non-Striker", font=("Arial", 11), text_color="white", width=130, anchor="w")
        self.lbl_b2_name.pack(side="left", padx=4)
        self.lbl_b2_r = ctk.CTkLabel(b2_f, text="0", font=("Arial", 11), text_color="white", width=30)
        self.lbl_b2_r.pack(side="left")
        self.lbl_b2_b = ctk.CTkLabel(b2_f, text="0", font=("Arial", 11), text_color="white", width=30)
        self.lbl_b2_b.pack(side="left")
        self.lbl_b2_4s = ctk.CTkLabel(b2_f, text="0", font=("Arial", 11), text_color="white", width=30)
        self.lbl_b2_4s.pack(side="left")
        self.lbl_b2_6s = ctk.CTkLabel(b2_f, text="0", font=("Arial", 11), text_color="white", width=30)
        self.lbl_b2_6s.pack(side="left")

        bowl_f = ctk.CTkFrame(table_frame, fg_color="#2d2d2d", corner_radius=5)
        bowl_f.pack(fill="x", padx=4, pady=6)
        self.lbl_bowler_stats = ctk.CTkLabel(bowl_f, text="Bowler: - (0.0-0-0-0 | Econ: 0.00)", font=("Arial", 11, "bold"), text_color="#ffcc00")
        self.lbl_bowler_stats.pack(anchor="w", padx=8, pady=6)

        ctk.CTkLabel(self.left_panel, text="PLAYER SQUAD MANAGEMENT", font=("Arial", 12, "bold"), text_color="#ffcc00").pack(anchor="w", padx=12, pady=6)
        
        ctk.CTkLabel(self.left_panel, text="Select Striker:", font=("Arial", 10, "bold"), text_color="#ccc").pack(anchor="w", padx=12)
        self.combo_striker = ctk.CTkComboBox(self.left_panel, values=self.current_batting_squad, width=410, height=28, font=("Arial", 11), command=lambda x: self.update_crease_labels())
        self.combo_striker.pack(padx=12, pady=2)
        if self.current_batting_squad: self.combo_striker.set(self.current_batting_squad[0])

        ctk.CTkLabel(self.left_panel, text="Select Non-Striker:", font=("Arial", 10, "bold"), text_color="#ccc").pack(anchor="w", padx=12)
        self.combo_non_striker = ctk.CTkComboBox(self.left_panel, values=self.current_batting_squad, width=410, height=28, font=("Arial", 11), command=lambda x: self.update_crease_labels())
        self.combo_non_striker.pack(padx=12, pady=2)
        if len(self.current_batting_squad) > 1: self.combo_non_striker.set(self.current_batting_squad[1])

        ctk.CTkLabel(self.left_panel, text="Select Bowler:", font=("Arial", 10, "bold"), text_color="#ccc").pack(anchor="w", padx=12)
        self.combo_bowler = ctk.CTkComboBox(self.left_panel, values=self.bowling_squad, width=410, height=28, font=("Arial", 11), command=lambda x: self.update_crease_labels())
        self.combo_bowler.pack(padx=12, pady=2)
        if self.bowling_squad: self.combo_bowler.set(self.bowling_squad[0])

        # Center Panel
        self.center_panel = ctk.CTkFrame(self.frame_main, fg_color="#1a1a1a")
        self.center_panel.pack(side="left", fill="both", expand=True, padx=5)
        
        ctk.CTkLabel(self.center_panel, text="PITCH & GROUND MAPPING SYSTEM (Click on Maps to Mark)", font=("Arial", 11, "bold"), text_color="white").pack(pady=4)
        
        maps_sub = ctk.CTkFrame(self.center_panel, fg_color="transparent")
        maps_sub.pack(pady=2)
        
        wagon_frame = ctk.CTkFrame(maps_sub, fg_color="#1a1a1a")
        wagon_frame.pack(side="left", padx=10)
        ctk.CTkLabel(wagon_frame, text="WAGON WHEEL", font=("Arial", 9, "bold"), text_color="#00ffcc").pack(pady=2)
        
        self.canvas_wagon = ctk.CTkCanvas(wagon_frame, width=240, height=240, bg="#1e3a1e", highlightthickness=1, highlightbackground="#444")
        self.canvas_wagon.pack()
        self.draw_wagon_ground()
        self.canvas_wagon.bind("<Button-1>", self.on_wagon_click)

        pitch_frame = ctk.CTkFrame(maps_sub, fg_color="#1a1a1a")
        pitch_frame.pack(side="left", padx=10)
        ctk.CTkLabel(pitch_frame, text="PITCH MAP", font=("Arial", 9, "bold"), text_color="#ffcc00").pack(pady=2)
        
        self.canvas_pitch = ctk.CTkCanvas(pitch_frame, width=150, height=190, bg="#d4c596", highlightthickness=1, highlightbackground="#444")
        self.canvas_pitch.pack()
        self.draw_pitch_zones()
        self.canvas_pitch.bind("<Button-1>", self.on_pitch_click)

        side_frame = ctk.CTkFrame(pitch_frame, fg_color="transparent")
        side_frame.pack(pady=2)
        self.var_side = ctk.StringVar(value="Over")
        ctk.CTkRadioButton(side_frame, text="Over", variable=self.var_side, value="Over", font=("Arial", 8)).pack(side="left", padx=3)
        ctk.CTkRadioButton(side_frame, text="Around", variable=self.var_side, value="Around", font=("Arial", 8)).pack(side="left", padx=3)

        video_outer = ctk.CTkFrame(self.center_panel, fg_color="#141414", corner_radius=6)
        video_outer.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.lbl_active_extra = ctk.CTkLabel(video_outer, text="📹 Active Mode: Normal Delivery (Live Webcam Feed)", font=("Arial", 10, "bold"), text_color="#00ffcc")
        self.lbl_active_extra.pack(anchor="w", padx=8, pady=(2, 0))
        
        self.frame_video = ctk.CTkFrame(video_outer, fg_color="black", corner_radius=4)
        self.frame_video.pack(fill="both", expand=True, padx=8, pady=2)
        self.frame_video.pack_propagate(False)

        # Right Panel
        self.right_panel = ctk.CTkFrame(self.frame_main, width=360, fg_color="#1a1a1a")
        self.right_panel.pack(side="right", fill="y", padx=5)
        
        ctk.CTkLabel(self.right_panel, text="BALL TAGGING & WICKET INFO", font=("Arial", 11, "bold"), text_color="white").pack(anchor="w", padx=12, pady=8)
        
        ctk.CTkLabel(self.right_panel, text="SELECT RUNS (0 to 10):", font=("Arial", 9, "bold"), text_color="#00ffcc").pack(anchor="w", padx=12, pady=2)
        runs_grid = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        runs_grid.pack(padx=12, pady=4)
        for i, r in enumerate(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]):
            btn = ctk.CTkButton(runs_grid, text=r, width=42, height=28, fg_color="#007acc", font=("Arial", 9, "bold"),
                                command=lambda val=int(r): self.selected_runs.set(val))
            btn.grid(row=i//4, column=i%4, padx=2, pady=2)

        ctk.CTkLabel(self.right_panel, text="SELECT SHOT TYPE:", font=("Arial", 9, "bold"), text_color="#ccc").pack(anchor="w", padx=12, pady=4)
        modern_shots = ["Cover Drive", "Straight Drive", "Pull Shot", "Sweep", "Reverse Sweep", "Hook Shot", "Scoop Shot", "Cut Shot", "Defensive Push"]
        self.combo_shot = ctk.CTkComboBox(self.right_panel, values=modern_shots, width=330, height=26)
        self.combo_shot.pack(padx=12, pady=2)
        self.combo_shot.set("Cover Drive")
        
        ctk.CTkLabel(self.right_panel, text="WICKET TYPE:", font=("Arial", 9, "bold"), text_color="#ff6666").pack(anchor="w", padx=12, pady=4)
        self.combo_out = ctk.CTkComboBox(self.right_panel, values=["None", "Caught", "Bowled", "LBW", "Run Out", "Stumped", "Hit Wicket"], width=330, height=26)
        self.combo_out.pack(padx=12, pady=2)
        self.combo_out.set("None")

        ctk.CTkLabel(self.right_panel, text="FIELDER / POSITION (If Out):", font=("Arial", 9, "bold"), text_color="#ffcc00").pack(anchor="w", padx=12, pady=4)
        self.combo_fielder = ctk.CTkComboBox(self.right_panel, values=["Select Fielder Position", "Wicket Keeper", "Slip", "Gully", "Point", "Cover", "Mid Off", "Mid On", "Square Leg", "Long Off", "Long On"], width=330, height=26)
        self.combo_fielder.pack(padx=12, pady=2)
        self.combo_fielder.set("Select Fielder Position")

        ctk.CTkButton(self.right_panel, text="💾 SAVE BALL & TRIM CLIP", fg_color="#00b33c", hover_color="#00802b", height=40, font=("Arial", 11, "bold"), command=self.save_ball).pack(fill="x", padx=12, pady=10)

        self.update_crease_labels()
        self.start_webcam_stream()

    def start_webcam_stream(self):
        self.cap = cv2.VideoCapture(0)
        self.update_webcam_frame()

    def update_webcam_frame(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.frame_buffer.append(frame.copy())
                if len(self.frame_buffer) > 40:
                    self.frame_buffer.pop(0)

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb_frame)
                
                w = self.frame_video.winfo_width()
                h = self.frame_video.winfo_height()
                if w > 10 and h > 10:
                    img = img.resize((w, h))
                    
                imgtk = ImageTk.PhotoImage(image=img)
                
                if not hasattr(self, 'video_lbl'):
                    self.video_lbl = ctk.CTkLabel(self.frame_video, text="")
                    self.video_lbl.pack(fill="both", expand=True)
                    
                self.video_lbl.configure(image=imgtk)
                self.video_lbl.image = imgtk
                
        self.after(15, self.update_webcam_frame)

    def toggle_inning(self):
        if self.current_inning >= self.max_innings:
            messagebox.showinfo("Match Complete", f"මෙම {self.match_data['format']} match format එකේ සියලු innings අවසන්.")
            return

        self.current_inning += 1
        self.lbl_status.configure(text=f"● INNING {self.current_inning} LIVE")
        self.current_runs = 0
        self.current_wickets = 0
        self.current_balls = 0
        self.total_deliveries = 0
        self.extras_count = 0
        self.recent_balls_history = []
        
        # Swap Squads for Next Inning
        self.batsman_stats = {}
        self.bowler_stats = {}
        self.current_batting_squad, self.bowling_squad = self.bowling_squad, self.current_batting_squad

        self.combo_striker.configure(values=self.current_batting_squad)
        self.combo_non_striker.configure(values=self.current_batting_squad)
        self.combo_bowler.configure(values=self.bowling_squad)

        if self.current_batting_squad:
            self.combo_striker.set(self.current_batting_squad[0])
        if len(self.current_batting_squad) > 1:
            self.combo_non_striker.set(self.current_batting_squad[1])
        if self.bowling_squad:
            self.combo_bowler.set(self.bowling_squad[0])

        self.update_mini_dots_ui("-")
        self.update_crease_labels()

        messagebox.showinfo("Inning Switched", f"Inning {self.current_inning} ආරම්භ කළා.")

    def set_extra(self, extra_type):
        if self.active_extra_type == extra_type:
            self.active_extra_type = "None"
            self.lbl_active_extra.configure(text="📹 Active Mode: Normal Delivery", text_color="#00ffcc")
        else:
            self.active_extra_type = extra_type
            self.lbl_active_extra.configure(text=f"📹 Active Mode: {extra_type} Selected", text_color="#ffcc00")

    def set_wicket_action(self):
        self.combo_out.set("Bowled")

    def draw_wagon_ground(self):
        self.canvas_wagon.delete("all")
        self.canvas_wagon.create_oval(15, 15, 225, 225, outline="white", width=2)
        self.canvas_wagon.create_oval(65, 65, 175, 175, outline="white", width=1, dash=(3,3))
        self.canvas_wagon.create_rectangle(110, 90, 130, 150, fill="#c2b280", outline="white")
        wx, wy = self.wagon_coords
        self.canvas_wagon.create_line(120, 120, wx, wy, fill="#00ffcc", width=2)
        self.canvas_wagon.create_oval(wx-4, wy-4, wx+4, wy+4, fill="yellow", outline="black")

    def draw_pitch_zones(self):
        self.canvas_pitch.delete("all")
        self.canvas_pitch.create_rectangle(15, 10, 135, 50, fill="#ff9999", outline="#333")
        self.canvas_pitch.create_rectangle(15, 50, 135, 90, fill="#ffcc66", outline="#333")
        self.canvas_pitch.create_rectangle(15, 90, 135, 130, fill="#66b3ff", outline="#333")
        self.canvas_pitch.create_rectangle(15, 130, 135, 170, fill="#99ff99", outline="#333")
        px, py = self.pitch_coords
        self.canvas_pitch.create_oval(px-4, py-4, px+4, py+4, fill="red", outline="white", width=1)

    def on_wagon_click(self, event):
        self.wagon_coords = (event.x, event.y)
        self.draw_wagon_ground()

    def on_pitch_click(self, event):
        self.pitch_coords = (event.x, event.y)
        self.draw_pitch_zones()

    def update_crease_labels(self):
        s = self.combo_striker.get()
        ns = self.combo_non_striker.get()
        b = self.combo_bowler.get()
        
        if s not in self.batsman_stats: self.batsman_stats[s] = {'runs': 0, 'balls': 0, '4s': 0, '6s': 0}
        if ns not in self.batsman_stats: self.batsman_stats[ns] = {'runs': 0, 'balls': 0, '4s': 0, '6s': 0}
        if b not in self.bowler_stats: self.bowler_stats[b] = {'balls': 0, 'runs': 0, 'wickets': 0}
        
        s_data = self.batsman_stats[s]
        ns_data = self.batsman_stats[ns]
        b_data = self.bowler_stats[b]
        
        self.lbl_b1_name.configure(text=f"> {s} (P)")
        self.lbl_b1_r.configure(text=str(s_data['runs']))
        self.lbl_b1_b.configure(text=str(s_data['balls']))
        self.lbl_b1_4s.configure(text=str(s_data['4s']))
        self.lbl_b1_6s.configure(text=str(s_data['6s']))
        
        self.lbl_b2_name.configure(text=f"  {ns}")
        self.lbl_b2_r.configure(text=str(ns_data['runs']))
        self.lbl_b2_b.configure(text=str(ns_data['balls']))
        self.lbl_b2_4s.configure(text=str(ns_data['4s']))
        self.lbl_b2_6s.configure(text=str(ns_data['6s']))
        
        b_balls = b_data['balls']
        b_overs = f"{b_balls // 6}.{b_balls % 6}"
        total_overs_float = b_balls / 6.0
        econ = round(b_data['runs'] / total_overs_float, 2) if total_overs_float > 0 else 0.0
        
        self.lbl_bowler_stats.configure(text=f"Bowler: {b} ({b_overs}-{b_data['runs']}-{b_data['wickets']} | Econ: {econ})")

    def update_mini_dots_ui(self, ball_symbol):
        if ball_symbol != "-":
            self.recent_balls_history.append(ball_symbol)
            if len(self.recent_balls_history) > 6:
                self.recent_balls_history.pop(0)
            
        for widget in self.dots_sub_container.winfo_children():
            widget.destroy()
            
        display_list = self.recent_balls_history.copy()
        while len(display_list) < 6:
            display_list.append("•")
            
        for b in display_list:
            if b == "•":
                btn = ctk.CTkButton(self.dots_sub_container, text=b, width=22, height=22, fg_color="#333", text_color="#777", corner_radius=11, font=("Arial", 9, "bold"), state="disabled")
            else:
                color = "#cc0000" if b == "W" else ("#ffcc00" if b in ["WD", "NB"] else "#007acc")
                btn = ctk.CTkButton(self.dots_sub_container, text=b, width=22, height=22, fg_color=color, corner_radius=11, font=("Arial", 9, "bold"))
            btn.pack(side="left", padx=2)

    def save_ball(self):
        bat_runs = self.selected_runs.get()
        shot = self.combo_shot.get()
        wicket = self.combo_out.get()
        striker = self.combo_striker.get()
        non_striker = self.combo_non_striker.get()
        bowler = self.combo_bowler.get()
        bowling_side = self.var_side.get()
        extra_type = self.active_extra_type
        
        fielder = self.combo_fielder.get()
        if fielder == "Select Fielder Position":
            fielder = "None"

        ball_runs = bat_runs
        is_legal_delivery = True
        extra_runs_added = 0
        
        if extra_type in ["Wide", "NoBall"]:
            extra_runs_added = 1 + bat_runs  
            ball_runs = extra_runs_added
            self.extras_count += extra_runs_added
            is_legal_delivery = False  
        elif extra_type in ["Bye", "LegBye"]:
            extra_runs_added = bat_runs
            self.extras_count += extra_runs_added
            ball_runs = extra_runs_added
        else:
            self.current_runs += bat_runs
            
        if extra_type in ["Wide", "NoBall", "Bye", "LegBye"]:
            self.current_runs += extra_runs_added

        self.total_deliveries += 1
        
        if is_legal_delivery:
            self.current_balls += 1
            
        if wicket != "None":
            self.current_wickets += 1
            
        if striker not in self.batsman_stats: self.batsman_stats[striker] = {'runs': 0, 'balls': 0, '4s': 0, '6s': 0}
        if bowler not in self.bowler_stats: self.bowler_stats[bowler] = {'balls': 0, 'runs': 0, 'wickets': 0}
        
        if extra_type != "Wide":
            self.batsman_stats[striker]['balls'] += 1
            if extra_type not in ["Bye", "LegBye"]:
                self.batsman_stats[striker]['runs'] += bat_runs
                if bat_runs == 4: self.batsman_stats[striker]['4s'] += 1
                elif bat_runs == 6: self.batsman_stats[striker]['6s'] += 1
                
        self.bowler_stats[bowler]['balls'] += 1
        self.bowler_stats[bowler]['runs'] += ball_runs
        if wicket != "None":
            self.bowler_stats[bowler]['wickets'] += 1
            
        overs_val = f"{self.current_balls // 6}.{self.current_balls % 6}"
        
        # Save Video Clip into Inning Folder Structure
        inning_dir = os.path.join(self.match_dir, f"inning_{self.current_inning}")
        os.makedirs(inning_dir, exist_ok=True)
        clip_filename = os.path.join(inning_dir, f"ball_{self.total_deliveries}_{overs_val.replace('.', '_')}.mp4")
        
        if self.frame_buffer:
            h, w, _ = self.frame_buffer[0].shape
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(clip_filename, fourcc, 20.0, (w, h))
            for f in self.frame_buffer:
                out.write(f)
            out.release()
        
        if wicket != "None":
            ball_symbol = "W"
        elif extra_type == "Wide":
            ball_symbol = "WD"
        elif extra_type == "NoBall":
            ball_symbol = "NB"
        else:
            ball_symbol = str(bat_runs)
            
        self.update_mini_dots_ui(ball_symbol)
        
        # Write into match-specific DB
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ball_logs (inning, over_ball, batsman, bowler, runs, extras_type, shot_type, wicket_type, fielder, bowling_side, wagon_x, wagon_y, pitch_x, pitch_y, clip_path) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (self.current_inning, overs_val, striker, bowler, ball_runs, extra_type, shot, wicket, fielder, bowling_side, 
              self.wagon_coords[0], self.wagon_coords[1], self.pitch_coords[0], self.pitch_coords[1], clip_filename))
        conn.commit()
        conn.close()
        
        self.active_extra_type = "None"
        self.lbl_active_extra.configure(text="📹 Active Mode: Normal Delivery", text_color="#00ffcc")
        
        # Wicket handling logic
        if wicket != "None":
            if striker in self.current_batting_squad:
                self.current_batting_squad.remove(striker)
            
            self.combo_striker.configure(values=self.current_batting_squad)
            self.combo_non_striker.configure(values=self.current_batting_squad)
            
            if self.current_batting_squad:
                self.combo_striker.set(self.current_batting_squad[0])
                
            messagebox.showwarning("Wicket Fall!", f"Wicket down! '{striker}' is out and has been removed from the batting lineup. Please select the new incoming batsman.")

        self.combo_out.set("None")
        
        if bat_runs in [1, 3, 5, 7, 9] and extra_type not in ["Wide"] and wicket == "None":
            self.combo_striker.set(non_striker)
            self.combo_non_striker.set(striker)
            
        # Over complete logic
        if is_legal_delivery and self.current_balls > 0 and self.current_balls % 6 == 0:
            current_s = self.combo_striker.get()
            current_ns = self.combo_non_striker.get()
            self.combo_striker.set(current_ns)
            self.combo_non_striker.set(current_s)
            
            self.recent_balls_history = []
            self.update_mini_dots_ui("-")
            
            messagebox.showinfo("Over Complete!", "Over completed! Please select the new bowler for the upcoming over.")

        self.update_crease_labels()
        
        self.lbl_runs_val.configure(text=f"{self.current_runs} / {self.current_wickets}")
        self.lbl_overs_val.configure(text=f"{overs_val} / {self.max_overs}")
        self.lbl_extras_val.configure(text=str(self.extras_count))
        
        total_overs_decimal = (self.current_balls / 6.0) if self.current_balls > 0 else 0.1
        current_rr = round(self.current_runs / total_overs_decimal, 2)
        self.lbl_rr_val.configure(text=f"{current_rr}")
        
        messagebox.showinfo("Success & Video Saved", f"Inning {self.current_inning} Ball Saved!\nMP4 Video Recorded at:\n{clip_filename}")

    def end_match_and_generate(self):
        answer = messagebox.askyesno("End Match", "Are you sure you want to end the match and generate the analytics report?")
        if answer:
            if hasattr(self, "cap") and self.cap.isOpened():
                self.cap.release()
            messagebox.showinfo("Match Ended", "Match successfully completed! Opening your comprehensive analytics report.")
            open_report_window(self, self.db_path)


# ==========================================================
# WINDOW 1: MATCH SETUP & 11-PLAYER SQUADS (LAUNCHER)
# ==========================================================
class MatchSetupApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Cric Analytics - Match Setup & 11-Player Squads")
        self.geometry("750x780")
        
        ctk.CTkLabel(self, text="🏏 PROFESSIONAL MATCH SETUP & SQUADS", font=("Arial", 16, "bold"), text_color="#00ffcc").pack(pady=10)
        
        form_frame = ctk.CTkFrame(self, fg_color="#1a1a1a")
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(form_frame, text="Team 1 Name:", font=("Arial", 10, "bold")).pack(anchor="w", padx=15, pady=2)
        self.e_team1 = ctk.CTkEntry(form_frame, width=680); self.e_team1.pack(padx=15, pady=3); self.e_team1.insert(0, "Tamil Union CC")
        
        ctk.CTkLabel(form_frame, text="Team 2 Name:", font=("Arial", 10, "bold")).pack(anchor="w", padx=15, pady=2)
        self.e_team2 = ctk.CTkEntry(form_frame, width=680); self.e_team2.pack(padx=15, pady=3); self.e_team2.insert(0, "Galle Cricket Club")

        ctk.CTkLabel(form_frame, text="Venue:", font=("Arial", 10, "bold")).pack(anchor="w", padx=15, pady=2)
        self.e_venue = ctk.CTkEntry(form_frame, width=680); self.e_venue.pack(padx=15, pady=3); self.e_venue.insert(0, "Galle International Stadium")

        ctk.CTkLabel(form_frame, text="Match Format (Auto sets Overs):", font=("Arial", 10, "bold"), text_color="#ffcc00").pack(anchor="w", padx=15, pady=2)
        self.format_combo = ctk.CTkComboBox(form_frame, values=["T20 (20 Overs)", "ODI (50 Overs)", "Test Match (Unlimited)"], width=680)
        self.format_combo.pack(padx=15, pady=3)
        self.format_combo.set("T20 (20 Overs)")

        ctk.CTkLabel(form_frame, text="Team 1 Squad (11 Players comma-separated):", font=("Arial", 10, "bold"), text_color="#00ffcc").pack(anchor="w", padx=15, pady=2)
        self.e_squad1 = ctk.CTkEntry(form_frame, width=680)
        self.e_squad1.pack(padx=15, pady=3)
        self.e_squad1.insert(0, "Navod P., R. Harold, Ravidu C., K. Silva, D. Perera, S. Fernando, M. Bhanuka, T. Lakshan, C. Asalanka, V. Nuwan, D. Madushanka")

        ctk.CTkLabel(form_frame, text="Team 2 Squad (11 Players comma-separated):", font=("Arial", 10, "bold"), text_color="#00bfff").pack(anchor="w", padx=15, pady=2)
        self.e_squad2 = ctk.CTkEntry(form_frame, width=680)
        self.e_squad2.pack(padx=15, pady=3)
        self.e_squad2.insert(0, "T. Guruge, T. Gamage, S. Kavin, M. Theekshana, L. Sandakan, P. Madushan, K. Rajitha, A. Dananjaya, N. Pradeep, L. Kumara, M. Pathirana")

        self.btn_start_match = ctk.CTkButton(self, text="🏏 START MATCH", fg_color="#28a745", hover_color="#218838", height=48, font=("Arial", 12, "bold"), command=self.launch_dashboard)
        self.btn_start_match.pack(pady=15)

    def launch_dashboard(self):
        team1 = self.e_team1.get().strip()
        team2 = self.e_team2.get().strip()
        venue = self.e_venue.get().strip()

        if not team1 or not team2:
            messagebox.showerror("Missing Information", "කරුණාකර කණ්ඩායම් දෙකේ නම් ඇතුළත් කරන්න.")
            return

        fmt = self.format_combo.get()

        if "Test" in fmt:
            max_overs = 999
            max_innings = 4
        elif "ODI" in fmt:
            max_overs = 50
            max_innings = 2
        else:
            max_overs = 20
            max_innings = 2

        squad1 = [p.strip() for p in self.e_squad1.get().split(",") if p.strip()]
        squad2 = [p.strip() for p in self.e_squad2.get().split(",") if p.strip()]

        if len(squad1) < 2 or len(squad2) < 1:
            messagebox.showerror("Invalid Squad", "අවම වශයෙන් Team 1 සඳහා ක්‍රීඩකයන් දෙදෙනෙකු සහ Team 2 සඳහා එක් ක්‍රීඩකයෙකු සිටිය යුතුය.")
            return

        match_dir, db_path = create_match_folder(team1, team2, venue, fmt)

        match_data = {
            "team1": team1,
            "team2": team2,
            "venue": venue,
            "format": fmt.split(" ")[0],
            "max_overs": max_overs,
            "max_innings": max_innings,
            "squad1": squad1,
            "squad2": squad2,
            "match_dir": match_dir,
            "db_path": db_path
        }

        self.withdraw()
        dashboard = LiveDashboard(self, match_data)
        dashboard.grab_set()

if __name__ == "__main__":
    app = MatchSetupApp()
    app.mainloop()