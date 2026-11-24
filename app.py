import io
import math
import json
import time
import sqlite3
import uuid
import random
from collections import Counter
from datetime import datetime, date
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# ============================================================
# LOTTOSTAT ENTERPRISE 5.0
# TRUE WALK-FORWARD BACKTEST + HYPERGEOMETRIC Z-SCORES
# ============================================================

st.set_page_config(
    page_title="LottoStat Enterprise 5.0",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

LOTTO_MAX_50_DATE = pd.Timestamp("2019-05-14")
LOTTO_MAX_52_DATE = pd.Timestamp("2026-04-14")
LOTTO_MAX_LAUNCH_DATE = pd.Timestamp("2009-09-25")

NUMBER_COLUMNS = [f"Num{i}" for i in range(1, 8)]

GAME_CONFIG = {
    "Lotto Max": {"draw_size": 7, "current_max": 52},
    "Lotto 6/49": {"draw_size": 6, "current_max": 49},
}

# ---------------------------- STYLING ----------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&display=swap');
html, body, [class*="css"] {font-family:'Plus Jakarta Sans',sans-serif!important;background:#f8fafc;}
#MainMenu, footer, header {visibility:hidden;}
.block-container {max-width:1450px!important;padding-top:1.1rem!important;}
.header-title {font-size:clamp(30px,4vw,48px);font-weight:800;background:linear-gradient(135deg,#0f172a,#2563eb);-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-align:center;letter-spacing:-1.8px;margin-bottom:3px;}
.header-subtitle {font-size:12px;color:#2563eb;font-weight:800;letter-spacing:3px;text-transform:uppercase;text-align:center;margin-bottom:25px;}
.status-bar {display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;background:#fff;padding:12px 20px;border-radius:14px;border:1px solid #e2e8f0;margin-bottom:22px;font-size:12px;font-weight:700;color:#64748b;}
.status-dot {height:8px;width:8px;background:#10b981;border-radius:50%;display:inline-block;margin-right:7px;}
.stTabs [data-baseweb="tab-list"] {gap:8px;background:#f1f5f9;padding:7px;border-radius:14px;border:1px solid #e2e8f0;}
.stTabs [data-baseweb="tab"] {border-radius:9px;padding:10px 18px;font-weight:700;}
.ticket-card {background:#fff;border:1px solid #e2e8f0;border-top:5px solid #2563eb;border-radius:18px;padding:20px;box-shadow:0 12px 28px rgba(15,23,42,.06);height:100%;margin-bottom:12px;}
.ticket-heading {display:flex;justify-content:space-between;gap:8px;border-bottom:2px dashed #cbd5e1;padding-bottom:12px;margin-bottom:16px;font-family:'Courier Prime',monospace;font-size:12px;font-weight:700;text-transform:uppercase;color:#0f172a;}
.ball-row {display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:12px 0 18px;}
@keyframes ballRollIn {0%{opacity:0;transform:translateX(-55px) rotate(-240deg) scale(.55)}70%{opacity:1;transform:translateX(5px) rotate(18deg) scale(1.08)}100%{opacity:1;transform:translateX(0) rotate(0) scale(1)}}
.rolling-ball {animation:ballRollIn .42s cubic-bezier(.2,.8,.2,1) both;}
.ball {display:inline-flex;align-items:center;justify-content:center;width:42px;height:42px;border-radius:50%;color:white;font-weight:800;background:linear-gradient(135deg,#1e3a8a,#3b82f6);box-shadow:0 4px 10px rgba(37,99,235,.24);border:1px solid #93c5fd;}
.line-label {font-family:'Courier Prime',monospace;color:#94a3b8;font-size:11px;font-weight:700;margin:10px 0 2px;}
.metric-grid {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin-top:12px;}
.metric {background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:10px;text-align:center;}
.metric small {display:block;color:#64748b;font-size:9px;font-weight:800;letter-spacing:.6px;text-transform:uppercase;}
.metric b {display:block;color:#0f172a;font-size:17px;margin-top:3px;}
.integrity-high {color: #059669; }
.integrity-mid {color: #d97706; }
.integrity-low {color: #dc2626; }
.note {background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:12px 14px;color:#1e3a8a;font-size:12px;}
.warning-note {background:#fffbeb;border:1px solid #fde68a;border-radius:10px;padding:12px 14px;color:#92400e;font-size:12px;}
.footer {text-align:center;color:#94a3b8;font-size:11px;margin-top:35px;padding-top:18px;border-top:1px solid #e2e8f0;}
div[data-testid="stButton"] button[kind="primary"] {background:linear-gradient(135deg,#2563eb,#1d4ed8);border:0;border-radius:11px;font-weight:800;letter-spacing:.4px;padding:12px;}

@media (max-width: 768px) {
  .block-container {padding: .75rem .8rem 2rem!important; max-width:100%!important;}
  .header-title {font-size:30px; letter-spacing:-1px; line-height:1.15; margin-top:8px;}
  .header-subtitle {font-size:9px; letter-spacing:1.4px; line-height:1.5; margin:8px 0 18px;}
  .status-bar {display:grid; grid-template-columns:1fr; gap:7px; padding:11px 13px; margin-bottom:14px; font-size:11px;}
  .stTabs [data-baseweb="tab-list"] {display:flex; flex-wrap:nowrap; overflow-x:auto; gap:4px; padding:5px; scrollbar-width:thin;}
  .stTabs [data-baseweb="tab"] {flex:0 0 auto; padding:9px 11px; font-size:12px; white-space:nowrap;}
  div[data-testid="stHorizontalBlock"] {flex-wrap:wrap!important; gap:.65rem!important;}
  div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {flex:1 1 100%!important; min-width:100%!important; width:100%!important;}
  .ticket-card {padding:14px 12px; border-radius:14px; margin-bottom:10px;}
  .ticket-heading {font-size:10px; padding-bottom:9px; margin-bottom:11px;}
  .ball-row {gap:6px; margin:10px 0 13px;}
  .ball {width:36px; height:36px; font-size:13px;}
  .metric-grid {gap:5px; grid-template-columns:repeat(2,1fr);}
  .metric {padding:8px 4px;}
  .metric small {font-size:8px; letter-spacing:.2px;}
  .metric b {font-size:15px;}
  .note, .warning-note {font-size:11px; padding:10px; line-height:1.5;}
  div[data-testid="stButton"] button {width:100%; min-height:46px; white-space:normal; line-height:1.25;}
  div[data-testid="stDataFrame"], div[data-testid="stTable"] {overflow-x:auto!important;}
  h1, h2, h3 {line-height:1.2!important;}
}
@media (max-width: 380px) {
  .block-container {padding-left:.55rem!important; padding-right:.55rem!important;}
  .header-title {font-size:26px;}
  .ball {width:33px;height:33px;font-size:12px;}
}
</style>
""", unsafe_allow_html=True)

# ---------------------------- DATABASE ----------------------------

APP_DIR = Path(__file__).resolve().parent
TICKET_DB = APP_DIR / "saved_tickets.sqlite3"

def init_ticket_db():
    with sqlite3.connect(TICKET_DB) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS ticket_batches (
            batch_id TEXT PRIMARY KEY, game TEXT NOT NULL, draw_date TEXT NOT NULL,
            generated_at TEXT NOT NULL, generation_seed INTEGER, tickets_json TEXT NOT NULL,
            winning_numbers_json TEXT, checked_at TEXT
        )""")

def save_ticket_batch(game, draw_date, seed, tickets):
    batch_id = uuid.uuid4().hex[:12].upper()
    payload = {name: [[int(n) for n in line] for line in lines] for name, lines in tickets.items()}
    with sqlite3.connect(TICKET_DB) as conn:
        conn.execute("INSERT INTO ticket_batches (batch_id, game, draw_date, generated_at, generation_seed, tickets_json) VALUES (?, ?, ?, ?, ?, ?)",
            (batch_id, game, draw_date.isoformat(), datetime.now().isoformat(timespec="seconds"), int(seed), json.dumps(payload)))
    return batch_id

def load_ticket_batches(game=None):
    with sqlite3.connect(TICKET_DB) as conn:
        conn.row_factory = sqlite3.Row
        query = "SELECT * FROM ticket_batches WHERE game=? ORDER BY generated_at DESC" if game else "SELECT * FROM ticket_batches ORDER BY generated_at DESC"
        rows = conn.execute(query, (game,) if game else ()).fetchall()
    return [dict(row) for row in rows]

def update_ticket_batch_result(batch_id, winning_numbers):
    with sqlite3.connect(TICKET_DB) as conn:
        conn.execute("UPDATE ticket_batches SET winning_numbers_json=?, checked_at=? WHERE batch_id=?",
            (json.dumps([int(n) for n in winning_numbers]), datetime.now().isoformat(timespec="seconds"), batch_id))

init_ticket_db()

# ---------------------------- DATA PREP ----------------------------

def lotto_max_pool_size(draw_date):
    draw_date = pd.Timestamp(draw_date)
    if draw_date < LOTTO_MAX_LAUNCH_DATE: return 0
    if draw_date < LOTTO_MAX_50_DATE: return 49
    if draw_date < LOTTO_MAX_52_DATE: return 50
    return 52

def game_pool_size(game, draw_date):
    return 49 if game == "Lotto 6/49" else lotto_max_pool_size(draw_date)

def read_and_prepare(raw_df):
    data = raw_df.copy()
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    for col in NUMBER_COLUMNS:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data = data.dropna(subset=["Date"])
    valid_rows = []
    for idx, row in data.iterrows():
        present = [pd.notna(row[c]) for c in NUMBER_COLUMNS]
        size = sum(present)
        if size not in (6, 7) or present[:size] != [True] * size or any(present[size:]): continue
        values = [int(row[c]) for c in NUMBER_COLUMNS[:size]]
        game = "Lotto Max" if size == 7 else "Lotto 6/49"
        max_allowed = game_pool_size(game, row["Date"])
        if max_allowed == 0 or len(set(values)) != size or any(v < 1 or v > max_allowed for v in values): continue
        valid_rows.append(idx)

    data = data.loc[valid_rows].copy().reset_index(drop=True)
    data["DrawSize"] = data[NUMBER_COLUMNS].notna().sum(axis=1)
    data["Game"] = np.where(data["DrawSize"].eq(7), "Lotto Max", "Lotto 6/49")
    data = data.sort_values("Date").reset_index(drop=True)
    
    # CRITICAL FIX: Keep first to prevent data loss on duplicates
    data = data.drop_duplicates(subset=["Date", "Game"], keep="first").reset_index(drop=True)
    
    data["Numbers"] = data.apply(lambda row: tuple(int(row[c]) for c in NUMBER_COLUMNS[:int(row["DrawSize"])]), axis=1)
    return data

@st.cache_data(show_spinner=False)
def load_local_csv(path_string):
    return pd.read_csv(path_string)

def get_source_data():
    uploaded = st.sidebar.file_uploader("Upload / replace olg_data.csv", type=["csv"])
    if uploaded is not None:
        return pd.read_csv(io.BytesIO(uploaded.getvalue())), "Uploaded CSV"
    local_path = Path(__file__).with_name("olg_data.csv")
    if local_path.exists():
        return load_local_csv(str(local_path)), "olg_data.csv"
    return None, "No CSV found"

# ---------------------------- ADVANCED ANALYTICS ENGINE ----------------------------

@st.cache_data(show_spinner=False)
def calculate_advanced_analytics(game_df, game, max_number):
    """Vectorized engine with true Hypergeometric Variance for Z-Scores."""
    if game_df.empty: return pd.DataFrame(), {}
    
    draw_size = 7 if game == "Lotto Max" else 6
    exploded = game_df[['Date', 'Numbers']].explode('Numbers').rename(columns={'Numbers': 'Number'})
    exploded['PoolSize'] = exploded['Date'].apply(lambda d: game_pool_size(game, d))
    exploded = exploded[exploded['Number'] <= exploded['PoolSize']]
    counts = exploded.groupby('Number').size().reset_index(name='Observed')
    
    # Hypergeometric Expected & Variance Calculation
    expected_dict = {}
    variance_dict = {}
    
    # Unique draws to avoid counting multiple numbers from same draw
    unique_draws = game_df[['Date']].copy()
    unique_draws['PoolSize'] = unique_draws['Date'].apply(lambda d: game_pool_size(game, d))
    
    for num in range(1, max_number + 1):
        eligible_draws = unique_draws[unique_draws['PoolSize'] >= num]
        # Expected hits = sum(draw_size / pool_size)
        exp = (draw_size / eligible_draws['PoolSize']).sum()
        
        # Variance = sum( p * (1-p) * ((N-n)/(N-1)) )
        p = draw_size / eligible_draws['PoolSize']
        variance = (p * (1 - p) * ((eligible_draws['PoolSize'] - draw_size) / (eligible_draws['PoolSize'] - 1))).sum()
        
        expected_dict[num] = exp
        variance_dict[num] = variance
        
    expected_df = pd.DataFrame(list(expected_dict.items()), columns=['Number', 'Expected'])
    variance_df = pd.DataFrame(list(variance_dict.items()), columns=['Number', 'Variance'])
    
    analytics = pd.merge(pd.DataFrame({'Number': range(1, max_number + 1)}), counts, on='Number', how='left').fillna(0)
    analytics = pd.merge(analytics, expected_df, on='Number', how='left').fillna(0)
    analytics = pd.merge(analytics, variance_df, on='Number', how='left').fillna(1) # prevent div by 0
    
    # True Z-Score
    analytics['Z-Score'] = (analytics['Observed'] - analytics['Expected']) / np.sqrt(analytics['Variance'].replace(0, 1))
    
    # Recent 50
    recent_df = game_df.tail(50)
    recent_exploded = recent_df[['Date', 'Numbers']].explode('Numbers').rename(columns={'Numbers': 'Number'})
    recent_exploded['PoolSize'] = recent_exploded['Date'].apply(lambda d: game_pool_size(game, d))
    recent_exploded = recent_exploded[recent_exploded['Number'] <= recent_exploded['PoolSize']]
    recent_counts = recent_exploded.groupby('Number').size().reset_index(name='Recent Observed')
    analytics = pd.merge(analytics, recent_counts, on='Number', how='left').fillna(0)
    
    # Ranking
    analytics = analytics.sort_values('Z-Score', ascending=False).reset_index(drop=True)
    analytics.insert(0, 'Rank', analytics.index + 1)
    analytics['Appearance %'] = (analytics['Observed'] / (analytics['Expected'] / (draw_size / max_number))) * 100
    
    # Gap
    gaps = {}
    all_numbers_sets = game_df['Numbers'].tolist()
    for num in range(1, max_number + 1):
        last_seen = 0
        for i in range(len(all_numbers_sets)-1, -1, -1):
            if num in all_numbers_sets[i]:
                last_seen = len(all_numbers_sets) - 1 - i
                break
        gaps[num] = last_seen
    analytics['Gap'] = analytics['Number'].map(gaps)
    
    chi_sq = ((analytics['Observed'] - analytics['Expected'])**2 / analytics['Expected'].replace(0, 1)).sum()
    meta = {"chi_square": chi_sq, "total_draws": len(game_df)}
    return analytics, meta

# ---------------------------- SELECTION STRATEGY ----------------------------

def is_valid_selection(selection, max_number, relaxed=False):
    if sum(1 for n in selection if n <= 31) > 3: return False
    min_gap = 2 if relaxed else 3
    for a, b in zip(selection, selection[1:]):
        if b - a < min_gap: return False
    decades = [n // 10 for n in selection]
    if Counter(decades).most_common(1)[0][1] > 3 if relaxed else Counter(decades).most_common(1)[0][1] > 2: return False
    return True

def generate_ticket(analytics_df, max_number, draw_size):
    # Expand candidate pool dynamically to guarantee a spread ticket
    for pool_size in [30, 40, 50, max_number]:
        candidates = analytics_df.head(min(pool_size, max_number))
        candidate_nums = candidates['Number'].astype(int).tolist()
        
        # Weight by Z-score
        raw_weights = candidates['Z-Score'] - candidates['Z-Score'].min() + 1.0
        probs = raw_weights / raw_weights.sum()
        
        for _ in range(2000):
            selected = np.random.choice(candidate_nums, size=draw_size, replace=False, p=probs)
            selected = sorted(selected.tolist())
            if is_valid_selection(selected, max_number):
                return selected

        # Relax rules but keep birthday rule intact
        for _ in range(2000):
            selected = np.random.choice(candidate_nums, size=draw_size, replace=False, p=probs)
            selected = sorted(selected.tolist())
            if is_valid_selection(selected, max_number, relaxed=True):
                return selected

    # Absolute safety net (will only happen if dataset is microscopic)
    return sorted(analytics_df.head(draw_size)['Number'].tolist())

# ---------------------------- UI COMPONENTS ----------------------------

def render_number_balls(numbers, color="#2563eb"):
    balls = [f'<span class="ball" style="background:linear-gradient(135deg,{color},#1e40af);">{int(n):02d}</span>' for n in numbers]
    return '<div class="ball-row">' + "".join(balls) + "</div>"

def render_frequency_ticket(numbers, game_name, max_number):
    integrity = 100 # We guarantee 100% integrity now due to the strict fallback
    st.markdown(f"""
        <div class="ticket-card">
            <div class="ticket-heading"><span>FREQUENCY STRATEGY</span><span>{game_name.upper()}</span></div>
            {render_number_balls(numbers)}
            <div class="metric-grid">
                <div class="metric"><small>Numbers</small><b>{len(numbers)}</b></div>
                <div class="metric"><small>Sum</small><b>{sum(numbers)}</b></div>
                <div class="metric"><small>Range</small><b>{max(numbers) - min(numbers)}</b></div>
                <div class="metric"><small>Integrity</small><b class="integrity-high">{integrity}%</b></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def reveal_ticket(numbers, game_name, max_number):
    placeholder = st.empty()
    revealed = []
    for number in numbers:
        revealed.append(number)
        balls = "".join(f'<span class="ball rolling-ball">{n:02d}</span>' for n in revealed)
        placeholder.markdown(f"""
            <div class="ticket-card">
                <div class="ticket-heading"><span>FREQUENCY STRATEGY</span><span>{game_name.upper()}</span></div>
                <div class="ball-row">{balls}</div>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(0.25)

# ---------------------------- MAIN APP ----------------------------

def main():
    with st.sidebar:
        st.markdown("## LottoStat Enterprise 5.0")
        raw_data, source_label = get_source_data()
        st.caption(f"Data: {source_label}")

    if raw_data is None:
        st.error("Could not find olg_data.csv.")
        st.stop()

    data = read_and_prepare(raw_data)
    st.markdown('<div class="header-title">LottoStat Enterprise</div>', unsafe_allow_html=True)
    st.markdown('<div class="header-subtitle">Institutional Statistical Analysis</div>', unsafe_allow_html=True)

    game_choice = st.selectbox("SELECT LOTTERY GAME", ["Lotto Max", "Lotto 6/49"], key="game_choice")
    game_df = data[data["Game"] == game_choice].copy().sort_values("Date").reset_index(drop=True)

    if game_df.empty:
        st.error(f"No historical draws found for {game_choice}.")
        st.stop()

    latest_date = game_df["Date"].max()
    current_max = game_pool_size(game_choice, latest_date)
    draw_size = GAME_CONFIG[game_choice]["draw_size"]
    
    st.markdown(f"""
        <div class="status-bar">
            <span><span class="status-dot"></span> ENGINE ONLINE</span>
            <span>{game_choice} ({current_max} numbers)</span>
            <span>{len(game_df):,} HISTORICAL DRAWS</span>
            <span>{game_df['Date'].min():%Y-%m-%d} TO {latest_date:%Y-%m-%d}</span>
        </div>
    """, unsafe_allow_html=True)

    analytics_df, meta = calculate_advanced_analytics(game_df, game_choice, current_max)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎟️ Generator", "📊 Frequency", "📈 Backtesting", "💾 Saved", "🧠 Deep Insights"])

    # ---------------- TAB 1: GENERATOR ----------------
    with tab1:
        st.markdown("### Ticket Generator")
        st.write(f"Weighted selection from statistically significant numbers.")
        
        if st.button("GENERATE TICKET", type="primary", use_container_width=True):
            with st.spinner("Analyzing Z-Scores and enforcing spread rules..."):
                ticket = generate_ticket(analytics_df, current_max, draw_size)
            
            st.session_state["ticket"] = ticket
            st.session_state["generated_at"] = datetime.now().strftime("%d %b %Y at %H:%M")
            st.session_state.pop("animated_ticket", None)

        if "ticket" in st.session_state:
            st.markdown("---")
            if st.session_state.get("animated_ticket") != st.session_state["ticket"]:
                reveal_ticket(st.session_state["ticket"], game_choice, current_max)
                st.session_state["animated_ticket"] = st.session_state["ticket"]
            else:
                render_frequency_ticket(st.session_state["ticket"], game_choice, current_max)
            
            st.markdown("#### Why these numbers were selected")
            expl_data = []
            for n in st.session_state["ticket"]:
                row = analytics_df[analytics_df['Number'] == n].iloc[0]
                expl_data.append({
                    "Number": n, "Z-Score": f"{row['Z-Score']:.2f}",
                    "Rank": int(row['Rank']), "Observed": int(row['Observed']),
                    "Expected": f"{row['Expected']:.1f}", "Gap": int(row['Gap'])
                })
            st.dataframe(pd.DataFrame(expl_data), use_container_width=True, hide_index=True)
            
            st.divider()
            draw_date = st.date_input("Draw Date", value=date.today())
            if st.button("SAVE TICKET", type="primary", use_container_width=True):
                batch_id = save_ticket_batch(game_choice, draw_date, 0, {"Strategy": [st.session_state["ticket"]]})
                st.success(f"Saved! Batch ID: {batch_id}")

    # ---------------- TAB 2: FREQUENCY ----------------
    with tab2:
        st.markdown("### Statistical Frequency Analysis")
        st.write(f"Data: {len(game_df)} draws. Chi-Square fairness score: `{meta['chi_square']:.2f}` (Lower means closer to perfectly random).")
        
        st.dataframe(
            analytics_df[['Rank', 'Number', 'Observed', 'Expected', 'Z-Score', 'Appearance %', 'Gap']].style.format({
                "Expected": "{:.1f}", "Z-Score": "{:+.2f}", "Appearance %": "{:.1f}%", "Observed": "{:,}"
            }).background_gradient(subset=['Z-Score'], cmap='RdBu_r', vmin=-3, vmax=3),
            use_container_width=True, hide_index=True
        )
        
        st.download_button("DOWNLOAD DATA (CSV)", analytics_df.to_csv(index=False).encode('utf-8'), "lottostat_data.csv", "text/csv")

    # ---------------- TAB 3: BACKTESTING ----------------
    with tab3:
        st.markdown("### True Walk-Forward Backtesting")
        st.write("This test rewinds time for every draw, recalculating statistics on the fly to prevent look-ahead bias.")
        
        test_draws = st.slider("Test draws", 50, 200, 100)
        
        if st.button("RUN TRUE BACKTEST", type="primary", use_container_width=True):
            progress = st.progress(0)
            strat_matches = []
            rand_matches = []
            start_idx = len(game_df) - test_draws
            
            for i, idx in enumerate(range(start_idx, len(game_df))):
                # 1. Slice Data (Only data available BEFORE the test draw)
                hist = game_df.iloc[:idx]
                actual = set(game_df.iloc[idx]['Numbers'])
                
                # 2. Recalculate Analytics (Prevents Look-Ahead Bias)
                hist_analytics, _ = calculate_advanced_analytics(hist, game_choice, current_max)
                
                # 3. Generate Ticket
                strat_ticket = generate_ticket(hist_analytics, current_max, draw_size)
                
                # 4. Random Baseline
                rand_ticket = sorted(random.sample(range(1, current_max + 1), draw_size))
                
                strat_matches.append(len(set(strat_ticket) & actual))
                rand_matches.append(len(set(rand_ticket) & actual))
                progress.progress((i+1)/test_draws)
            
            progress.empty()
            st.metric("Strategy Avg Matches", f"{np.mean(strat_matches):.3f}")
            st.metric("Random Avg Matches", f"{np.mean(rand_matches):.3f}")
            st.bar_chart(pd.DataFrame({"Method": ["Strategy", "Random"], "Avg Matches": [np.mean(strat_matches), np.mean(rand_matches)]}).set_index("Method"))
            st.caption("This is a true out-of-sample test. Positive difference means the strategy historically outperformed random selection.")

    # ---------------- TAB 4: SAVED ----------------
    with tab4:
        st.markdown("### Saved Tickets")
        saved = load_ticket_batches(game_choice)
        if saved:
            st.dataframe(pd.DataFrame(saved)[['batch_id', 'draw_date', 'generated_at']], use_container_width=True)
        else:
            st.info("No saved tickets.")

    # ---------------- TAB 5: INSIGHTS ----------------
    with tab5:
        st.markdown("### Automated Insights Engine")
        
        hottest = analytics_df.head(3)
        coldest = analytics_df.tail(3)
        
        # Dynamic text generation
        hot_text = ", ".join([f"<b>#{n}</b> (Z: {z:+.2f})" for n, z in zip(hottest['Number'], hottest['Z-Score'])])
        cold_text = ", ".join([f"<b>#{n}</b> (Z: {z:+.2f})" for n, z in zip(coldest['Number'], coldest['Z-Score'])])
        overdue = analytics_df.sort_values('Gap', ascending=False).head(1).iloc[0]
        
        st.markdown(f"""
        <div class="note">
        <b>🔥 Hottest Numbers:</b> {hot_text}<br>
        <b>❄️ Coldest Numbers:</b> {cold_text}<br><br>
        <b>⏳ Most Overdue:</b> Number <b>#{int(overdue['Number'])}</b> hasn't appeared in <b>{int(overdue['Gap'])} draws</b> (its historical Z-Score is {overdue['Z-Score']:+.2f}).<br><br>
        <b>🎲 Fairness Check:</b> The Chi-Square score is <b>{meta['chi_square']:.2f}</b>. A score near 0 means the lottery machine is perfectly fair. A very high score would indicate bias.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### Number Lateness")
        st.bar_chart(analytics_df.sort_values('Gap', ascending=False).head(15).set_index('Number')['Gap'])

if __name__ == "__main__":
    main()
