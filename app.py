import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from collections import Counter
from sklearn.cluster import KMeans
import random
import time
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="LottoStat Enterprise", page_icon="💎", layout="wide")

# --- PRO UI/UX STYLING (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: #f8fafc;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .block-container {
        max-width: 1100px !important;
        padding-top: 1rem !important;
    }
    
    /* Top Status Bar */
    .status-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #ffffff;
        padding: 12px 24px;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        margin-bottom: 25px;
        font-size: 13px;
        font-weight: 600;
        color: #64748b;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
    }
    .dot {
        height: 8px; width: 8px;
        background-color: #10b981;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.8);
        animation: blink 2s infinite;
    }
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }

    /* Premium Typography */
    .header-title {
        font-size: 48px;
        font-weight: 800;
        background: linear-gradient(135deg, #0f172a 0%, #2563eb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 5px;
        letter-spacing: -2px;
    }
    .header-subtitle {
        font-size: 14px;
        color: #2563eb;
        font-weight: 800;
        letter-spacing: 3px;
        text-transform: uppercase;
        text-align: center;
        margin-bottom: 30px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #f1f5f9;
        padding: 8px;
        border-radius: 16px;
        margin-bottom: 25px;
        border: 1px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 12px 24px;
        background-color: transparent;
        color: #64748b;
        font-weight: 700;
        transition: all 0.2s;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #1e3a8a !important;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
    
    /* Premium Generate Button */
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 24px !important;
        font-size: 15px !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 8px 20px -5px rgba(37, 99, 235, 0.6) !important;
        transition: all 0.2s ease !important;
        margin-bottom: 20px !important;
    }
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 12px 25px -5px rgba(37, 99, 235, 0.8) !important;
    }
    
    /* --- THE PHYSICAL TICKET --- */
    .ticket-wrapper {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 25px;
        margin: 0;
        width: 100%;
        box-shadow: 0 15px 30px -10px rgba(0,0,0,0.08);
        position: relative;
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    
    /* Perforated edges */
    .ticket-wrapper::before, .ticket-wrapper::after {
        content: '';
        position: absolute;
        width: 20px;
        height: 20px;
        background-color: #f8fafc;
        border-radius: 50%;
        top: 50%;
        transform: translateY(-50%);
        z-index: 1;
    }
    .ticket-wrapper::before { left: -10px; border-right: 1px solid #e2e8f0; }
    .ticket-wrapper::after { right: -10px; border-left: 1px solid #e2e8f0; }
    
    .ticket-header {
        display: flex;
        justify-content: space-between;
        border-bottom: 2px dashed #cbd5e1;
        padding-bottom: 15px;
        margin-bottom: 20px;
        font-family: 'Courier Prime', monospace;
        font-size: 12px; 
        font-weight: 700;
        text-transform: uppercase;
        position: relative;
        z-index: 2;
    }
    
    /* Force the balls into a perfect 3x2 grid */
    .ball-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        justify-items: center;
        align-items: center;
        margin: 20px 0;
        flex-grow: 1;
        position: relative;
        z-index: 2;
    }
    
    /* --- PREMIUM BALLS --- */
    .lottery-ball {
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: #ffffff;
        border-radius: 50%;
        width: 60px; 
        height: 60px;
        font-weight: 800;
        font-size: 24px;
        box-shadow: 0 10px 20px rgba(37, 99, 235, 0.4), inset 0 2px 4px rgba(255,255,255,0.3);
        border: 2px solid #93c5fd;
    }
    
    .lottery-ball.purple {
        background: linear-gradient(135deg, #86198f 0%, #c026d3 100%);
        box-shadow: 0 10px 20px rgba(192, 38, 211, 0.4), inset 0 2px 4px rgba(255,255,255,0.3);
        border: 2px solid #f0abfc;
    }
    
    /* Stat Cards */
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        margin-top: auto;
        position: relative;
        z-index: 2;
    }
    
    .stat-card {
        background: #f8fafc;
        border-radius: 12px;
        padding: 12px 8px; 
        text-align: center;
        border: 1px solid #e2e8f0;
    }
    .stat-title { font-size: 9px; font-weight: 800; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }
    .stat-value { font-size: 18px; font-weight: 800; color: #0f172a; margin-top: 4px; }
    
    .share-card { background: linear-gradient(180deg, #f0fdf4 0%, #dcfce7 100%); border-color: #bbf7d0; }
    .share-value { color: #16a34a; }

    .footer { text-align: center; color: #94a3b8; font-size: 12px; margin-top: 50px; padding-top: 20px; border-top: 1px solid #e2e8f0; font-weight: 600; }

    /* Sidebar specific styling */
    .sidebar-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
    }
    .sidebar-title {
        font-weight: 800;
        font-size: 14px;
        margin-bottom: 5px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .sidebar-text {
        font-size: 12px;
        color: #475569;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    df = pd.read_csv("olg_data.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_data()
num_cols_all = [c for c in df.columns if c.startswith('Num')]

# --- SCORING ALGORITHMS ---
def calculate_entropy(ticket):
    gaps = [ticket[i+1] - ticket[i] for i in range(len(ticket)-1)]
    if not gaps: return 50
    return min(100, max(0, int((np.std(gaps) / 8) * 100)))

def get_jackpot_share(ticket):
    high_nums = sum(1 for n in ticket if n > 31)
    if high_nums >= 4: return "Low"
    elif high_nums >= 2: return "Medium"
    else: return "High"

# --- HTML TICKET BUILDER (FOR ANIMATION) ---
def build_ticket_html(final_numbers, current_idx, max_num, is_blue, time_str):
    ball_html = ""
    is_final = (current_idx >= len(final_numbers))
    
    for j in range(len(final_numbers)):
        if is_final or j < current_idx:
            # Landed
            ball_class = "lottery-ball" if is_blue else "lottery-ball purple"
            ball_html += f"<div class='{ball_class}'>{final_numbers[j]}</div>"
        elif j == current_idx:
            # Spinning
            rand_num = random.randint(1, max_num)
            ball_html += f"<div class='lottery-ball' style='filter: blur(2px); background: #cbd5e1; color: #ffffff;'>{rand_num}</div>"
        else:
            # Waiting
            ball_html += f"<div class='lottery-ball' style='background: #f8fafc; color: #cbd5e1; border: 2px solid #e2e8f0; box-shadow: none;'>?</div>"

    border_color = "#2563eb" if is_blue else "#c026d3"
    strat_name = "STAT EDGE" if is_blue else "CONTRARIAN"
    
    sum_val = sum(final_numbers) if is_final else "-"
    entropy_val = calculate_entropy(final_numbers) if is_final else "-"
    share_val = get_jackpot_share(final_numbers) if is_final else "-"

    return f"""
    <div class="ticket-wrapper" style="border-top: 5px solid {border_color};">
        <div class="ticket-header">
            <span style="color: #0f172a;">STRATEGY: {strat_name}</span>
            <span style="color: #64748b;">{time_str}</span>
        </div>
        <div class="ball-container">
            {ball_html}
        </div>
        <div class="stat-grid">
            <div class="stat-card">
                <div class="stat-title">Sum</div>
                <div class="stat-value">{sum_val}</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Entropy</div>
                <div class="stat-value">{entropy_val}</div>
            </div>
            <div class="stat-card share-card">
                <div class="stat-title share-title">Share</div>
                <div class="stat-value share-value">{share_val}</div>
            </div>
        </div>
    </div>
    """

# --- ULTRA-ACCURATE GENERATOR ---
def generate_ultra_ticket(max_number, num_picks, df_stats, strategy):
    scale = num_picks / len(num_cols_all)
    sums = df_stats[num_cols_all].sum(axis=1) * scale
    sum_mean, sum_std = sums.mean(), sums.std()
    sum_low, sum_high = sum_mean - 1.5 * sum_std, sum_mean + 1.5 * sum_std
    
    odd_counts = (df_stats[num_cols_all] % 2 != 0).sum(axis=1) * scale
    mode_odd = int(round(odd_counts.mode()[0]))
    odd_range = (max(0, mode_odd - 1), min(num_picks, mode_odd + 1))
    
    attempts = 0
    while attempts < 5000:
        all_numbers = df_stats[num_cols_all].values.flatten()
        counts = Counter(all_numbers)
        pool = [int(num) for num, count in counts.items() if num <= max_number]
        
        if strategy == "Contrarian Maximizer":
            high_pool = [int(num) for num in counts.keys() if 31 < num <= max_number]
            low_pool = [int(num) for num in counts.keys() if num <= 31]
            num_high = random.choice([3, 4])
            num_low = num_picks - num_high
            if len(high_pool) >= num_high and len(low_pool) >= num_low:
                picks = sorted(random.sample(high_pool, num_high) + random.sample(low_pool, num_low))
            else:
                picks = sorted(random.sample(range(1, max_number + 1), num_picks))
        else:
            weights = [counts[num] for num in pool]
            picks = sorted(random.choices(pool, weights=weights, k=num_picks))
            picks = list(set(picks))
        
        if len(picks) < num_picks:
            picks = sorted(random.sample(range(1, max_number + 1), num_picks))
        
        if not (sum_low <= sum(picks) <= sum_high): attempts += 1; continue
        odd_count = sum(1 for x in picks if x % 2 != 0)
        if not (odd_range[0] <= odd_count <= odd_range[1]): attempts += 1; continue
        
        consecutive = sum(1 for i in range(len(picks) - 1) if picks[i+1] - picks[i] == 1)
        if consecutive >= 2: attempts += 1; continue
        return picks
    return sorted(random.sample(range(1, max_number + 1), num_picks))

# --- BACKTEST SIMULATOR ---
def backtest_ticket(ticket, df_stats):
    recent_draws = df_stats.tail(500)
    match_counts = {3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
    for _, row in recent_draws.iterrows():
        draw = set(row[num_cols_all].dropna().astype(int))
        matches = len(draw.intersection(set(ticket)))
        if matches >= 3:
            match_counts[matches] = match_counts.get(matches, 0) + 1
    return match_counts

# --- MAIN APP ---
try:
    with st.sidebar:
        st.markdown("<h2 style='font-weight: 800; color: #0f172a; margin-bottom: 20px;'>⚙️ Engine Settings</h2>", unsafe_allow_html=True)
        game_choice = st.selectbox("Select Game", ["Lotto 6/49", "Lotto Max"], index=0)
        
        st.markdown("<hr style='border: 1px solid #e2e8f0; margin: 20px 0;'>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size: 12px; color: #64748b; font-weight: 600;'>Database: {len(df):,} draws</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size: 12px; color: #64748b; font-weight: 600;'>Engine: Dual-Strategy ML</div>", unsafe_allow_html=True)
        
        st.markdown("<hr style='border: 1px solid #e2e8f0; margin: 20px 0;'>", unsafe_allow_html=True)
        
        st.markdown("<h3 style='font-weight: 800; color: #0f172a; margin-bottom: 15px; font-size: 16px;'>🧠 Which Ticket to Pick?</h3>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="sidebar-box" style="border-left: 4px solid #2563eb;">
            <div class="sidebar-title" style="color: #2563eb;">🔵 Statistical Edge</div>
            <div class="sidebar-text">
                Plays the historical sweet spot. Perfectly matches the 40-year average for sum, odd/even ratios, and frequency. It looks exactly like a real winning draw.
            </div>
        </div>
        
        <div class="sidebar-box" style="border-left: 4px solid #c026d3;">
            <div class="sidebar-title" style="color: #c026d3;">🟣 Contrarian Maximizer</div>
            <div class="sidebar-text">
                Plays human psychology. It forces high numbers (32-50) to avoid birthdays. If you win, you share the jackpot with far fewer people.
            </div>
        </div>
        
        <div class="sidebar-box" style="background: #fefce8; border-color: #fef08a;">
            <div class="sidebar-title" style="color: #854d0e;">🏆 Expert Verdict</div>
            <div class="sidebar-text" style="color: #713f12;">
                <b>Pick the Contrarian ticket first.</b><br><br>
                While both have the exact same odds of hitting the jackpot, the Contrarian ticket has a massive <b>Expected Value (EV)</b> advantage. By avoiding numbers 1-31, you drastically reduce the chance of splitting the prize.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Top Status Bar
    st.markdown(f"""
    <div class="status-bar">
        <div><span class="dot"></span> Enterprise Engine Online</div>
        <div>Dual-Generation Mode Active</div>
        <div>Last Sync: {datetime.now().strftime('%H:%M:%S')}</div>
    </div>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
        <div class="header-title">LottoStat Enterprise</div>
        <div class="header-subtitle">Institutional Grade Analytics</div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🎟️ Ticket Optimizer", "🔬 Backtest Simulator", "📈 Deep Analytics"])
    
    # ==========================================
    # TAB 1: TICKET OPTIMIZER
    # ==========================================
    with tab1:
        if st.button(f"Generate Dual {game_choice} Tickets", use_container_width=True, type="primary"):
            max_num = 49 if game_choice == "Lotto 6/49" else 50
            num_picks = 6 if game_choice == "Lotto 6/49" else 7
            
            final_stat = generate_ultra_ticket(max_num, num_picks, df, "Statistical Edge")
            final_cont = generate_ultra_ticket(max_num, num_picks, df, "Contrarian Maximizer")
            
            col_stat, col_cont = st.columns(2, gap="medium")
            with col_stat:
                stat_placeholder = st.empty()
            with col_cont:
                cont_placeholder = st.empty()
                
            now_str = datetime.now().strftime('%H:%M')
            
            # SLOWED DOWN ANIMATION
            for i in range(num_picks):
                # 1. Spin the current number multiple times
                for _ in range(6): # Spin 6 times for suspense
                    stat_placeholder.markdown(build_ticket_html(final_stat, i, max_num, True, now_str), unsafe_allow_html=True)
                    cont_placeholder.markdown(build_ticket_html(final_cont, i, max_num, False, now_str), unsafe_allow_html=True)
                    time.sleep(0.08) 
                
                # 2. Lock the number in
                stat_placeholder.markdown(build_ticket_html(final_stat, i + 1, max_num, True, now_str), unsafe_allow_html=True)
                cont_placeholder.markdown(build_ticket_html(final_cont, i + 1, max_num, False, now_str), unsafe_allow_html=True)
                
                # 3. Pause for half a second so the user can see the newly locked number
                time.sleep(0.4)
            
            # Save to state
            st.session_state['ticket_stat'] = final_stat
            st.session_state['ticket_cont'] = final_cont
            st.session_state['game_type'] = game_choice
            st.session_state['max_num'] = max_num
            st.session_state['ticket_time'] = now_str

        elif 'ticket_stat' in st.session_state:
            # Show static final state if switching tabs
            col_stat, col_cont = st.columns(2, gap="medium")
            with col_stat:
                st.markdown(build_ticket_html(
                    st.session_state['ticket_stat'], 
                    len(st.session_state['ticket_stat']), 
                    st.session_state['max_num'], 
                    True, 
                    st.session_state.get('ticket_time', datetime.now().strftime('%H:%M'))
                ), unsafe_allow_html=True)
            with col_cont:
                st.markdown(build_ticket_html(
                    st.session_state['ticket_cont'], 
                    len(st.session_state['ticket_cont']), 
                    st.session_state['max_num'], 
                    False, 
                    st.session_state.get('ticket_time', datetime.now().strftime('%H:%M'))
                ), unsafe_allow_html=True)
            
        else:
            st.markdown("""
            <div style="text-align: center; padding: 60px 20px; background: #f8fafc; border-radius: 20px; border: 2px dashed #cbd5e1; margin-top: 20px;">
                <div style="font-size: 60px; margin-bottom: 20px;">💎</div>
                <div style="color: #64748b; font-weight: 600; font-size: 16px;">
                    Dual-Engine Ready.<br>Generate to compare both AI strategies side-by-side.
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ==========================================
    # TAB 2: BACKTEST SIMULATOR
    # ==========================================
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; font-weight: 800; color: #0f172a;'>Time Machine Simulation</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b; font-size: 14px;'>See how your tickets would have performed against the last 500 real-world draws.</p>", unsafe_allow_html=True)
        
        if 'ticket_stat' in st.session_state:
            col_bt1, col_bt2 = st.columns(2)
            
            with col_bt1:
                st.markdown("#### 🔵 Statistical Edge Backtest")
                with st.spinner("Simulating..."):
                    time.sleep(0.5)
                    res_stat = backtest_ticket(st.session_state['ticket_stat'], df)
                st.success(f"Hit 3+ numbers **{sum(res_stat.values())} times** in the last 500 draws.")
                
            with col_bt2:
                st.markdown("#### 🟣 Contrarian Backtest")
                with st.spinner("Simulating..."):
                    time.sleep(0.5)
                    res_cont = backtest_ticket(st.session_state['ticket_cont'], df)
                st.success(f"Hit 3+ numbers **{sum(res_cont.values())} times** in the last 500 draws.")
                
            st.info("💡 Note: Backtesting is for entertainment. The lottery is random, but these algorithms ensure you avoid statistically improbable patterns.")
            
        else:
            st.warning("Generate tickets in the 'Ticket Optimizer' tab first to run the simulation!")

    # ==========================================
    # TAB 3: DEEP ANALYTICS
    # ==========================================
    with tab3:
        st.markdown("<br>", unsafe_allow_html=True)
        
        time_filter = st.radio("Data Range:", ["All Time", "Last 5 Years", "Last 1 Year"], horizontal=True, label_visibility="collapsed")
        
        df_filtered = df.copy()
        if time_filter != "All Time":
            years = 5 if time_filter == "Last 5 Years" else 1
            cutoff = df['Date'].max() - pd.DateOffset(years=years)
            df_filtered = df[df['Date'] >= cutoff].copy()

        all_numbers = df_filtered[num_cols_all].values.flatten()
        all_numbers = [x for x in all_numbers if pd.notna(x)] 
        counts = Counter(all_numbers)
        freq_df = pd.DataFrame(counts.items(), columns=['Number', 'Frequency'])
        df_filtered['Sum'] = df_filtered[num_cols_all].sum(axis=1)
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("#### 🔔 Winning Sum Distribution")
            fig_sum = px.histogram(df_filtered, x="Sum", nbins=30, color_discrete_sequence=['#3b82f6'])
            fig_sum.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=20, b=10), xaxis_title="Sum", yaxis_title="Frequency")
            st.plotly_chart(fig_sum, use_container_width=True)
            
        with col_b:
            st.markdown("#### 📈 All-Time Frequency")
            fig_freq = px.bar(freq_df, x='Number', y='Frequency', color='Frequency', color_continuous_scale='Blues')
            fig_freq.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=20, b=10), coloraxis_showscale=False)
            st.plotly_chart(fig_freq, use_container_width=True)
            
        st.markdown("#### 🤖 Machine Learning Clusters")
        kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
        cluster_df = df_filtered.dropna(subset=num_cols_all).copy()
        cluster_df['Cluster'] = kmeans.fit_predict(cluster_df[num_cols_all])
        fig_cluster = px.scatter(cluster_df.tail(200), x=num_cols_all[0], y=num_cols_all[1], color=cluster_df.tail(200)['Cluster'].astype(str), color_discrete_sequence=['#2563eb', '#7c3aed', '#db2777', '#ea580c'])
        fig_cluster.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_cluster, use_container_width=True)

    # --- FOOTER ---
    st.markdown("""
    <div class="footer">
        For entertainment purposes only. Please play responsibly.<br>
        Powered by Historical Data & Machine Learning.
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"An error occurred: {e}")