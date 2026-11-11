import streamlit as st
import cv2
import numpy as np
import pandas as pd
from io import BytesIO

# =========================================================
# SMART EXAM CHECKER
# Desain antarmuka diperbarui; algoritma pemeriksaan dipertahankan.
# =========================================================

st.set_page_config(
    page_title="Smart Exam Checker",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------- THEME -------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');

:root {
    --navy: #101b35;
    --navy-2: #172747;
    --blue: #356df3;
    --blue-light: #eaf0ff;
    --text: #17233d;
    --muted: #71809a;
    --line: #e7ecf4;
    --surface: #ffffff;
}
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
.stApp {
    background:
      radial-gradient(circle at 82% 0%, rgba(70, 116, 245, .10), transparent 27rem),
      #f4f7fc;
    color: var(--text);
}
.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}
header[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #101b35 0%, #172747 100%);
    border-right: 1px solid rgba(255,255,255,.08);
}
[data-testid="stSidebar"] * { color: #edf3ff !important; }
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stNumberInput input {
    background: rgba(255,255,255,.10) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,.18) !important;
    border-radius: 10px !important;
}
[data-testid="stSidebar"] [data-baseweb="input"] {
    background: transparent;
}
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.18); }
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color: #b9c7e0 !important; }

.hero {
    position: relative;
    overflow: hidden;
    padding: 30px 34px;
    border-radius: 22px;
    color: white;
    background: linear-gradient(120deg, #101b35 0%, #1c3768 65%, #356df3 125%);
    box-shadow: 0 16px 38px rgba(26, 55, 105, .16);
    margin-bottom: 24px;
}
.hero:after {
    content: "✓";
    position: absolute;
    right: 42px;
    top: -42px;
    font-size: 190px;
    font-weight: 800;
    color: rgba(255,255,255,.055);
}
.hero-kicker {
    color: #a9c3ff;
    font-size: .76rem;
    font-weight: 800;
    letter-spacing: .16em;
    text-transform: uppercase;
    margin-bottom: 9px;
}
.hero-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: clamp(1.8rem, 3vw, 2.65rem);
    font-weight: 800;
    line-height: 1.15;
    margin: 0;
    color: #fff;
}
.hero-subtitle {
    color: #d4def2;
    font-size: 1rem;
    margin-top: 10px;
    max-width: 680px;
}
.hero-tag {
    display: inline-block;
    margin-top: 18px;
    padding: 7px 12px;
    border-radius: 999px;
    background: rgba(255,255,255,.12);
    border: 1px solid rgba(255,255,255,.16);
    color: #eef4ff;
    font-size: .78rem;
    font-weight: 600;
}
.section-heading {
    display: flex;
    align-items: center;
    gap: 11px;
    margin: 27px 0 12px;
    color: #17233d;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.13rem;
    font-weight: 800;
}
.section-number {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 30px;
    height: 30px;
    border-radius: 9px;
    color: #fff;
    background: #356df3;
    font-size: .88rem;
}
.helper-text {
    color: #71809a;
    font-size: .88rem;
    margin: -4px 0 13px 41px;
}
div[data-testid="stFileUploader"] section {
    background: #fff;
    border: 1.5px dashed #b9c9e8;
    border-radius: 15px;
}
div[data-testid="stFileUploader"] section:hover {
    border-color: #356df3;
}
div[data-testid="stSelectbox"] > div > div,
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {
    border-radius: 10px !important;
}
div[data-testid="stSelectbox"] label,
div[data-testid="stTextInput"] label,
div[data-testid="stNumberInput"] label {
    font-weight: 600;
    color: #35445f;
}
div[data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(100deg, #285ce5, #477cf7);
    border: 0;
    border-radius: 12px;
    min-height: 3.1rem;
    font-weight: 800;
    letter-spacing: .02em;
    box-shadow: 0 8px 18px rgba(53,109,243,.22);
}
div[data-testid="stButton"] button[kind="primary"]:hover {
    background: linear-gradient(100deg, #1e4fcf, #356df3);
    border: 0;
    transform: translateY(-1px);
}
div[data-testid="stDownloadButton"] button {
    background: #142544;
    color: #fff;
    border: 0;
    border-radius: 11px;
    min-height: 2.9rem;
    font-weight: 700;
}
div[data-testid="stMetric"] {
    background: #fff;
    border: 1px solid #e7ecf4;
    border-radius: 15px;
    padding: 16px 17px;
    box-shadow: 0 5px 18px rgba(27,48,85,.045);
}
div[data-testid="stMetricLabel"] { color: #71809a; font-weight: 600; }
div[data-testid="stMetricValue"] { color: #17233d; font-weight: 800; }
div[data-testid="stDataFrame"] {
    border: 1px solid #e7ecf4;
    border-radius: 13px;
    overflow: hidden;
}
div[data-testid="stAlert"] { border-radius: 12px; }
div[data-testid="stExpander"] {
    background: #fff;
    border: 1px solid #e7ecf4;
    border-radius: 12px;
}
.footer {
    margin-top: 35px;
    padding-top: 16px;
    border-top: 1px solid #e3e9f2;
    color: #8793a8;
    text-align: center;
    font-size: .8rem;
}
</style>
""", unsafe_allow_html=True)

# ------------------------- HEADER -------------------------
st.markdown("""
<div class="hero">
  <div class="hero-kicker">Automated answer sheet evaluation</div>
  <div class="hero-title">📝 Smart Exam Checker</div>
  <div class="hero-subtitle">
    Sistem pemeriksaan lembar jawaban pilihan ganda secara otomatis.
    Unggah lembar jawaban, tentukan kunci, lalu dapatkan hasil koreksi dan nilai.
  </div>
  <div class="hero-tag">20 Soal &nbsp; • &nbsp; 2 Kolom &nbsp; • &nbsp; Pilihan A–D</div>
</div>
""", unsafe_allow_html=True)

st.info("Pastikan lembar jawaban menggunakan template 20 soal, dua kolom, dengan pilihan A–D.")

# ------------------------- SIDEBAR -------------------------
with st.sidebar:
    st.markdown("## 👤 Identitas Peserta")
    st.caption("Isi data peserta sebelum melakukan pemeriksaan.")
    nama = st.text_input("Nama peserta", placeholder="Contoh: Carolina")
    nomor = st.text_input("Nomor peserta", placeholder="Contoh: 018")
    st.divider()
    st.markdown("## ⚙️ Pengaturan Nilai")
    bobot = st.number_input(
        "Poin setiap jawaban benar",
        min_value=0.0,
        max_value=100.0,
        value=5.0,
        step=0.5,
        help="Contoh: 5 poin × 20 soal = nilai maksimal 100.",
    )
    st.caption("Jawaban kosong dan ganda tidak mendapat poin.")
    st.divider()
    st.caption("SMART EXAM CHECKER · PROTOTIPE")

# ------------------------- INPUT IMAGE -------------------------
st.markdown('<div class="section-heading"><span class="section-number">1</span> Unggah lembar jawaban</div>', unsafe_allow_html=True)
st.markdown('<div class="helper-text">Pilih foto atau hasil scan lembar jawaban peserta. Pastikan gambar utuh dan tidak buram.</div>', unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Pilih gambar lembar jawaban",
    type=["png", "jpg", "jpeg"],
    help="Gunakan gambar utuh, jelas, dan tidak terpotong.",
    label_visibility="collapsed",
)
if uploaded:
    st.success(f"File berhasil dipilih: {uploaded.name}")
    with st.expander("Pratinjau lembar jawaban", expanded=True):
        st.image(uploaded, caption="Gambar yang akan diperiksa", use_container_width=True)

# ------------------------- ANSWER KEY -------------------------
st.markdown('<div class="section-heading"><span class="section-number">2</span> Masukkan kunci jawaban</div>', unsafe_allow_html=True)
st.markdown('<div class="helper-text">Pilih jawaban yang benar untuk setiap nomor soal.</div>', unsafe_allow_html=True)

keys = {}
left, right = st.columns(2)
for q in range(1, 21):
    target = left if q <= 10 else right
    with target:
        keys[q] = st.selectbox(
            f"Soal {q}",
            ["A", "B", "C", "D"],
            key=f"final_key_{q}",
            label_visibility="visible",
        )

# ------------------------- PROCESS -------------------------
st.markdown('<div class="section-heading"><span class="section-number">3</span> Proses pemeriksaan</div>', unsafe_allow_html=True)
st.markdown('<div class="helper-text">Tekan tombol di bawah untuk membaca arsiran, mencocokkan kunci, dan menghitung nilai.</div>', unsafe_allow_html=True)

run_check = st.button(
    "🔎  BACA, KOREKSI, DAN HITUNG NILAI",
    type="primary",
    use_container_width=True,
    disabled=uploaded is None,
)

if run_check:
    raw = np.frombuffer(uploaded.getvalue(), np.uint8)
    original = cv2.imdecode(raw, cv2.IMREAD_COLOR)
    if original is None:
        st.error("Gambar tidak dapat dibaca. Silakan unggah ulang file PNG atau JPG.")
        st.stop()

    h0, w0 = original.shape[:2]
    img = cv2.resize(original, (900, int(h0 * 900 / w0)))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 1.2)
    H, W = gray.shape
    circles = cv2.HoughCircles(
        blur,
        cv2.HOUGH_GRADIENT,
        dp=1.15,
        minDist=18,
        param1=100,
        param2=27,
        minRadius=12,
        maxRadius=30,
    )
    if circles is None:
        st.error("Bulatan tidak terdeteksi. Gunakan gambar yang jelas dan tidak terpotong.")
        st.stop()

    candidates = []
    for x, y, r in np.round(circles[0]).astype(int):
        if 0.12 * H < y < 0.91 * H and 0.12 * W < x < 0.94 * W:
            if all(np.hypot(x - a, y - b) > 16 for a, b, _ in candidates):
                candidates.append((int(x), int(y), int(r)))
    if len(candidates) < 30:
        st.error(f"Kandidat bulatan terlalu sedikit ({len(candidates)}). Pastikan gambar utuh dan jelas.")
        st.stop()

    def cluster(values, k):
        samples = np.float32(values).reshape(-1, 1)
        criteria = (
            cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
            100,
            0.2,
        )
        _, labels, centers = cv2.kmeans(
            samples, k, None, criteria, 10, cv2.KMEANS_PP_CENTERS
        )
        centers = centers.flatten()
        order = np.argsort(centers)
        remap = {int(old): new for new, old in enumerate(order)}
        return centers[order], np.array([remap[int(v)] for v in labels.flatten()])

    xcenters, xl = cluster([p[0] for p in candidates], 8)
    ycenters, yl = cluster([p[1] for p in candidates], 10)
    grid = {}
    for i, p in enumerate(candidates):
        cell = (int(xl[i]), int(yl[i]))
        distance = abs(p[0] - xcenters[cell[0]]) + abs(p[1] - ycenters[cell[1]])
        if cell not in grid or distance < grid[cell][0]:
            grid[cell] = (distance, p)

    if len(grid) != 80:
        st.error(
            f"Terdeteksi {len(grid)} dari 80 posisi bulatan. "
            "Pastikan gambar tidak terpotong dan sesuai dengan template 20 soal."
        )
        st.stop()

    details = []
    overlay = img.copy()
    letters = ["A", "B", "C", "D"]
    for row in range(10):
        for col in range(8):
            _, (x, y, r) = grid[(col, row)]
            mask = np.zeros(gray.shape, dtype=np.uint8)
            cv2.circle(mask, (x, y), max(5, int(r * 0.52)), 255, -1)
            ratio = float(np.mean(gray[mask == 255] < 110))
            q = row + 1 if col < 4 else row + 11
            details.append({"Nomor soal": q, "Pilihan": letters[col % 4], "Rasio gelap": ratio})

    detail_df = pd.DataFrame(details)
    rows = []
    for q in range(1, 21):
        qdata = detail_df[detail_df["Nomor soal"] == q]
        marked = qdata[qdata["Rasio gelap"] >= 0.60]["Pilihan"].tolist()
        if len(marked) == 0:
            answer, status = "-", "KOSONG"
        elif len(marked) == 1:
            answer, status = marked[0], "TERBACA"
        else:
            answer, status = ", ".join(marked), "GANDA"
        rows.append({"Nomor soal": q, "Jawaban peserta": answer, "Status": status})

    result = pd.DataFrame(rows)
    result["Kunci jawaban"] = result["Nomor soal"].map(keys)
    result["Hasil"] = result.apply(
        lambda r: "BENAR"
        if r["Status"] == "TERBACA" and r["Jawaban peserta"] == r["Kunci jawaban"]
        else ("SALAH" if r["Status"] == "TERBACA" else r["Status"]),
        axis=1,
    )

    correct = int((result["Hasil"] == "BENAR").sum())
    wrong = int((result["Hasil"] == "SALAH").sum())
    blank = int((result["Hasil"] == "KOSONG").sum())
    double = int((result["Hasil"] == "GANDA").sum())
    score = min(100.0, correct * float(bobot))

    st.divider()
    st.markdown('<div class="section-heading"><span class="section-number">4</span> Hasil pemeriksaan</div>', unsafe_allow_html=True)
    info1, info2 = st.columns(2)
    info1.write(f"**Nama peserta:** {nama or 'Belum diisi'}")
    info2.write(f"**Nomor peserta:** {nomor or 'Belum diisi'}")

    metrics = st.columns(5)
    for col, label, value in zip(
        metrics,
        ["Benar", "Salah", "Kosong", "Ganda", "Nilai"],
        [correct, wrong, blank, double, f"{score:.1f}"],
    ):
        col.metric(label, value)

    st.markdown("#### Rincian jawaban")
    st.dataframe(result, use_container_width=True, hide_index=True)

    for row in range(10):
        for col in range(8):
            _, (x, y, r) = grid[(col, row)]
            q = row + 1 if col < 4 else row + 11
            letter = letters[col % 4]
            ratio = detail_df[
                (detail_df["Nomor soal"] == q) & (detail_df["Pilihan"] == letter)
            ]["Rasio gelap"].iloc[0]
            color = (0, 180, 0) if ratio >= 0.60 else (0, 140, 220)
            cv2.circle(overlay, (x, y), max(5, int(r * 0.52)), color, 2)

    with st.expander("Lihat gambar dengan penanda hasil deteksi"):
        st.image(
            cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB),
            caption="Lingkaran hijau = dianggap terisi; oranye = dianggap kosong.",
            use_container_width=True,
        )
    with st.expander("Lihat rasio gelap setiap pilihan"):
        display_detail = detail_df.copy()
        display_detail["Rasio gelap"] = display_detail["Rasio gelap"].round(3)
        st.dataframe(display_detail, use_container_width=True, hide_index=True)

    export = result.copy()
    export.insert(0, "Nama peserta", nama)
    export.insert(1, "Nomor peserta", nomor)
    summary = pd.DataFrame(
        [{
            "Nama peserta": nama,
            "Nomor peserta": nomor,
            "Jumlah soal": 20,
            "Benar": correct,
            "Salah": wrong,
            "Kosong": blank,
            "Ganda": double,
            "Nilai": score,
        }]
    )
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        summary.to_excel(writer, index=False, sheet_name="Ringkasan")
        export.to_excel(writer, index=False, sheet_name="Detail Jawaban")
        detail_df.assign(**{"Rasio gelap": detail_df["Rasio gelap"].round(3)}).to_excel(
            writer, index=False, sheet_name="Rasio Gelap"
        )

    st.download_button(
        "📥  Unduh hasil pemeriksaan Excel",
        data=output.getvalue(),
        file_name="hasil_smart_exam_checker.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
    st.caption(
        "Catatan: versi ini disiapkan untuk template 20 soal dua kolom A–D yang telah diuji. "
        "Uji kembali dengan beberapa lembar sebelum digunakan dalam ujian sebenarnya."
    )

st.markdown("""
<div class="footer">
  Smart Exam Checker · Prototipe pemeriksaan lembar jawaban pilihan ganda
</div>
""", unsafe_allow_html=True)
