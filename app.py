"""Streamlit UI for FoodRescue AI."""
from datetime import date
import pandas as pd
import streamlit as st
from database import (init_db, add_organization, get_organizations, add_donation,
                      get_donations, update_donation_status, dashboard_counts)
from matching import rank_recipients

st.set_page_config(page_title="FoodRescue AI", page_icon="🥕", layout="wide")
init_db()
st.title("🥕 FoodRescue AI")
st.caption("Community Food Redistribution — educational prototype")
st.sidebar.warning("Use demo/non-sensitive data. Matches are suggestions, not guarantees.")
page = st.sidebar.radio("Navigate",["Dashboard","Register Organization","Donate Food","View Donations","Find Matches"])

if page == "Dashboard":
    st.header("Dashboard")
    counts = dashboard_counts()
    cols = st.columns(4)
    for col,(label,key) in zip(cols,[("Organizations","organizations"),("Recipients","recipients"),("Total donations","donations"),("Available donations","available")]):
        col.metric(label,counts[key])
    donations = get_donations("Available")
    st.subheader("Available donations")
    if donations:
        st.dataframe(pd.DataFrame(donations)[["food_name","quantity_kg","expiration_date","donor_name","pickup_address","status"]],use_container_width=True,hide_index=True)
    else:
        st.info("No donations yet. Register an organization and add a donation to get started.")
    st.markdown("Register organizations, record surplus food, then use **Find Matches** to rank eligible recipients.")

elif page == "Register Organization":
    st.header("Register an Organization")
    with st.form("org_form",clear_on_submit=True):
        name = st.text_input("Organization name *")
        role = st.selectbox("Organization role",["Donor","Recipient","Both"])
        address = st.text_input("Address or general location *")
        capacity = st.number_input("Maximum food capacity (kg)",min_value=0.0,value=25.0,step=5.0)
        coords = st.checkbox("Add approximate latitude and longitude")
        lat = lon = None
        if coords:
            c1,c2 = st.columns(2)
            lat = c1.number_input("Latitude",min_value=-90.0,max_value=90.0,value=30.45,format="%.6f")
            lon = c2.number_input("Longitude",min_value=-180.0,max_value=180.0,value=-91.14,format="%.6f")
        contact = st.text_input("Contact name (optional)")
        email = st.text_input("Contact email (optional)")
        phone = st.text_input("Contact phone (optional)")
        submit = st.form_submit_button("Register organization")
    if submit:
        if not name.strip() or not address.strip():
            st.error("Enter an organization name and location.")
        else:
            add_organization(name,role,address,lat,lon,capacity,contact,email,phone)
            st.success(f"Registered {name.strip()}.")
    orgs = get_organizations()
    if orgs:
        st.subheader("Registered organizations")
        st.dataframe(pd.DataFrame(orgs)[["name","org_type","address","capacity_kg","contact_email"]],use_container_width=True,hide_index=True)

elif page == "Donate Food":
    st.header("Record a Food Donation")
    donors = get_organizations("Donor")
    if not donors:
        st.info("Register a donor organization first.")
    else:
        labels = {f'{o["name"]} (ID {o["id"]})':o for o in donors}
        with st.form("donation_form",clear_on_submit=True):
            label = st.selectbox("Donor organization",list(labels))
            food = st.text_input("Food item / description *",placeholder="e.g., packaged sandwiches")
            qty = st.number_input("Quantity (kg)",min_value=0.1,value=10.0,step=1.0)
            expiry = st.date_input("Expiration / use-by date",value=date.today())
            pickup = st.text_input("Pickup address",value=labels[label]["address"])
            notes = st.text_area("Storage or pickup notes (optional)")
            submit = st.form_submit_button("Save donation")
        if submit:
            if not food.strip() or not pickup.strip():
                st.error("Enter a food description and pickup address.")
            else:
                did = add_donation(labels[label]["id"],food,qty,expiry.isoformat(),pickup,notes)
                st.success(f"Donation #{did} saved.")

elif page == "View Donations":
    st.header("Food Donations")
    status = st.selectbox("Filter by status",["Available","Reserved","Completed","All"])
    donations = get_donations(status)
    if donations:
        st.dataframe(pd.DataFrame(donations)[["id","food_name","quantity_kg","expiration_date","donor_name","pickup_address","status","notes"]],use_container_width=True,hide_index=True)
        choices = {f'#{d["id"]} — {d["food_name"]} ({d["status"]})':d for d in donations}
        selected = st.selectbox("Choose a donation to update",list(choices))
        new_status = st.selectbox("New status",["Available","Reserved","Completed"])
        if st.button("Update status"):
            update_donation_status(choices[selected]["id"],new_status)
            st.success("Donation status updated.")
            st.rerun()
    else:
        st.info("No donations match this filter.")

elif page == "Find Matches":
    st.header("Find Recipient Matches")
    donations = get_donations("Available")
    recipients = get_organizations("Recipient")
    if not donations:
        st.info("No available donations. Add a donation first.")
    elif not recipients:
        st.info("Register at least one recipient organization first.")
    else:
        choices = {f'#{d["id"]} — {d["food_name"]} | {d["quantity_kg"]} kg | expires {d["expiration_date"]}':d for d in donations}
        label = st.selectbox("Choose a donation",list(choices))
        donation = choices[label]
        st.write(f'**Donor:** {donation["donor_name"]}')
        st.write(f'**Pickup location:** {donation["pickup_address"]}')
        donor = next((o for o in get_organizations() if o["id"]==donation["donor_id"]),None)
        ranked = rank_recipients(donation,recipients,donor)
        if ranked:
            rows = [{"Recipient":r["name"],"Capacity (kg)":r["capacity_kg"],"Match score":r["score"],
                     "Distance (km)":r["distance_km"] if r["distance_km"] is not None else "Unknown",
                     "Location":r["address"],"Capacity score":r["capacity_score"],"Urgency score":r["urgency_score"]} for r in ranked]
            st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
            st.caption("Scoring weights: capacity fit 40%, distance 40%, expiration urgency 20%. Unknown coordinates receive a neutral distance score.")
            st.warning("Confirm acceptance, pickup timing, storage needs, and food safety with the recipient. This tool does not verify food safety.")
        else:
            st.warning("No recipients have enough listed capacity for this donation.")
