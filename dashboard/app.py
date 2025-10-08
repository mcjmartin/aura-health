# dashboard/app.py
import os
import json
from datetime import datetime
from pathlib import Path

import requests
import pandas as pd
import plotly.express as px
import streamlit as st

# --- Configuration ---
# Change this if your backend runs somewhere else:
API_URL = os.environ.get("AURA_API_URL", "http://127.0.0.1:8000")
DEFAULT_USER_ID = os.environ.get("AURA_USER_ID", "student_123")

# Local data fallback (if API not running)
DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "user_stats.json"

st.set_page_config(page_title="Aura Health Dashboard", layout="wide")
st.title("🧘 Aura Health — Student Wellbeing Dashboard")

# --- Helpers ---
def load_stats_via_api(user_id: str):
    try:
        r = requests.get(f"{API_URL}/api/user/{user_id}/stats", timeout=5)
        r.raise_for_status()
        return r.json(), "api"
    except Exception:
        return None, "error"

def save_entry_via_api(user_id: str, mood: int, stress: int, sleep: int, date_str: str | None = None):
    payload = {"user_id": user_id, "mood": mood, "stress": stress, "sleep": sleep}
    if date_str:
        payload["date"] = date_str
    r = requests.post(f"{API_URL}/api/entries", json=payload, timeout=5)
    r.raise_for_status()
    return True

def load_stats_from_local(user_id: str):
    if not DATA_FILE.exists():
        return {"latest": {"mood": 0, "stress": 0, "sleep": 0}, "series": []}
    data = json.loads(DATA_FILE.read_text())
    rows = data.get(user_id, [])
    # Recreate weekly aggregates (simple version)
    if not rows:
        return {"latest": {"mood": 0, "stress": 0, "sleep": 0}, "series": []}
    latest = rows[-1]
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df["year_week"] = df["date"].dt.strftime("%G-W%V")
    agg = df.groupby("year_week")[["mood", "stress", "sleep"]].mean().round(2).reset_index()
    agg.rename(columns={"year_week": "week", "mood": "Mood", "stress": "Stress", "sleep": "Sleep"}, inplace=True)
    return {"latest": {"mood": int(latest["mood"]), "stress": int(latest["stress"]), "sleep": int(latest["sleep"])},
            "series": agg.to_dict(orient="records")}

# --- Sidebar controls ---
with st.sidebar:
    st.header("Settings")
    user_id = st.text_input("User ID", value=DEFAULT_USER_ID)
    api_url_input = st.text_input("API URL", value=API_URL)
    if api_url_input != API_URL:
        API_URL = api_url_input  # update at runtime

# --- Load data (API first, fallback local) ---
stats, source = load_stats_via_api(user_id)
if stats is None:
    stats = load_stats_from_local(user_id)
    st.info("API not reachable. Showing local data from data/user_stats.json")
else:
    st.caption("Data source: FastAPI")

latest = stats.get("latest", {"mood": 0, "stress": 0, "sleep": 0})
series = stats.get("series", [])

# --- KPI cards ---
col1, col2, col3 = st.columns(3)
col1.metric("Mood Level", f"{latest.get('mood', 0)}/10")
col2.metric("Stress Index", f"{latest.get('stress', 0)}/10")
col3.metric("Sleep Quality", f"{latest.get('sleep', 0)}/10")

# --- Weekly Progress chart ---
st.subheader("📈 Weekly Progress")
if series:
    df = pd.DataFrame(series)
    fig = px.line(df, x="week", y=["Mood", "Stress", "Sleep"], markers=True,
                  title="Mood, Stress & Sleep — Weekly Averages (0–10)")
    fig.update_yaxes(range=[0, 10])
    st.plotly_chart(fig, use_container_width=True)
else:
    st.write("No weekly data yet. Add a few entries below.")

# --- Quick check-in (writes via API if available, otherwise local file) ---
st.subheader("📝 Quick Daily Check-in")
with st.form("checkin"):
    c1, c2, c3, c4 = st.columns([1,1,1,1])
    mood = c1.slider("Mood", 0, 10, value=6)
    stress = c2.slider("Stress", 0, 10, value=5)
    sleep = c3.slider("Sleep", 0, 10, value=7)
    date_str = c4.date_input("Date", value=datetime.now()).strftime("%Y-%m-%d")
    submitted = st.form_submit_button("Save Entry")

if submitted:
    try:
        # prefer API if reachable
        ok = False
        try:
            save_entry_via_api(user_id, mood, stress, sleep, date_str)
            ok = True
            st.success("Saved via API.")
        except Exception:
            # fallback: write locally to JSON
            db = {}
            if DATA_FILE.exists():
                db = json.loads(DATA_FILE.read_text())
            db.setdefault(user_id, []).append({
                "date": date_str,
                "mood": mood,
                "stress": stress,
                "sleep": sleep
            })
            DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
            DATA_FILE.write_text(json.dumps(db, indent=2))
            st.warning(f"API not available. Saved locally to {DATA_FILE}")

        st.experimental_rerun()
    except Exception as e:
        st.error(f"Could not save entry: {e}")

# --- Simple breathing section ---
st.subheader("🫁 Breathing Exercise (4–7–8)")
st.write("Inhale 4s, hold 7s, exhale 8s. Try a few cycles.")
st.video("https://www.youtube.com/watch?v=EYQsRBNYdPk")
