import requests
import pandas as pd
import json
from datetime import datetime
from database import get_connection

def insert_aus_draw(game_type, draw_date, numbers, bonus=None, powerball=None):
    """
    Inserts a single draw record into the 'aus_draws' table.
    """
    import sqlite3
    conn = get_connection()
    if not conn:
        return None
    numbers_str = ",".join(map(str, numbers))
    bonus_str = ",".join(map(str, bonus)) if bonus else None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(draw_id) FROM aus_draws")
        result = cursor.fetchone()
        max_draw_id = result[0] if result[0] is not None else 0
        new_draw_id = max_draw_id + 1

        sql = """
        INSERT INTO aus_draws (draw_id, game_type, draw_date, numbers, bonus, powerball)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql, (new_draw_id, game_type, draw_date, numbers_str, bonus_str, powerball))
        conn.commit()
        cursor.close()
        conn.close()
        return new_draw_id
    except sqlite3.IntegrityError as e:
        print(f"IntegrityError inserting aus_draw on {draw_date} for {game_type}: {e}")
        return None
    except Exception as e:
        print("Error inserting aus_draw:", e)
        return None


def fetch_all_aus_draws(game_type):
    """
    Fetches all draw records from the database for a specific game_type.
    """
    conn = get_connection()
    if not conn:
        return []
    draws_list = []
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT draw_date, numbers, bonus, powerball FROM aus_draws WHERE game_type = ? ORDER BY draw_date ASC",
            (game_type,)
        )
        rows = cursor.fetchall()
        for (draw_date, nums_str, bonus_str, powerball) in rows:
            try:
                num_list = list(map(int, nums_str.split(",")))
                bonus_list = list(map(int, bonus_str.split(","))) if bonus_str else []
            except ValueError:
                continue
            draws_list.append({
                "draw_date": draw_date,
                "numbers": num_list,
                "bonus": bonus_list,
                "powerball": powerball
            })
        cursor.close()
        conn.close()
        return draws_list
    except Exception as e:
        print("Error fetching aus_draws:", e)
        return []

def load_from_csv(file_path, game_type):
    try:
        df = pd.read_csv(file_path)
        num_cols = [c for c in df.columns if 'Number' in c or 'Main' in c or c.isdigit()]
        bonus_cols = [c for c in df.columns if 'Bonus' in c or 'Supp' in c]
        pb_col = [c for c in df.columns if 'Powerball' in c]

        count = 0
        for index, row in df.iterrows():
            date_str = str(row.get('Date', ''))
            if not date_str:
                continue
            try:
                date_obj = pd.to_datetime(date_str)
                date_formatted = date_obj.strftime("%Y-%m-%d")
            except:
                continue

            nums = [int(row[c]) for c in num_cols if pd.notnull(row[c])]
            bonus = [int(row[c]) for c in bonus_cols if pd.notnull(row[c])]
            pb = int(row[pb_col[0]]) if pb_col and pd.notnull(row[pb_col[0]]) else None

            if nums:
                res = insert_aus_draw(game_type, date_formatted, nums, bonus, pb)
                if res:
                    count += 1

        print(f"Successfully loaded {count} {game_type} draws from CSV.")
        return count
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return 0
