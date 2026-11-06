import streamlit as st
import cv2
import numpy as np
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Smart Exam Checker", page_icon="📝", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #f4f7fb; }
.main-title { background: linear-gradient(120deg, #142d4e, #2364a6);
padding: 30px; border-radius: 15px; color: white; margin-bottom: 25px; }
.main-title h1 { color: white; }
.main-title p { color: #e1ecf8; font-size: 16px; }
.section-title { color: #183b60; font-size: 21px; font-weight: 700; margin-top: 15px; }
div[data-testid="stMetric"] { background-color: white; border: 1px solid #e1e8f0;
padding: 18px; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-title">
<h1>📝 Smart Exam Checker</h1>
<p>Sistem Pemeriksaan Lembar Jawaban Pilihan Ganda Otomatis</p>
<p>Berbasis Pengolahan Citra Digital Menggunakan OpenCV</p>
</div>
""", unsafe_allow_html=True)

st.write("Atur jumlah soal dan pilihan jawaban, lalu unggah lembar jawaban peserta.")

st.markdown('<p class="section-title">⚙️ Pengaturan Ujian</p>', unsafe_allow_html=True)
cfg1, cfg2 = st.columns(2)
with cfg1:
    jumlah_soal = st.number_input("Jumlah soal", min_value=1, max_value=100, value=20, step=1)
with cfg2:
    jumlah_pilihan = st.selectbox("Jumlah pilihan jawaban", options=[2, 3, 4, 5], index=2,
                                  format_func=lambda n: f"{n} pilihan ({', '.join('ABCDE'[:n])})")
pilihan = list("ABCDE"[:jumlah_pilihan])

st.markdown('<p class="section-title">🔑 Pengaturan Kunci Jawaban</p>', unsafe_allow_html=True)
st.write("Pilih kunci jawaban yang benar untuk setiap nomor soal.")
kunci_jawaban = []
kolom_per_baris = st.columns(4)
for i in range(int(jumlah_soal)):
    with kolom_per_baris[i % 4]:
        kunci = st.selectbox(
            f"Soal {i + 1}", options=pilihan, index=0, key=f"kunci_{i}_{jumlah_pilihan}_{jumlah_soal}"
        )
        kunci_jawaban.append(kunci)

st.divider()
st.markdown('<p class="section-title">👤 Identitas Peserta</p>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    nama = st.text_input("Nama Peserta")
with c2:
    nomor = st.text_input("Nomor Peserta")

st.markdown('<p class="section-title">📂 Unggah Lembar Jawaban</p>', unsafe_allow_html=True)
file = st.file_uploader("Pilih gambar lembar jawaban peserta", type=["png", "jpg", "jpeg"])

if file is not None:
    raw = np.asarray(bytearray(file.getvalue()), dtype=np.uint8)
    gambar = cv2.imdecode(raw, cv2.IMREAD_COLOR)
    if gambar is None:
        st.error("Gambar tidak dapat dibaca. Coba gunakan file PNG atau JPG.")
    else:
        left, right = st.columns(2)
        with left:
            st.markdown("**Pratinjau Lembar Jawaban**")
            st.image(cv2.cvtColor(gambar, cv2.COLOR_BGR2RGB), use_container_width=True)
        with right:
            st.markdown("**Informasi Gambar**")
            st.write("Nama file:", file.name)
            st.write("Lebar:", gambar.shape[1], "pixel")
            st.write("Tinggi:", gambar.shape[0], "pixel")
            st.write("Jumlah soal:", int(jumlah_soal))
            st.write("Pilihan jawaban:", ", ".join(pilihan))
        st.divider()

        st.warning(
            "Catatan tahap pengembangan: pengaturan jumlah soal dan pilihan sudah fleksibel, "
            "tetapi pembacaan gambar otomatis saat ini masih memakai koordinat template lama "
            "(20 soal, dua kolom, pilihan A–D). Untuk jumlah atau desain lain, tahap kalibrasi "
            "dan deteksi otomatis perlu diselesaikan terlebih dahulu."
        )

        if st.button("🔍 PERIKSA JAWABAN", type="primary", use_container_width=True):
            if int(jumlah_soal) > 20 or jumlah_pilihan > 4:
                st.error(
                    "Pembacaan otomatis untuk konfigurasi ini belum tersedia. "
                    "Untuk sementara, gunakan maksimal 20 soal dengan pilihan A–D "
                    "sampai fitur kalibrasi dikembangkan."
                )
            else:
                # Koordinat ini hanya berlaku untuk template 20 soal lama.
                gambar_ukur = cv2.resize(gambar, (1024, 1536))
                gray = cv2.cvtColor(gambar_ukur, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

                x_kiri = [172, 264, 354, 444]
                x_kanan = [652, 743, 832, 922]
                posisi_y = [378, 468, 557, 647, 736, 826, 916, 1006, 1095, 1184]

                hasil = []
                for kolom in [x_kiri, x_kanan]:
                    for y in posisi_y:
                        nilai_soal = []
                        for x in kolom[:jumlah_pilihan]:
                            mask = np.zeros(thresh.shape, dtype=np.uint8)
                            cv2.circle(mask, (x, y), 13, 255, -1)
                            hitam = np.count_nonzero((thresh == 0) & (mask == 255))
                            nilai_soal.append(hitam)

                        terisi = [idx for idx, jumlah in enumerate(nilai_soal) if jumlah >= 80]
                        if len(terisi) == 0:
                            jawaban = "KOSONG"
                        elif len(terisi) > 1:
                            jawaban = "GANDA"
                        else:
                            jawaban = pilihan[terisi[0]]
                        hasil.append(jawaban)

                hasil = hasil[:int(jumlah_soal)]
                benar = salah = kosong = ganda = 0
                data = []
                for i, jawaban in enumerate(hasil):
                    kunci = kunci_jawaban[i]
                    if jawaban == "KOSONG":
                        status = "Kosong"; kosong += 1
                    elif jawaban == "GANDA":
                        status = "Ganda"; ganda += 1
                    elif jawaban == kunci:
                        status = "Benar"; benar += 1
                    else:
                        status = "Salah"; salah += 1
                    data.append({
                        "Nomor Soal": i + 1,
                        "Jawaban Peserta": jawaban,
                        "Kunci Jawaban": kunci,
                        "Status": status
                    })

                nilai = (benar / int(jumlah_soal)) * 100
                st.divider()
                st.markdown('<p class="section-title">📊 Hasil Pemeriksaan</p>', unsafe_allow_html=True)
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True, hide_index=True)

                st.markdown('<p class="section-title">📈 Ringkasan Hasil</p>', unsafe_allow_html=True)
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("✅ Benar", benar)
                m2.metric("❌ Salah", salah)
                m3.metric("⚪ Kosong", kosong)
                m4.metric("🔁 Ganda", ganda)

                st.markdown("**Grafik Hasil Pemeriksaan**")
                grafik = pd.DataFrame({"Jumlah": [benar, salah, kosong, ganda]},
                                      index=["Benar", "Salah", "Kosong", "Ganda"])
                st.bar_chart(grafik)

                st.divider()
                st.markdown('<p class="section-title">🏆 Nilai Akhir Peserta</p>', unsafe_allow_html=True)
                st.metric("Nilai Akhir", f"{nilai:.1f} / 100")
                if nilai == 100:
                    st.success("Sangat baik! Semua jawaban benar.")
                elif nilai >= 60:
                    st.success("Pemeriksaan selesai. Hasil berhasil dihitung.")
                else:
                    st.warning("Pemeriksaan selesai. Silakan periksa hasil jawaban.")

                ringkasan = pd.DataFrame([{
                    "Nama Peserta": nama, "Nomor Peserta": nomor,
                    "Jumlah Soal": int(jumlah_soal), "Jumlah Pilihan": jumlah_pilihan,
                    "Benar": benar, "Salah": salah, "Kosong": kosong,
                    "Ganda": ganda, "Nilai Akhir": nilai
                }])
                excel = BytesIO()
                with pd.ExcelWriter(excel, engine="openpyxl") as writer:
                    df.to_excel(writer, sheet_name="Detail Jawaban", index=False)
                    ringkasan.to_excel(writer, sheet_name="Ringkasan", index=False)
                st.download_button(
                    label="📥 Download Hasil Excel", data=excel.getvalue(),
                    file_name="hasil_pemeriksaan.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.caption("Smart Exam Checker | Pengolahan Citra Digital")
else:
    st.info("Silakan unggah gambar lembar jawaban untuk memulai pemeriksaan.")
