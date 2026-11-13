import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

# --- 1. LOCAL DATABASE SETUP ---
# මෙතනින් අපේ ලැප්ටොප් එක ඇතුළේ 'match_database.db' නමින් පුංචි ලෝකල් ඩේටාබේස් ෆයිල් එකක් හැදෙනවා.
def init_db():
    conn = sqlite3.connect("match_database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS match_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_a TEXT,
            team_b TEXT,
            ground TEXT,
            match_type TEXT,
            match_date TEXT,
            match_time TEXT
        )
    """)
    conn.commit()
    conn.close()

# --- 2. START MATCH BUTTON FUNCTION ---
# යූසර් විස්තර දීලා 'Start Match' බට්න් එක එබූ විට මේක ක්‍රියාත්මක වෙනවා.
def start_match():
    team_a = entry_team_a.get().strip()
    team_b = entry_team_b.get().strip()
    ground = entry_ground.get().strip()
    match_type = combo_type.get()
    match_date = entry_date.get().strip()
    match_time = entry_time.get().strip()
    
    # කෙනෙක් හිස් තැන් තියලා නම් අරන්ට් කරන්නේ, එයාට එරර් මැසේජ් එකක් පෙන්වනවා.
    if not team_a or not team_b or not ground or not match_date or not match_time:
        messagebox.showerror("Error", "කරුණාකර සියලුම විස්තර සම්පූර්ණ කරන්න!")
        return
    
    try:
        # ඩේටාබේස් එකට කනෙක්ට් වී ඩේටා සේව් කිරීම (Insert)
        conn = sqlite3.connect("match_database.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO match_details (team_a, team_b, ground, match_type, match_date, match_time)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (team_a, team_b, ground, match_type, match_date, match_time))
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Success", f"මැච් විස්තර සාර්ථකව ලෝකල් සේව් විය!\n\n{team_a} vs {team_b}\nగ్రවුන්ඩ් එක: {ground}")
        
        # මෙතැනදී තමයි ඉදිරියට ප්‍රධාන ඩෑෂ්බෝඩ් (Analysis Dashboard) වින්ඩෝ එක ඕපන් වෙන්න කෝඩ් එක ලියන්නේ.
        root.destroy() # දැනට මේ සෙටප් වින්ඩෝ එක වහලා දානවා
        
    except Exception as e:
        messagebox.showerror("Database Error", f"දෝෂයක් සිදු විය: {e}")

# --- 3. UI DESIGN (USER INTERFACE) ---
init_db() # ඇප් එක පටන් ගන්නකොටම ඩේටාබේස් එක චෙක් කරලා හදාගන්නවා

root = tk.Tk()
root.title("Cricket Performance Analysis - New Match Setup")
root.geometry("500x520")
root.config(bg="#f0f2f5")

# Heading Title
lbl_title = tk.Label(root, text="නව තරඟ ආරම්භක සැකසුම (Match Setup)", font=("Arial", 14, "bold"), bg="#f0f2f5", fg="#333")
lbl_title.pack(pady=15)

# Main Frame for Form Fields
frame_form = tk.Frame(root, bg="#f0f2f5")
frame_form.pack(pady=5)

# 1. Team A Name
tk.Label(frame_form, text="Team A Name:", font=("Arial", 11, "bold"), bg="#f0f2f5").pack(anchor="w", padx=20)
entry_team_a = tk.Entry(frame_form, font=("Arial", 11), width=38)
entry_team_a.pack(pady=5, padx=20)

# 2. Team B Name
tk.Label(frame_form, text="Team B Name:", font=("Arial", 11, "bold"), bg="#f0f2f5").pack(anchor="w", padx=20)
entry_team_b = tk.Entry(frame_form, font=("Arial", 11), width=38)
entry_team_b.pack(pady=5, padx=20)

# 3. Ground / Venue Name
tk.Label(frame_form, text="Ground / Venue Name:", font=("Arial", 11, "bold"), bg="#f0f2f5").pack(anchor="w", padx=20)
entry_ground = tk.Entry(frame_form, font=("Arial", 11), width=38)
entry_ground.pack(pady=5, padx=20)

# 4. Match Type (T20 / ODI)
tk.Label(frame_form, text="Match Type / Overs:", font=("Arial", 11, "bold"), bg="#f0f2f5").pack(anchor="w", padx=20)
combo_type = ttk.Combobox(frame_form, values=["T20 (20 Overs)", "ODI (50 Overs)", "Test", "Custom"], font=("Arial", 11), width=36)
combo_type.pack(pady=5, padx=20)
combo_type.current(0)

# 5. Match Date
tk.Label(frame_form, text="Match Date (YYYY-MM-DD):", font=("Arial", 11, "bold"), bg="#f0f2f5").pack(anchor="w", padx=20)
entry_date = tk.Entry(frame_form, font=("Arial", 11), width=38)
entry_date.pack(pady=5, padx=20)

# 6. Starting Time
tk.Label(frame_form, text="Starting Time:", font=("Arial", 11, "bold"), bg="#f0f2f5").pack(anchor="w", padx=20)
entry_time = tk.Entry(frame_form, font=("Arial", 11), width=38)
entry_time.pack(pady=5, padx=20)

# Start Match Button
btn_start = tk.Button(root, text="Start Match & Open Dashboard", font=("Arial", 12, "bold"), bg="#28a745", fg="white", width=30, command=start_match)
btn_start.pack(pady=20)

root.mainloop()