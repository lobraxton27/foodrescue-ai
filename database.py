"""SQLite data access for FoodRescue AI."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("foodrescue.db")

def connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS organizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            org_type TEXT NOT NULL CHECK(org_type IN ('Donor','Recipient','Both')),
            address TEXT NOT NULL,
            latitude REAL, longitude REAL,
            capacity_kg REAL NOT NULL DEFAULT 0,
            contact_name TEXT, contact_email TEXT, contact_phone TEXT
        );
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            donor_id INTEGER NOT NULL,
            food_name TEXT NOT NULL,
            quantity_kg REAL NOT NULL CHECK(quantity_kg > 0),
            expiration_date TEXT NOT NULL,
            pickup_address TEXT NOT NULL,
            notes TEXT,
            status TEXT NOT NULL DEFAULT 'Available'
                CHECK(status IN ('Available','Reserved','Completed')),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(donor_id) REFERENCES organizations(id)
        );
        """)

def add_organization(name, org_type, address, latitude, longitude, capacity_kg,
                     contact_name="", contact_email="", contact_phone=""):
    with connect() as conn:
        cur = conn.execute("""INSERT INTO organizations
            (name,org_type,address,latitude,longitude,capacity_kg,contact_name,contact_email,contact_phone)
            VALUES (?,?,?,?,?,?,?,?,?)""",
            (name.strip(),org_type,address.strip(),latitude,longitude,float(capacity_kg),
             contact_name.strip(),contact_email.strip(),contact_phone.strip()))
        return cur.lastrowid

def get_organizations(role=None):
    with connect() as conn:
        if role == "Donor":
            rows = conn.execute("SELECT * FROM organizations WHERE org_type IN ('Donor','Both') ORDER BY name").fetchall()
        elif role == "Recipient":
            rows = conn.execute("SELECT * FROM organizations WHERE org_type IN ('Recipient','Both') ORDER BY name").fetchall()
        else:
            rows = conn.execute("SELECT * FROM organizations ORDER BY name").fetchall()
        return [dict(r) for r in rows]

def add_donation(donor_id, food_name, quantity_kg, expiration_date, pickup_address, notes=""):
    with connect() as conn:
        cur = conn.execute("""INSERT INTO donations
            (donor_id,food_name,quantity_kg,expiration_date,pickup_address,notes)
            VALUES (?,?,?,?,?,?)""",
            (donor_id,food_name.strip(),float(quantity_kg),str(expiration_date),pickup_address.strip(),notes.strip()))
        return cur.lastrowid

def get_donations(status="All"):
    sql = """SELECT d.*, o.name AS donor_name FROM donations d
             JOIN organizations o ON o.id=d.donor_id"""
    args = ()
    if status != "All":
        sql += " WHERE d.status=?"
        args = (status,)
    sql += " ORDER BY d.expiration_date ASC, d.id DESC"
    with connect() as conn:
        return [dict(r) for r in conn.execute(sql,args).fetchall()]

def update_donation_status(donation_id, status):
    if status not in ("Available","Reserved","Completed"):
        raise ValueError("Invalid status")
    with connect() as conn:
        conn.execute("UPDATE donations SET status=? WHERE id=?",(status,donation_id))

def dashboard_counts():
    with connect() as conn:
        return {
            "organizations": conn.execute("SELECT COUNT(*) FROM organizations").fetchone()[0],
            "recipients": conn.execute("SELECT COUNT(*) FROM organizations WHERE org_type IN ('Recipient','Both')").fetchone()[0],
            "donations": conn.execute("SELECT COUNT(*) FROM donations").fetchone()[0],
            "available": conn.execute("SELECT COUNT(*) FROM donations WHERE status='Available'").fetchone()[0],
        }
