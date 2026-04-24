import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
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
    except sqlite3.IntegrityError:
        # Ignore duplicate insertions silently
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

def scrape_latest_results(game_type):
    """
    Scrapes the latest results from australia.national-lottery.com
    and inserts them into the local database.
    """
    game_urls = {
        'saturday': 'saturday-lotto',
        'oz': 'oz-lotto',
        'powerball': 'powerball'
    }

    if game_type not in game_urls:
        return 0

    url = f"https://australia.national-lottery.com/{game_urls[game_type]}/results"
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return 0

        soup = BeautifulSoup(response.content, 'html.parser')
        ball_lists = soup.find_all('ul', class_='balls')

        count = 0
        for ul in ball_lists:
            # We must be careful because some balls are main, some are bonus/powerball
            container = ul.parent
            date_a = container.find('a', href=re.compile(r'/results/\d{2}-\d{2}-\d{4}'))
            if not date_a:
                continue

            date_str_raw = date_a['href'].split('/')[-1]
            # Convert DD-MM-YYYY to YYYY-MM-DD
            try:
                date_obj = datetime.strptime(date_str_raw, "%d-%m-%Y")
                date_formatted = date_obj.strftime("%Y-%m-%d")
            except:
                continue

            main = []
            bonus = []
            pb = None

            for li in ul.find_all('li', class_='ball'):
                classes = li.get('class', [])
                try:
                    val = int(li.text.strip())
                except:
                    continue

                if 'powerball' in classes:
                    pb = val
                elif 'bonus' in classes or 'supp' in classes:
                    bonus.append(val)
                else:
                    main.append(val)

            # For Saturday Lotto, it is 6 main + 2 supps, but the site might just list them sequentially.
            # Usually the last balls are supplementary if not explicitly classed. Let's rely on classes if possible.
            # If classes didn't distinguish, we might need to slice them based on game_type.
            if game_type == 'saturday' and len(main) == 8 and len(bonus) == 0:
                bonus = main[-2:]
                main = main[:-2]
            elif game_type == 'oz' and len(main) == 10 and len(bonus) == 0:
                bonus = main[-3:]
                main = main[:-3]
            elif game_type == 'powerball' and pb is None and len(main) == 8:
                pb = main[-1]
                main = main[:-1]

            if main:
                res = insert_aus_draw(game_type, date_formatted, main, bonus, pb)
                if res:
                    count += 1

        return count
    except Exception as e:
        print(f"Scraping error: {e}")
        return 0

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
