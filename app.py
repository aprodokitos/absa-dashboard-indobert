import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Dashboard ABSA - Kurs Dolar/Rupiah",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Clean Dark Theme CSS & Typography (Inter Font) ───────────────────
st.markdown("""
    <style>
    /* Import Inter Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Apply Inter font globally and force dark mode colors */
    html, body, [class*="css"], .stMarkdown, p, span, h1, h2, h3, h4, li, label {
        font-family: 'Inter', 'Segoe UI', sans-serif !important;
        color: #f8fafc !important;
    }
    
    /* Force main app background to softer dark black (Zinc 950) */
    .stApp {
        background-color: #09090b !important;
    }
    
    /* Style all native Streamlit containers with border to look like clean dark cards */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #121214 !important;
        border: 1px solid #222226 !important;
        border-radius: 10px !important;
        padding: 1.2rem !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.15), 0 2px 4px -1px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Force container cards inside columns to stretch to equal height */
    div[data-testid="column"] > div[data-testid="stVerticalBlock"] {
        height: 100% !important;
        display: flex !important;
        flex-direction: column !important;
    }
    div[data-testid="column"] > div[data-testid="stVerticalBlock"] > div {
        height: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        flex: 1 !important;
    }
    div[data-testid="column"] div[data-testid="stVerticalBlockBorderWrapper"] {
        height: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        flex: 1 !important;
    }
    
    /* Remove outer border/background from stVerticalBlockBorderWrapper if it contains the scoreboard-row */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.scoreboard-row) {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        height: auto !important;
    }
    
    /* Hide top decoration bar and default footer */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Remove excessive top padding */
    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 2.5rem;
    }
    
    /* Custom Scoreboard CSS Row & Card Layout */
    .scoreboard-row {
        display: flex;
        gap: 20px;
        width: 100%;
        margin-bottom: 30px;
        box-sizing: border-box;
    }
    
    .score-card {
        flex: 1;
        text-align: center;
        background-color: #121214;
        border: 1px solid #222226;
        border-radius: 10px;
        padding: 22px 15px;
        height: 195px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
        box-sizing: border-box;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.15), 0 2px 4px -1px rgba(0, 0, 0, 0.1);
    }
    
    .score-header {
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        color: #a1a1aa !important; /* Zinc 400 */
        letter-spacing: 0.02em;
        text-transform: none; /* Do not force uppercase */
        margin: 0;
    }
    
    .score-val {
        font-size: 2.4rem !important;
        font-weight: 800 !important;
        color: #38bdf8 !important; /* Sky blue accent */
        margin: 12px 0 !important;
        line-height: 1.1;
    }
    
    .score-desc {
        font-size: 0.78rem !important;
        color: #71717a !important; /* Zinc 500 */
        margin: 0;
        line-height: 1.3;
    }
    
    /* EWS State Styles */
    .ews-green {
        background-color: #166534 !important;
        border: 1px solid #22c55e !important;
    }
    .ews-green .score-header {
        color: #86efac !important;
    }
    .ews-green .score-val {
        color: #ffffff !important;
    }
    .ews-green .score-desc {
        color: #86efac !important;
    }
    
    .ews-yellow {
        background-color: #78350f !important;
        border: 1px solid #eab308 !important;
    }
    .ews-yellow .score-header {
        color: #fef08a !important;
    }
    .ews-yellow .score-val {
        color: #ffffff !important;
    }
    .ews-yellow .score-desc {
        color: #fef08a !important;
    }
    
    .ews-red {
        background-color: #7f1d1d !important;
        border: 1px solid #ef4444 !important;
    }
    .ews-red .score-header {
        color: #fca5a5 !important;
    }
    .ews-red .score-val {
        color: #ffffff !important;
    }
    .ews-red .score-desc {
        color: #fca5a5 !important;
    }
    
    /* Responsive layout for smaller screens */
    @media (max-width: 992px) {
        .scoreboard-row {
            flex-direction: column;
            gap: 15px;
        }
        .score-card {
            width: 100%;
            height: 180px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# =====================================================
# LOAD DATA & CALCULATIONS
# =====================================================
def parse_engagement_val(val):
    if pd.isna(val):
        return 0
    val_str = str(val).strip().replace('\xa0', ' ').upper()
    if not val_str:
        return 0
    
    # check for RB (ribu / thousand)
    if 'RB' in val_str:
        try:
            num = val_str.replace('RB', '').strip().replace(',', '.')
            return int(float(num) * 1000)
        except ValueError:
            return 0
            
    # check for JT (juta / million)
    if 'JT' in val_str:
        try:
            num = val_str.replace('JT', '').strip().replace(',', '.')
            return int(float(num) * 1000000)
        except ValueError:
            return 0
            
    # check for K (thousand)
    if 'K' in val_str:
        try:
            num = val_str.replace('K', '').strip().replace(',', '.')
            return int(float(num) * 1000)
        except ValueError:
            return 0
            
    try:
        # standard integer parsing
        return int(float(val_str))
    except ValueError:
        return 0

@st.cache_data
def load_data():
    df = pd.read_csv("data/dolar_rupiah.csv")
    for col in ['replies', 'retweets', 'likes']:
        if col in df.columns:
            df[col] = df[col].apply(parse_engagement_val)
    return df

df_full = load_data()
df_full = df_full.dropna(subset=['timestamp'])
df_full['date'] = pd.to_datetime(df_full['timestamp']).dt.date
df_full['engagement'] = df_full['likes'] + df_full['retweets'] + df_full['replies']

# Load model live using Streamlit cache
from utils.model_loader import load_model, predict

@st.cache_resource
def get_model():
    try:
        return load_model()
    except Exception as e:
        return None, None

model, tokenizer = get_model()

min_date = df_full['date'].min()
max_date = df_full['date'].max()

# =====================================================
# 1. HEADER SECTION (with expanded spacing)
# =====================================================
st.markdown("<h1 style='font-weight: 800; font-size: 2.5rem; margin-bottom: 30px;'>Dashboard Deteksi Respon Publik Terhadap Kenaikan Kurs Dolar AS / Rupiah</h1>", unsafe_allow_html=True)

# =====================================================
# 1.5 FILTER WAKTU ANALISIS (On Main Page, Above Scoreboard)
# =====================================================
col_f1, col_f2 = st.columns([2, 3])
with col_f1:
    time_option = st.selectbox(
        "📅 Pilih Rentang Waktu (Khusus Scoreboard & EWS):",
        ["Semua Data", "7 Hari Terakhir", "30 Hari Terakhir", "Rentang Kustom"],
        label_visibility="visible"
    )
with col_f2:
    if time_option == "Rentang Kustom":
        date_range = st.date_input(
            "📅 Pilih Rentang Tanggal (Khusus Scoreboard & EWS):",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            label_visibility="visible"
        )
        if len(date_range) == 2:
            start_filter, end_filter = date_range
        else:
            start_filter = min_date
            end_filter = max_date
    else:
        if time_option == "7 Hari Terakhir":
            start_filter = max_date - timedelta(days=6)
            end_filter = max_date
        elif time_option == "30 Hari Terakhir":
            start_filter = max_date - timedelta(days=29)
            end_filter = max_date
        else:
            start_filter = min_date
            end_filter = max_date
        st.write("") # Spacer

# Filter the dataframe for the Scoreboard ONLY
df_scoreboard = df_full[(df_full['date'] >= start_filter) & (df_full['date'] <= end_filter)]

# Safety check for empty scoreboard dataframe
if df_scoreboard.empty:
    st.warning("Tidak ada data opini pada rentang waktu yang terpilih untuk Scoreboard. Silakan pilih rentang waktu lain.")
    st.stop()

# Calculate metrics for Scoreboard (using df_scoreboard)
total_tweets = len(df_scoreboard)
total_engagement = df_scoreboard['engagement'].sum()
range_neg = (df_scoreboard['sentiment'] == 'Negatif').sum()
range_panic = round((range_neg / total_tweets * 100), 2) if total_tweets > 0 else 0.0

if range_panic > 60:
    alert_status = "RED ALERT"
    alert_class = "ews-red"
    alert_desc = "Kepanikan tinggi, disarankan intervensi pasar valas"
elif range_panic >= 45:
    alert_status = "YELLOW ALERT"
    alert_class = "ews-yellow"
    alert_desc = "Waspada volatilitas, pantau pergerakan sentimen"
else:
    alert_status = "GREEN ALERT"
    alert_class = "ews-green"
    alert_desc = "Persepsi publik aman, kondisi pasar stabil"

# Use full dataset for the rest of the dashboard components
df = df_full

# Daily statistics computed on full dataset (df = df_full)
daily_stats = df.groupby('date').agg(
    total_tweets=('text', 'count'),
    neg_tweets=('sentiment', lambda x: (x == 'Negatif').sum())
).reset_index()
daily_stats['panic_index'] = (daily_stats['neg_tweets'] / daily_stats['total_tweets'] * 100).round(2)
daily_stats = daily_stats.sort_values('date')
daily_stats['panic_index_ma'] = daily_stats['panic_index'].rolling(window=3, min_periods=1).mean().round(2)

# =====================================================
# 2. ROW 1: SCOREBOARD (CONSOLIDATED HTML ROW)
# =====================================================
st.markdown(f"""
<div class="scoreboard-row">
    <!-- Card 1 -->
    <div class="score-card">
        <div class="score-header">Total Opini (Tweet)</div>
        <div class="score-val">{total_tweets:,}</div>
        <div class="score-desc">Keseluruhan data opini di-crawling dari platform X</div>
    </div>
    <!-- Card 2 -->
    <div class="score-card">
        <div class="score-header">Total Engagement</div>
        <div class="score-val">{total_engagement:,}</div>
        <div class="score-desc">Jumlah akumulasi Likes, Retweets, dan Replies</div>
    </div>
    <!-- Card 3 -->
    <div class="score-card">
        <div class="score-header">Indeks Kepanikan (Rata-Rata)</div>
        <div class="score-val">{range_panic}%</div>
        <div class="score-desc">Rasio sentimen negatif rata-rata periode terpilih</div>
    </div>
    <!-- Card 4 (EWS) -->
    <div class="score-card ews-card {alert_class}">
        <div class="score-header">Status Sistem (EWS)</div>
        <div class="score-val">{alert_status}</div>
        <div class="score-desc">{alert_desc}</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")

# =====================================================
# 2.5 ROW 1.5: RANDOM TWEETS SAMPLE WITH PREDICTIONS
# =====================================================
# Initialize session state for selected tweets if not exist, or if current indices are invalid in filtered df
if 'selected_tweet_indices' not in st.session_state:
    st.session_state.selected_tweet_indices = df.sample(min(5, len(df))).index.tolist()
else:
    # Filter only indices that actually exist in the current filtered dataframe
    valid_indices = [idx for idx in st.session_state.selected_tweet_indices if idx in df.index]
    if len(valid_indices) < min(5, len(df)):
        st.session_state.selected_tweet_indices = df.sample(min(5, len(df))).index.tolist()
    else:
        st.session_state.selected_tweet_indices = valid_indices

with st.container(border=True):
    col_title, col_btn = st.columns([5, 1.2])
    with col_title:
        st.markdown("<h3 style='font-size: 1.4rem; font-weight: 700; margin-bottom: 5px; color: #f8fafc;'>🔍 Sampel Opini Publik & Analisis Model ABSA</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #71717a; margin-bottom: 0; font-size: 0.85rem;'>Daftar opini acak beserta hasil prediksi aspek, sentimen, dan tingkat keyakinan (confidence) dari model fine-tuned IndoBERT.</p>", unsafe_allow_html=True)
    with col_btn:
        st.write("") # vertical alignment spacer
        # If the button is clicked, resample new indices for current run
        if st.button("Acak Sampel 🔄", use_container_width=True):
            st.session_state.selected_tweet_indices = df.sample(min(5, len(df))).index.tolist()
            
    # Show warning if model is missing
    if model is None or tokenizer is None:
        st.warning("⚠️ Berkas bobot model (`pytorch_model.bin`) tidak ditemukan di `/model/model_indobert_absa/`. Prediksi langsung dinonaktifkan, menampilkan nilai default bawaan dari dataset.")

    # Load selected data safely using list comprehension to prevent KeyError
    selected_indices = [idx for idx in st.session_state.selected_tweet_indices if idx in df.index]
    if not selected_indices:
        selected_indices = df.sample(min(5, len(df))).index.tolist()
        st.session_state.selected_tweet_indices = selected_indices
    selected_df = df.loc[selected_indices]
    
    # Render table rows using safe string concatenation to avoid template errors from raw text
    import html
    import hashlib
    
    html_rows = []
    for idx, row in selected_df.iterrows():
        username = html.escape(str(row['username'])) if pd.notna(row['username']) else "anon"
        username = username.lstrip('@')
        display_name = html.escape(str(row['display_name'])) if pd.notna(row['display_name']) else "User X"
        tweet_text = html.escape(str(row['text'])) if pd.notna(row['text']) else ""
        
        if model is None or tokenizer is None:
            aspect = str(row['aspect']) if pd.notna(row['aspect']) else "Umum"
            sentiment = str(row['sentiment']) if pd.notna(row['sentiment']) else "Netral"
            confidence = 100.0
        else:
            # Live prediction using fine-tuned IndoBERT
            raw_text = str(row['text']) if pd.notna(row['text']) else ""
            pred_aspect, pred_sentiment, aspect_conf, sentiment_conf = predict(
                raw_text, model, tokenizer
            )
            # Average confidence score of aspect and sentiment classifications
            confidence = round((aspect_conf + sentiment_conf) / 2.0, 1)
            aspect = pred_aspect
            sentiment = pred_sentiment
        
        # Sentiment badge style
        if sentiment == 'Positif':
            sent_badge = '<span style="display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 700; background-color: #166534; color: #86efac; border: 1px solid #22c55e;">Positif</span>'
        elif sentiment == 'Negatif':
            sent_badge = '<span style="display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 700; background-color: #7f1d1d; color: #fca5a5; border: 1px solid #ef4444;">Negatif</span>'
        else:
            sent_badge = '<span style="display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 700; background-color: #27272a; color: #a1a1aa; border: 1px solid #3f3f46;">Netral</span>'
            
        # Aspect colors mapped to match colors of Sebaran Aspek & Matriks
        COLORS_ASPECT = {
            'Ekonomi nasional': '#1e40af',
            'Umum': '#3b82f6',
            'Harga barang': '#60a5fa',
            'Investasi': '#93c5fd',
            'Ekspor': '#bfdbfe'
        }
        asp_color = COLORS_ASPECT.get(aspect, '#3b82f6')
        
        aspect_badge = '<span style="display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; background-color: ' + asp_color + '1a; color: ' + asp_color + '; border: 1px solid ' + asp_color + '; white-space: nowrap;">' + aspect + '</span>'
        
        row_html = (
            '<tr style="border-bottom: 1px solid #222226;">'
            '<td style="padding: 12px 10px; text-align: left; vertical-align: top;">'
            '<div style="font-weight: 600; font-size: 0.85rem; color: #38bdf8; margin-bottom: 5px;">@' + username + ' <span style="color: #71717a; font-weight: 400;">• ' + display_name + '</span></div>'
            '<div style="font-size: 0.88rem; line-height: 1.4; color: #f4f4f5;">' + tweet_text + '</div>'
            '</td>'
            '<td style="padding: 12px 10px; text-align: center; vertical-align: middle;">' + aspect_badge + '</td>'
            '<td style="padding: 12px 10px; text-align: center; vertical-align: middle;">' + sent_badge + '</td>'
            '<td style="padding: 12px 10px; text-align: center; vertical-align: middle; font-weight: 700; color: #fafafa; font-size: 0.9rem;">' + str(confidence) + '%</td>'
            '</tr>'
        )
        html_rows.append(row_html)

    tbody_content = "".join(html_rows)
    table_html = (
        '<table style="width: 100%; border-collapse: collapse; margin-top: 15px;">'
        '<thead>'
        '<tr style="border-bottom: 2px solid #222226; text-align: left;">'
        '<th style="padding: 10px; color: #a1a1aa; font-weight: 600; font-size: 0.85rem; text-align: left;">Opini Publik (Tweet)</th>'
        '<th style="padding: 10px; color: #a1a1aa; font-weight: 600; font-size: 0.85rem; width: 160px; text-align: center;">Aspek</th>'
        '<th style="padding: 10px; color: #a1a1aa; font-weight: 600; font-size: 0.85rem; width: 120px; text-align: center;">Sentimen</th>'
        '<th style="padding: 10px; color: #a1a1aa; font-weight: 600; font-size: 0.85rem; width: 130px; text-align: center;">Confidence</th>'
        '</tr>'
        '</thead>'
        '<tbody>' + tbody_content + '</tbody>'
        '</table>'
    )
    st.markdown(table_html, unsafe_allow_html=True)
st.write("")

# =====================================================
# 3. ROW 2: CHART DISTRIBUSI SENTIMEN & ASPEK
# =====================================================
col_dist1, col_dist2 = st.columns(2)

with col_dist1:
    with st.container(border=True):
        st.markdown("<h3 style='font-size: 1.3rem; font-weight: 600; margin-bottom: 10px;'>Sebaran Sentimen Publik</h3>", unsafe_allow_html=True)
        st.write("")
        sent_counts = df['sentiment'].value_counts().reset_index()
        sent_counts.columns = ['Sentimen', 'Jumlah']
        COLORS_SENT = {'Negatif': '#ef4444', 'Netral': '#f59e0b', 'Positif': '#22c55e'}
        
        # Create bar chart without 'color' grouping to keep bars centered on x-axis labels
        fig_sent = px.bar(
            sent_counts,
            x='Sentimen',
            y='Jumlah',
            text='Jumlah',
            template="plotly_dark",
            height=300
        )
        
        # Color each bar according to its category directly on the trace
        marker_colors = [COLORS_SENT.get(s, '#94a3b8') for s in sent_counts['Sentimen']]
        
        fig_sent.update_traces(
            textposition='outside',
            cliponaxis=False,
            marker_color=marker_colors
        )
        
        # Give Y axis headroom (15% extra) to prevent value labels from being cut off
        max_sent_val = sent_counts['Jumlah'].max() if not sent_counts.empty else 100
        fig_sent.update_yaxes(range=[0, max_sent_val * 1.15])
        
        fig_sent.update_layout(
            showlegend=False,
            margin=dict(l=10, r=10, t=25, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_sent, use_container_width=True)
        st.markdown("<p style='font-size: 0.85rem; color: #a1a1aa; border-top: 1px solid #222226; padding-top: 10px; margin-top: 10px;'>💡 <b>Insight:</b> Mayoritas opini publik bersentimen <b>Negatif</b>, menunjukkan kekhawatiran dan ketidakpuasan masyarakat yang mendalam terhadap pelemahan nilai tukar Rupiah.</p>", unsafe_allow_html=True)

with col_dist2:
    with st.container(border=True):
        st.markdown("<h3 style='font-size: 1.3rem; font-weight: 600; margin-bottom: 10px;'>Sebaran Aspek yang Dibahas</h3>", unsafe_allow_html=True)
        st.write("")
        asp_counts = df['aspect'].value_counts().reset_index()
        asp_counts.columns = ['Aspek', 'Jumlah']
        
        # Custom color mapping for consistency with risk matrix
        COLORS_ASPECT = {
            'Ekonomi nasional': '#1e40af',
            'Umum': '#3b82f6',
            'Harga barang': '#60a5fa',
            'Investasi': '#93c5fd',
            'Ekspor': '#bfdbfe'
        }
        
        fig_asp = px.bar(
            asp_counts,
            x='Aspek',
            y='Jumlah',
            text='Jumlah',
            template="plotly_dark",
            height=300
        )
        
        marker_colors_asp = [COLORS_ASPECT.get(a, '#94a3b8') for a in asp_counts['Aspek']]
        
        fig_asp.update_traces(
            textposition='outside',
            cliponaxis=False,
            marker_color=marker_colors_asp
        )
        
        # Give Y axis headroom (15% extra) to prevent value labels from being cut off
        max_asp_val = asp_counts['Jumlah'].max() if not asp_counts.empty else 100
        fig_asp.update_yaxes(range=[0, max_asp_val * 1.15])
        
        fig_asp.update_layout(
            margin=dict(l=10, r=10, t=25, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_asp, use_container_width=True)
        st.markdown("<p style='font-size: 0.85rem; color: #a1a1aa; border-top: 1px solid #222226; padding-top: 10px; margin-top: 10px;'>💡 <b>Insight:</b> Aspek <b>Ekonomi nasional</b> dan <b>Harga barang</b> menjadi fokus utama warganet, menandakan kekhawatiran terbesar berpusat pada stabilitas makro dan inflasi riil.</p>", unsafe_allow_html=True)

st.write("")

# =====================================================
# 3.5 ROW 2.5: RATA-RATA KETERLIBATAN PUBLIK PER ASPEK (NEW CHART)
# =====================================================
with st.container(border=True):
    st.markdown("<h3 style='font-size: 1.3rem; font-weight: 600; margin-bottom: 5px;'>Rata-Rata Keterlibatan Publik (Average Engagement) per Aspek</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #71717a; margin-bottom: 15px; font-size: 0.85rem;'>Menampilkan rata-rata jumlah interaksi publik (Likes + Retweets + Replies) pada setiap aspek ekonomi. Membantu mengidentifikasi topik mana yang paling memicu respons aktif warganet.</p>", unsafe_allow_html=True)
    
    # Calculate engagement stats per aspect on currently filtered dataframe
    engage_stats = df.groupby('aspect')['engagement'].mean().reset_index()
    engage_stats = engage_stats.sort_values('engagement', ascending=False)
    
    # Custom color mapping for consistency
    COLORS_ASPECT = {
        'Ekonomi nasional': '#1e40af',
        'Umum': '#3b82f6',
        'Harga barang': '#60a5fa',
        'Investasi': '#93c5fd',
        'Ekspor': '#bfdbfe'
    }
    
    # Create horizontal bar chart so labels are fully readable
    fig_engage = px.bar(
        engage_stats,
        y='aspect',
        x='engagement',
        text='engagement',
        orientation='h',
        labels={'aspect': 'Aspek Ekonomi', 'engagement': 'Rata-Rata Engagement'},
        template="plotly_dark",
        height=280
    )
    
    marker_colors_engage = [COLORS_ASPECT.get(a, '#94a3b8') for a in engage_stats['aspect']]
    
    fig_engage.update_traces(
        texttemplate='%{x:.1f}',
        textposition='outside',
        cliponaxis=False,
        marker_color=marker_colors_engage,
        hovertemplate="<b>%{y}</b><br>Rata-Rata Engagement: %{x:.1f}<extra></extra>"
    )
    
    # Give X axis headroom (15% extra) to prevent value labels from being cut off
    max_engage_val = engage_stats['engagement'].max() if not engage_stats.empty else 10
    fig_engage.update_xaxes(range=[0, max_engage_val * 1.15])
    
    fig_engage.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    st.plotly_chart(fig_engage, use_container_width=True)
    st.markdown("<p style='font-size: 0.85rem; color: #a1a1aa; border-top: 1px solid #222226; padding-top: 10px; margin-top: 10px;'>💡 <b>Insight:</b> Topik <b>Investasi</b> dan <b>Ekonomi nasional</b> memicu respons publik paling aktif per tweet, mengindikasikan sensitivitas tinggi terhadap isu penanaman modal dan makroekonomi.</p>", unsafe_allow_html=True)

st.write("")

# =====================================================
# 4. ROW 3: PANIC TREND & PRIORITY-RISK MATRIX
# =====================================================
col_trend1, col_trend2 = st.columns(2)

with col_trend1:
    with st.container(border=True):
        st.markdown("<h3 style='font-size: 1.3rem; font-weight: 600; margin-bottom: 10px;'>Tren Indeks Kepanikan Publik Harian</h3>", unsafe_allow_html=True)
        st.write("")
        fig_ews = px.line(
            daily_stats,
            x="date",
            y=["panic_index", "panic_index_ma"],
            labels={"value": "Persentase (%)", "date": "Tanggal"},
            template="plotly_dark",
            color_discrete_sequence=["#fca5a5", "#ef4444"],
            height=300
        )
        newnames = {'panic_index': 'Kepanikan Harian', 'panic_index_ma': 'Kepanikan (3-Day MA)'}
        fig_ews.for_each_trace(lambda t: t.update(name=newnames[t.name]))
        fig_ews.add_hline(y=60, line_dash="dash", line_color="#ef4444")
        fig_ews.add_hline(y=45, line_dash="dash", line_color="#f59e0b")
        fig_ews.update_layout(
            legend=dict(x=0.01, y=0.99, bgcolor="rgba(18,18,20,0.7)"),
            legend_title_text="",
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_ews, use_container_width=True)
        st.markdown("<p style='font-size: 0.85rem; color: #a1a1aa; border-top: 1px solid #222226; padding-top: 10px; margin-top: 10px;'>💡 <b>Insight:</b> Indeks Kepanikan mengalami lonjakan periodik yang tajam. Pola Moving Average (3-Day MA) membantu meredam gejolak harian untuk melihat pergeseran tren kepanikan yang lebih stabil.</p>", unsafe_allow_html=True)

with col_trend2:
    with st.container(border=True):
        st.markdown("<h3 style='font-size: 1.3rem; font-weight: 600; margin-bottom: 10px;'>Matriks Prioritas Risiko Aspek (Priority-Risk Matrix)</h3>", unsafe_allow_html=True)
        st.write("")
        aspect_stats = df.groupby('aspect').agg(
            urgency_volume=('text', 'count'),
            neg_tweets=('sentiment', lambda x: (x == 'Negatif').sum()),
            total_engagement=('engagement', 'sum')
        ).reset_index()
        aspect_stats['severity_pct'] = (aspect_stats['neg_tweets'] / aspect_stats['urgency_volume'] * 100).round(2)
        
        # Custom color mapping for consistency
        COLORS_ASPECT = {
            'Ekonomi nasional': '#1e40af',
            'Umum': '#3b82f6',
            'Harga barang': '#60a5fa',
            'Investasi': '#93c5fd',
            'Ekspor': '#bfdbfe'
        }
        
        fig_matrix = px.scatter(
            aspect_stats,
            x="severity_pct",
            y="urgency_volume",
            size="total_engagement",
            color="aspect",
            color_discrete_map=COLORS_ASPECT,
            hover_name="aspect",
            labels={
                "severity_pct": "Tingkat Keparahan (% Negatif)",
                "urgency_volume": "Tingkat Urgensi (Volume)",
                "total_engagement": "Dampak Sosial (Engagement)"
            },
            template="plotly_dark",
            size_max=35,
            height=300
        )
        x_mean = 50.0
        y_mean = aspect_stats['urgency_volume'].mean()
        fig_matrix.add_vline(x=x_mean, line_dash="dot", line_color="#94a3b8")
        fig_matrix.add_hline(y=y_mean, line_dash="dot", line_color="#94a3b8")
        fig_matrix.update_layout(
            legend_title_text="Aspek Ekonomi",
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_matrix, use_container_width=True)
        st.markdown("<p style='font-size: 0.85rem; color: #a1a1aa; border-top: 1px solid #222226; padding-top: 10px; margin-top: 10px;'>💡 <b>Insight:</b> <b>Ekonomi nasional</b> dan <b>Harga barang</b> berada di kuadran risiko prioritas tinggi (keparahan dan volume di atas rata-rata), memerlukan perhatian kebijakan utama.</p>", unsafe_allow_html=True)

st.write("")

# =====================================================
# 5. ROW 4: DUAL-AXIS CORRELATION CHART
# =====================================================
with st.container(border=True):
    st.markdown("<h3 style='font-size: 1.3rem; font-weight: 600; margin-bottom: 10px;'>Korelasi Tren Sentimen vs Pergerakan Kurs USD/IDR Aktual</h3>", unsafe_allow_html=True)
    st.write("")
    try:
        import yfinance as yf
        start_date = str(daily_stats['date'].min())
        end_date = str(daily_stats['date'].max() + timedelta(days=1))
        
        kurs_df = yf.download('IDR=X', start=start_date, end=end_date, auto_adjust=True)
        if not kurs_df.empty:
            kurs_close = kurs_df['Close'].squeeze()
            kurs_series = kurs_close.reindex(pd.to_datetime(daily_stats['date']), method='ffill')
            
            fig_dual = go.Figure()
            
            # Volume of negative tweets
            fig_dual.add_trace(
                go.Bar(
                    x=daily_stats['date'],
                    y=daily_stats['neg_tweets'],
                    name="Volume Tweet Negatif",
                    marker_color='#ef4444',
                    opacity=0.3,
                    yaxis="y1"
                )
            )
            
            # Exchange rate close
            fig_dual.add_trace(
                go.Scatter(
                    x=daily_stats['date'],
                    y=kurs_series.values,
                    name="Kurs USD/IDR Aktual",
                    line=dict(color='#38bdf8', width=3),
                    yaxis="y2"
                )
            )
            
            fig_dual.update_layout(
                template='plotly_dark',
                height=350,
                yaxis=dict(
                    title="Volume Tweet Negatif Harian",
                    titlefont=dict(color="#ef4444"),
                    tickfont=dict(color="#ef4444")
                ),
                yaxis2=dict(
                    title="Kurs USD/IDR (Rupiah)",
                    titlefont=dict(color="#38bdf8"),
                    tickfont=dict(color="#38bdf8"),
                    anchor="x",
                    overlaying="y",
                    side="right",
                    tickformat=",.0f"
                ),
                legend=dict(x=0.01, y=0.99, bgcolor="rgba(18,18,20,0.7)"),
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_dual, use_container_width=True)
            st.markdown("<p style='font-size: 0.85rem; color: #a1a1aa; border-top: 1px solid #222226; padding-top: 10px; margin-top: 10px;'>💡 <b>Insight:</b> Terlihat adanya korelasi positif yang kuat: setiap kali terjadi depresiasi Rupiah yang signifikan (kurs USD/IDR melonjak), volume opini negatif publik di platform X ikut melonjak secara simultan.</p>", unsafe_allow_html=True)
        else:
            st.warning("Data kurs dari Yahoo Finance kosong. Menampilkan volume tweet harian saja.")
    except Exception as e:
        st.warning(f"Gagal memuat data kurs aktual: {e}")

# =====================================================
# 6. ROW 5: INSIGHT & IMPLIKASI STAKEHOLDER (NEW SECTION)
# =====================================================
st.write("")
with st.container(border=True):
    st.markdown("<h3 style='font-size: 1.4rem; font-weight: 700; margin-bottom: 5px; color: #f8fafc;'>📌 Ringkasan Implikasi untuk Stakeholder</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #71717a; margin-bottom: 20px; font-size: 0.85rem;'>Dampak strategis fluktuasi sentimen publik dan kurs USD/IDR terhadap pembuat kebijakan dan pelaku industri.</p>", unsafe_allow_html=True)
    
    col_s1, col_s2, col_s3 = st.columns(3)
    
    with col_s1:
        st.markdown(
            """
            <div style='background-color: #18181b; border: 1px solid #27272a; border-radius: 8px; padding: 15px; height: 100%;'>
                <h4 style='font-size: 1rem; font-weight: 600; color: #38bdf8; margin-top: 0; margin-bottom: 10px;'>🏦 Otoritas Moneter (Bank Indonesia/Pemerintah)</h4>
                <p style='font-size: 0.82rem; color: #d4d4d8; line-height: 1.4; margin: 0;'>
                    <b>Implikasi:</b> Gunakan indeks kepanikan media sosial sebagai indikator pendukung intervensi pasar spot/DNDF untuk menenangkan kepanikan sebelum bertransmisi ke kepanikan fisik (spekulasi valas).
                </p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    with col_s2:
        st.markdown(
            """
            <div style='background-color: #18181b; border: 1px solid #27272a; border-radius: 8px; padding: 15px; height: 100%;'>
                <h4 style='font-size: 1rem; font-weight: 600; color: #fb923c; margin-top: 0; margin-bottom: 10px;'>🏬 Pelaku Industri & Importir</h4>
                <p style='font-size: 0.82rem; color: #d4d4d8; line-height: 1.4; margin: 0;'>
                    <b>Implikasi:</b> Tingginya urgensi aspek 'harga barang' menuntut importir melakukan lindung nilai (hedging) valas dan menyesuaikan strategi rantai pasok guna memitigasi kenaikan biaya produksi.
                </p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    with col_s3:
        st.markdown(
            """
            <div style='background-color: #18181b; border: 1px solid #27272a; border-radius: 8px; padding: 15px; height: 100%;'>
                <h4 style='font-size: 1rem; font-weight: 600; color: #34d399; margin-top: 0; margin-bottom: 10px;'>💼 Investor & Pelaku Pasar Keuangan</h4>
                <p style='font-size: 0.82rem; color: #d4d4d8; line-height: 1.4; margin: 0;'>
                    <b>Implikasi:</b> Puncak kepanikan publik di media sosial sering kali mendahului aksi jual masif di pasar modal. Investor dapat menggunakan tren harian ini untuk menyesuaikan portofolio aset defensif secara dini.
                </p>
            </div>
            """, 
            unsafe_allow_html=True
        )
