import streamlit as st
import cv2
import numpy as np
import pandas as pd
from io import BytesIO

# =========================
# KONFIGURASI HALAMAN
# =========================
st.set_page_config(
    page_title="Smart Exam Checker",
    page_icon="📝",
    layout="wide"
)

# =========================
# DESAIN TAMPILAN
# =========================
st.markdown("""
<style>
.stApp {
    background-color: #f4f7fb;
}
.main-title {
    background: linear-gradient(120deg, #142d4e, #2364a6);
    padding: 30px;
    border-radius: 15px;
    color: white;
    margin-bottom: 25px;
}
.main-title h1 {
    color: white;
}
.main-title p {
    color: #e1ecf8;
    font-size: 16px;
}
.section-title {
    color: #183b60;
    font-size: 21px;
    font-weight: 700;
    margin-top: 15px;
}
div[data-testid="stMetric"] {
    background-color: white;
    border: 1px solid #e1e8f0;
    padding: 18px;
    border-radius: 12px;
}
div.stButton > button {
    background-color: #2364a6;
    color: white;
    border-radius: 9px;
    border: none;
    padding: 10px 25px;
    font-weight: bold;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown("""
<div class="main-title">
    <h1>📝 Smart Exam Checker</h1>
    <p>Sistem Pemeriksaan Lembar Jawaban Pilihan Ganda Otomatis</p>
    <p>Berbasis Pengolahan Citra Digital Menggunakan OpenCV</p>
</div>
""", unsafe_allow_html=True)

st.write(
    "Unggah lembar jawaban peserta untuk melakukan "
    "pemeriksaan 20 soal secara otomatis."
)

# =========================
# PENGATURAN KUNCI JAWABAN
# =========================
st.markdown(
    '<p class="section-title">🔑 Pengaturan Kunci Jawaban</p>',
    unsafe_allow_html=True
)

st.write("Pilih kunci jawaban yang benar untuk setiap nomor soal.")

kunci_default = [
    'A', 'C', 'B', 'B', 'D',
    'A', 'C', 'B', 'D', 'A',
    'B', 'C', 'A', 'D', 'B',
    'C', 'A', 'D', 'B', 'C'
]

kunci_jawaban = []

kolom_kunci = st.columns(4)

for kolom in range(4):
    with kolom_kunci[kolom]:
        awal = kolom * 5

        st.markdown(
            f"**Soal {awal + 1}–{awal + 5}**"
        )

        for i in range(5):
            nomor_soal = awal + i

            jawaban = st.selectbox(
                f"Soal {nomor_soal + 1}",
                options=['A', 'B', 'C', 'D'],
                index=['A', 'B', 'C', 'D'].index(
                    kunci_default[nomor_soal]
                ),
                key=f"kunci_{nomor_soal}"
            )

            kunci_jawaban.append(jawaban)

st.divider()

# =========================
# IDENTITAS PESERTA
# =========================
st.markdown(
    '<p class="section-title">👤 Identitas Peserta</p>',
    unsafe_allow_html=True
)

c1, c2 = st.columns(2)

with c1:
    nama = st.text_input("Nama Peserta")

with c2:
    nomor = st.text_input("Nomor Peserta")

# =========================
# UNGGAH GAMBAR
# =========================
st.markdown(
    '<p class="section-title">📂 Unggah Lembar Jawaban</p>',
    unsafe_allow_html=True
)

file = st.file_uploader(
    "Pilih gambar lembar jawaban peserta",
    type=["png", "jpg", "jpeg"]
)

if file is not None:

    bytes_gambar = np.asarray(
        bytearray(file.read()),
        dtype=np.uint8
    )

    gambar = cv2.imdecode(
        bytes_gambar,
        cv2.IMREAD_COLOR
    )

    if gambar is None:
        st.error("Gambar tidak dapat dibaca.")
    else:

        kolom1, kolom2 = st.columns(2)

        with kolom1:
            st.markdown("**Pratinjau Lembar Jawaban**")

            st.image(
                cv2.cvtColor(gambar, cv2.COLOR_BGR2RGB),
                use_container_width=True
            )

        with kolom2:
            st.markdown("**Informasi Gambar**")

            st.write("Nama file:", file.name)
            st.write("Lebar:", gambar.shape[1], "pixel")
            st.write("Tinggi:", gambar.shape[0], "pixel")
            st.write("Jumlah soal:", 20)
            st.write("Pilihan jawaban: A, B, C, D")

            st.info(
                "Sistem menggunakan format lembar jawaban "
                "20 soal dengan dua kolom."
            )

        st.divider()

        if st.button("🔍 PERIKSA JAWABAN"):

            # =========================
            # PENGOLAHAN CITRA
            # =========================

            gambar_ukur = cv2.resize(
                gambar,
                (1024, 1536)
            )

            gray = cv2.cvtColor(
                gambar_ukur,
                cv2.COLOR_BGR2GRAY
            )

            _, thresh = cv2.threshold(
                gray,
                150,
                255,
                cv2.THRESH_BINARY
            )

            # KOORDINAT KOLOM KIRI DAN KANAN
            x_kiri = [172, 264, 354, 444]
            x_kanan = [652, 743, 832, 922]

            posisi_y = [
                378, 468, 557, 647, 736,
                826, 916, 1006, 1095, 1184
            ]

            pilihan = ['A', 'B', 'C', 'D']

            semua_x = [x_kiri, x_kanan]

            hasil = []

            # =========================
            # DETEKSI JAWABAN
            # =========================

            for kolom in semua_x:

                for y in posisi_y:

                    nilai_soal = []

                    for x in kolom:

                        mask = np.zeros(
                            thresh.shape,
                            dtype=np.uint8
                        )

                        cv2.circle(
                            mask,
                            (x, y),
                            13,
                            255,
                            -1
                        )

                        hitam = np.count_nonzero(
                            (thresh == 0) & (mask == 255)
                        )

                        nilai_soal.append(hitam)

                    terisi = [
                        i for i, jumlah in enumerate(nilai_soal)
                        if jumlah >= 80
                    ]

                    if len(terisi) == 0:
                        jawaban = "KOSONG"

                    elif len(terisi) > 1:
                        jawaban = "GANDA"

                    else:
                        jawaban = pilihan[terisi[0]]

                    hasil.append(jawaban)

            # =========================
            # PEMERIKSAAN JAWABAN
            # =========================

            benar = 0
            salah = 0
            kosong = 0
            ganda = 0

            data = []

            for i in range(20):

                jawaban = hasil[i]
                kunci = kunci_jawaban[i]

                if jawaban == "KOSONG":
                    status = "Kosong"
                    kosong += 1

                elif jawaban == "GANDA":
                    status = "Ganda"
                    ganda += 1

                elif jawaban == kunci:
                    status = "Benar"
                    benar += 1

                else:
                    status = "Salah"
                    salah += 1

                data.append({
                    "Nomor Soal": i + 1,
                    "Jawaban Peserta": jawaban,
                    "Kunci Jawaban": kunci,
                    "Status": status
                })

            nilai = (benar / 20) * 100

            # =========================
            # HASIL PEMERIKSAAN
            # =========================

            st.divider()

            st.markdown(
                '<p class="section-title">📊 Hasil Pemeriksaan</p>',
                unsafe_allow_html=True
            )

            df = pd.DataFrame(data)

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            # =========================
            # RINGKASAN HASIL
            # =========================

            st.markdown(
                '<p class="section-title">📈 Ringkasan Hasil</p>',
                unsafe_allow_html=True
            )

            c1, c2, c3, c4 = st.columns(4)

            c1.metric("✅ Benar", benar)
            c2.metric("❌ Salah", salah)
            c3.metric("⚪ Kosong", kosong)
            c4.metric("🔁 Ganda", ganda)

            # =========================
            # GRAFIK
            # =========================

            st.markdown("**Grafik Hasil Pemeriksaan**")

            grafik = pd.DataFrame({
                "Jumlah": [
                    benar,
                    salah,
                    kosong,
                    ganda
                ]
            }, index=[
                "Benar",
                "Salah",
                "Kosong",
                "Ganda"
            ])

            st.bar_chart(grafik)

            # =========================
            # NILAI AKHIR
            # =========================

            st.divider()

            st.markdown(
                '<p class="section-title">🏆 Nilai Akhir Peserta</p>',
                unsafe_allow_html=True
            )

            st.metric(
                "Nilai Akhir",
                f"{nilai:.1f} / 100"
            )

            if nilai == 100:
                st.success(
                    "Sangat baik! Semua jawaban benar."
                )

            elif nilai >= 60:
                st.success(
                    "Pemeriksaan selesai. Hasil berhasil dihitung."
                )

            else:
                st.warning(
                    "Pemeriksaan selesai. Silakan periksa hasil jawaban."
                )

            # =========================
            # DOWNLOAD EXCEL
            # =========================

            ringkasan = pd.DataFrame([{
                "Nama Peserta": nama,
                "Nomor Peserta": nomor,
                "Jumlah Soal": 20,
                "Benar": benar,
                "Salah": salah,
                "Kosong": kosong,
                "Ganda": ganda,
                "Nilai Akhir": nilai
            }])

            excel = BytesIO()

            with pd.ExcelWriter(
                excel,
                engine="openpyxl"
            ) as writer:

                df.to_excel(
                    writer,
                    sheet_name="Detail Jawaban",
                    index=False
                )

                ringkasan.to_excel(
                    writer,
                    sheet_name="Ringkasan",
                    index=False
                )

            st.download_button(
                label="📥 Download Hasil Excel",
                data=excel.getvalue(),
                file_name="hasil_pemeriksaan_20_soal.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.caption(
                "Smart Exam Checker | Pengolahan Citra Digital"
            )

else:
    st.info(
        "Silakan unggah gambar lembar jawaban untuk memulai pemeriksaan."
    )
