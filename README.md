# Personal Expense Tracker

A simple desktop app for recording and managing personal expenses. It saves records locally in an SQLite database and displays the total of all recorded expenses.

## Requirements
- Python 3.9 or newer
- Tkinter (usually included with Python on Windows)

## How to run
1. Extract the project folder.
2. Open a terminal or command prompt in the project folder.
3. Run `python main.py` (or `python3 main.py` on some systems).

## How to use
1. Enter the date in `YYYY-MM-DD` format.
2. Choose an expense category.
3. Enter a short description.
4. Enter the amount, then select **Add Expense**.
5. View your expenses in the table and the combined total above it.
6. Select a row and choose **Delete Selected** to remove an expense.

## Data storage
Expenses are saved in `expenses.db` in the folder where the app is run. Keep a backup of this file if you want to preserve your records when moving the project.
