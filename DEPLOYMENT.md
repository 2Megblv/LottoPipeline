# Australian Lotto Web App: Deployment & Usage Guide

## 1. System Requirements

*   **Operating System:** Windows, Linux, or macOS.
*   **Python Version:** Python 3.12 is *strictly* required to ensure compatibility with TensorFlow and Pennylane.
*   **Database:** SQLite3 installed on your system.

## 2. Environment Setup (Windows & Linux)

1.  **Clone the Repository (or Extract the Downloaded ZIP):**
    If you downloaded the `lotto_australia_deployment.zip` file, simply extract it and open your terminal inside the extracted folder. Alternatively, clone the main repository:
    ```bash
    git clone https://github.com/2Megblv/LottoPipeline.git
    cd LottoPipeline
    ```

2.  **Install the Required Dependencies:**
    Ensure you are using `pip` associated with Python 3.12.
    ```bash
    python3.12 -m pip install -r requirements.txt
    ```

3.  **Run the Application:**
    ```bash
    streamlit run app.py
    ```

## 3. Environment Setup (macOS Specific - Bulletproof Method)

macOS users often run into "externally-managed-environment" errors when trying to install global packages, and sometimes virtual environments fail to link `pip` correctly. To run this app successfully on a Mac, follow these explicit path-bound instructions.

1.  **Install Homebrew & Python 3.12:**
    Open Terminal and install Homebrew if you don't have it, then install Python 3.12.
    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    brew install python@3.12
    ```

2.  **Get the Code:**
    If you downloaded the `lotto_australia_deployment.zip` file, extract it and navigate into it using your terminal. Alternatively, clone it:
    ```bash
    git clone https://github.com/2Megblv/LottoPipeline.git
    cd LottoPipeline
    ```

3.  **Create the Virtual Environment:**
    ```bash
    python3.12 -m venv lotto_env
    ```

4.  **Install Dependencies (Using Absolute Paths):**
    To ensure packages are installed *strictly* into the new environment (and to avoid the "No module named streamlit" error), use the local environment's binary directly:
    ```bash
    ./lotto_env/bin/pip install -r requirements.txt
    ```

5.  **Running the Application:**
    Launch the app using the local environment's python binary. You do not even need to run `source activate` if you use this command:
    ```bash
    ./lotto_env/bin/python -m streamlit run app.py
    ```

This will automatically open a new tab in your default web browser pointing to `http://localhost:8501`.

## 4. How Data is Ingested

### Primary Method: Automated Web Scraping
The application is now equipped with an automated web scraper. Whenever you launch the app and click on a game tab (e.g., Saturday Lotto, Oz Lotto, or Powerball), the system will silently reach out to `australia.national-lottery.com` and scrape the latest official draw results. These results are automatically inserted into your local SQLite database, ensuring your machine learning models are always training on the most up-to-date data.

### Secondary Method: Manual CSV Upload (Fallback)
If the automated scraper fails due to website layout changes or network issues, you can still manually upload data.
1. Download the historical results for your target game as a CSV file.
2. Under the game header in the Streamlit UI, locate the **"Upload Historical CSV"** widget.
3. Drag and drop your CSV file. The application will parse it and insert any missing draws into the database.

## 5. Generating Tickets & Strategy Selection

Once you have at least 10 historical draws loaded, you can generate tickets.

1.  Check the **Lunar Phasing Module** on the sidebar. (Tip: Play during the "Full Moon Window" for optimal geomagnetic calm; skip "New Moon" days).
2.  Optionally enter your name in the **Chaldean Numerology** sidebar field to extract your personal vibration number (1-8).
3.  Select your **Strategy Configuration**:
    *   **Standard (Max 12 Games):** Generates up to 12 highly optimized standard games. This is the most cost-effective way to play.
    *   **System 8 (Wheel 8 Numbers):** Selects 8 main numbers instead of the standard 6 (or 7).
    *   **PowerHit (Powerball only):** Generates exactly 1 optimized 7-number line intended to be purchased with the guaranteed PowerHit add-on.
4.  Click **"Generate Tickets"**.

---

## 6. Strategy FAQ: System Entries vs. Standard Games

**Does Saturday Lotto have a System selection?**
Yes. In Australia, you can play a "System" entry for Saturday Lotto (which requires 6 winning numbers from 45). The Streamlit app supports **System 8** generation.

**Is it cheaper or higher odds to play a System game or a strict 12 Games?**
*   **Cost:** A strict 12-game standard entry is **significantly cheaper**. You are only paying for exactly 12 lines of 6 numbers. A System 8 entry in Saturday Lotto mathematically generates 28 unique 6-number combinations (because it wheels all possible 6-number combinations out of your 8 chosen numbers). Therefore, a System 8 ticket costs the equivalent of buying 28 standard games.
*   **Odds & Payouts:** A System 8 entry gives you **higher odds** of trapping the winning numbers, because you are covering 8 numbers out of the 45-number pool instead of just 6. Furthermore, because a System entry creates multiple combinations from those 8 numbers, if you manage to hit 4, 5, or 6 winning numbers within your pool of 8, you will win **multiple prizes across multiple divisions simultaneously** (e.g., winning Division 1 *plus* multiple Division 3 and 4 prizes).

**Conclusion:** Use **Standard (12 Games)** to strictly control your budget. Switch to **System 8** as your bankroll grows to drastically increase your odds of trapping numbers and multiplying your lower-division payouts.
