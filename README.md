# FoodRescue AI: Community Food Redistribution

FoodRescue AI is a beginner-friendly prototype that helps restaurants, grocery stores, and other donors share surplus food with food banks and community organizations. It records donations, stores organization information in SQLite, and ranks potential recipients using a simple, explainable matching score.

## Features

- Register food donors and recipient organizations
- Record surplus food donations, quantities, and expiration dates
- View available donations
- Rank recipient organizations by capacity, distance (when coordinates are provided), and urgency
- Store data locally in SQLite

## Tech stack

- Python
- Streamlit
- SQLite
- pandas
- geopy

## Run locally

1. Install Python 3.10 or newer.
2. Clone this repository and open a terminal in the project folder.
3. Create and activate a virtual environment (recommended).
4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Start the app:

   ```bash
   streamlit run app.py
   ```

Streamlit will print a local URL to open in your browser.

## Matching score

The prototype uses a transparent heuristic, not a trained machine-learning model. It considers recipient capacity, distance when both organizations have coordinates, and how soon the donation expires. Review matches with the recipient before arranging pickup; this app does not verify food safety or guarantee a donation is accepted.

## Data and privacy

The app creates `foodrescue.db` locally the first time it runs. The database is excluded from Git because it may contain contact details and operational information. Do not enter real personal or sensitive data into a demo deployment.

## Current scope

This is an educational MVP. It does not automatically contact organizations, arrange transport, or certify food safety. Future improvements could include user authentication, verified organizations, notification workflows, and a map view.
