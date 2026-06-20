import streamlit as st
import sys

st.set_page_config(
    page_title="ABSA Dashboard - Kurs Dolar/Rupiah",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================
# CUSTOM CSS
# ======================

st.markdown("""
<style>

[data-testid="stSidebar"] {
    background-color: #0f172a;
}

[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

.metric-card {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}

.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #38bdf8;
}

.metric-label {
    font-size: 0.85rem;
    color: #94a3b8;
}

h1, h2, h3 {
    color: #f1f5f9 !important;
}

</style>
""", unsafe_allow_html=True)

# ======================
# HEADER
# ======================

st.title(
    "📊 Dashboard ABSA — Respons Publik terhadap Kenaikan Kurs Dolar AS/Rupiah"
)

st.info(
    "👈 Pilih halaman dari sidebar untuk memulai eksplorasi dashboard.",
    icon="ℹ️"
)

# ======================
# DEBUG ENVIRONMENT
# ======================

st.subheader("🔧 Informasi Environment")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Python")

    st.code(sys.executable)

with col2:
    st.markdown("### Status Torch")

    try:
        import torch

        st.success("Torch berhasil dimuat")

        st.write(
            f"Versi Torch: {torch.__version__}"
        )

    except Exception as e:

        st.error(
            f"Torch gagal dimuat:\n{e}"
        )

# ======================
# DETAIL TORCH
# ======================

try:

    import torch

    st.subheader("📦 Detail Torch")

    st.write("Lokasi instalasi:")
    st.code(torch.__file__)

except:
    pass