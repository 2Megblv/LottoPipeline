# Australian Lotto Web App: Deployment & Usage Guide

## 1. System Requirements

*   **Operating System:** Windows, Linux, or macOS.
*   **Python Version:** Python 3.12 is *strictly* required to ensure compatibility with TensorFlow and Pennylane.
*   **Database:** SQLite3 installed on your system.

## 2. Environment Setup

1.  **Clone the Repository (or navigate to the directory):**
    ```bash
    git clone https://gitlab.com/Callam7/LottoPipeline.git
    cd LottoPipeline
    ```

2.  **Install the Required Dependencies:**
    Ensure you are using `pip` associated with Python 3.12.
    ```bash
    python3.12 -m pip install -r requirements.txt
    ```
    *Note: The new web application relies on `streamlit` for the UI, `ephem` for lunar calculations, and `pandas` for data handling, which are all included in the updated requirements.*

3.  **Initialize the Database:**
    The SQLite database (`lotto.db`) is automatically initialized to include the Australian tables (`aus_draws`) the first time the ML pipeline is run or data is uploaded.

## 3. Running the Application

To launch the local web application dashboard, run the following command from the root of the project:

```bash
streamlit run app.py
```

This will automatically open a new tab in your default web browser pointing to `http://localhost:8501`.

## 4. How to Upload Historical Data

Due to anti-scraping protections on official lottery websites, the app is designed to securely ingest historical draw data manually via CSV files.

### Step 1: Obtain the Data
Download the historical results for your target game (Saturday Lotto, Oz Lotto, or Powerball) as a CSV file from the official lottery website or a trusted third-party statistics site.

### Step 2: Verify the CSV Format
Ensure your CSV file contains columns that the app can interpret. The app's generic parser looks for:
*   A date column containing the word `Date`.
*   Main number columns containing words like `Number`, `Main`, or just numeric digits.
*   Bonus/Supplementary columns containing `Bonus` or `Supp`.
*   A Powerball column containing `Powerball` (if applicable).

### Step 3: Upload via the Dashboard
1. Open the Streamlit web app in your browser.
2. Select the tab for the specific game you wish to play (e.g., "Oz Lotto (7/47)").
3. Under the game header, locate the **"Upload Historical CSV"** widget.
4. Drag and drop your downloaded CSV file into the widget, or click to browse your files.
5. The application will parse the file, insert the new draws into the local SQLite database, and display a success message showing the number of draws loaded.

*Note: You only need to do this when you want to update the model with the latest week's results. The data persists in `lotto.db`.*

## 5. Generating Tickets

Once your historical data is loaded (the ML model requires at least 10 historical draws to run effectively):

1.  Check the **Lunar Phasing Module** on the sidebar. If it indicates a "New Moon," the framework advises skipping play for the day.
2.  Optionally enter your name in the **Chaldean Numerology** sidebar field to extract your personal vibration number (1-8).
3.  Select your **Strategy Configuration**:
    *   **Standard:** Generates up to 12 highly optimized standard games.
    *   **System 8:** Wheels 8 main numbers to mathematically trap more combinations.
    *   **PowerHit (Powerball only):** Generates exactly 1 optimized 7-number line intended to be purchased with the guaranteed PowerHit add-on.
4.  Click **"Generate Tickets"**. The app will run the full deep learning and quantum pipeline, restrict the probability pool, apply combinatorial balancing (rejecting bad ratios like 6:0 odds/evens), and output your final playable tickets.
