# Panduan & Dokumentasi Komponen Dashboard ABSA (Kurs Dolar/Rupiah)

Dokumen ini merupakan panduan teknis yang menjelaskan secara detail seluruh komponen yang ada pada **Dashboard Deteksi Respon Publik Terhadap Kenaikan Kurs Dolar AS / Rupiah**. Panduan ini merinci sumber data, rumus perhitungan, integrasi model kecerdasan buatan (IndoBERT), berkas kode program yang digunakan, serta tujuan analisis dari masing-masing visualisasi.

---

## 1. Tujuan Umum Dashboard
Dashboard ini dikembangkan sebagai alat bantu penunjang keputusan (*Decision Support System*) dan sistem peringatan dini (*Early Warning System / EWS*). Sistem ini mengintegrasikan **Analisis Sentimen Berbasis Aspek (Aspect-Based Sentiment Analysis / ABSA)** dari opini publik di media sosial X dengan **pergerakan kurs valuta asing riil (USD/IDR)** untuk mendeteksi tingkat kepanikan pasar secara temporal dan sektoral.

---

## 2. Berkas Utama yang Digunakan (File Registry)

Berikut adalah daftar berkas yang membangun fungsionalitas dashboard ini:

| Nama Berkas | Lokasi Berkas | Deskripsi / Peran |
| :--- | :--- | :--- |
| **`app.py`** | `/absa-dashboard-indobert-main/` | Berkas utama Streamlit yang merender UI, memproses tata letak (*layout*), memicu kalkulasi, dan menampilkan grafik interaktif. |
| **`dolar_rupiah.csv`** | `/absa-dashboard-indobert-main/data/` | Dataset utama berisi 10.131 baris opini hasil *crawling* X/Twitter lengkap dengan stempel waktu, teks, metrik interaksi, aspek, dan sentimen. |
| **`model_loader.py`** | `/absa-dashboard-indobert-main/utils/` | Script utilitas PyTorch untuk memuat arsitektur saraf IndoBERT dual-head dan memprediksi aspek/sentimen. |
| **`pytorch_model.bin`** | `/absa-dashboard-indobert-main/model/model_indobert_absa/` | Bobot biner (*neural network weights*) model fine-tuned IndoBERT hasil pelatihan Colab. |
| **`tokenizer.json`** & config | `/absa-dashboard-indobert-main/model/model_indobert_absa/` | Konfigurasi pemecah kata (*tokenizer*) IndoBERT untuk memetakan teks ke representasi token numerik. |

---

## 3. Arsitektur Model AI & Tokenisasi

*   **Model Dasar**: `indobenchmark/indobert-base-p1` (BERT-base versi bahasa Indonesia yang umum digunakan di lingkungan akademis).
*   **Arsitektur Dual-Head (Multi-Task Learning)**: 
    Model mengambil representasi tersembunyi (*hidden state*) dari token `[CLS]` (pooler output) setebal 768 dimensi, lalu melewatkannya ke lapisan *dropout* (rate = 0.3) sebelum membaginya ke dua kepala klasifikasi linier secara paralel:
    1.  **Head Aspek**: Memetakan teks ke 5 kelas aspek ekonomi (Linear layer output dimensi 5).
    2.  **Head Sentimen**: Memetakan teks ke 3 kelas sentimen (Linear layer output dimensi 3).
*   **Tokenisasi**: Menggunakan tokenisasi BERT dengan panjang input maksimum `MAX_LEN = 128`, ditambahkan *special tokens* (`[CLS]`, `[SEP]`), serta metode *truncation* dan *padding* bertipe `'max_length'`.

---

## 4. Panduan Detail Komponen Dashboard

### Filter Waktu Analisis (Time Filter Scope)
*   **Peran & Cakupan**: Filter rentang waktu (Semua Data, 7 Hari Terakhir, 30 Hari Terakhir, Rentang Kustom) dikonfigurasi secara eksklusif **hanya memengaruhi Scoreboard Utama & EWS Alarm Status** (dihitung menggunakan variabel `df_scoreboard`).
*   **Visualisasi Lain**: Untuk menjaga keutuhan statistik tren jangka panjang, grafik sebaran sentimen/aspek, average engagement, matriks prioritas risiko, grafik korelasi valas, dan tabel sampel opini publik diprogram agar **selalu menggunakan data utuh/lengkap (`df_full`)**.
*   **Keamanan Indeks**: Logika sampling tweet dilengkapi dengan penanganan interseksi indeks (`df.index.intersection` / list comprehension) untuk mencegah terjadinya `KeyError` di pandas ketika rentang waktu filter diubah secara dinamis.

---

### Row 1: Scoreboard Utama (Metric Cards)
Scoreboard diletakkan di bagian atas untuk memberikan ringkasan status pasar secara instan kepada pengambil keputusan.

#### A. Card 1: Total Opini (Tweet)
*   **Tujuan**: Mengetahui volume penyebaran opini publik yang berhasil dikumpulkan untuk rentang waktu terpilih.
*   **Sumber Data**: Kolom `tweet_id` pada `dolar_rupiah.csv`.
*   **Rumus Perhitungan**:
    $$\text{Total Opini} = \text{Jumlah Baris } (len(df\_scoreboard))$$
*   **File Kode**: Terhitung di `app.py` baris 291-294.

#### B. Card 2: Total Engagement
*   **Tujuan**: Mengukur tingkat kepedulian atau keaktifan respons warganet terhadap isu pelemahan rupiah (apakah tweet kurs sekadar dibaca atau memicu interaksi masif).
*   **Sumber Data**: Kolom `likes`, `retweets`, dan `replies` pada `dolar_rupiah.csv`.
*   **Rumus Perhitungan**:
    $$\text{Engagement per Tweet } (i) = \text{likes}_i + \text{retweets}_i + \text{replies}_i$$
    $$\text{Total Engagement} = \sum_{i=1}^{N} \text{Engagement}_i \quad \text{untuk } i \in df\_scoreboard$$
*   *Catatan Bug Fix*: Berkas ini memuat parser kustom `parse_engagement_val` untuk mengonversi singkatan bahasa Indonesia seperti `10 RB` menjadi `10.000` integer secara tepat sebelum ditotal.
*   **File Kode**: Terhitung di `app.py` baris 291-295.

#### C. Card 3: Indeks Kepanikan (Rata-Rata)
*   **Tujuan**: Menghitung porsi persepsi negatif publik terhadap isu pergerakan kurs dolar selama rentang tanggal terpilih.
*   **Sumber Data**: Kolom `sentiment` pada `dolar_rupiah.csv`.
*   **Rumus Perhitungan**:
    $$\text{Indeks Kepanikan} = \left( \frac{\text{Jumlah Tweet Sentimen 'Negatif' pada df\_scoreboard}}{\text{Total Tweet pada df\_scoreboard}} \right) \times 100\%$$
*   **File Kode**: Terhitung di `app.py` baris 296-297.

#### D. Card 4: Status Sistem (EWS)
*   **Tujuan**: Memberikan alarm peringatan dini otomatis kepada otoritas moneter (misal: Bank Indonesia) untuk menentukan tindakan intervensi pasar valas.
*   **Sumber Data & Logika Threshold**:
    *   **GREEN ALERT** (Indeks Kepanikan $< 45\%$): Persepsi publik aman, kondisi pasar stabil. Latar belakang berwarna hijau solid (`#166534`).
    *   **YELLOW ALERT** (Indeks Kepanikan $45\% - 60\%$): Waspada volatilitas, pantau pergerakan sentimen. Latar belakang berwarna cokelat/kuning tua (`#78350f`).
    *   **RED ALERT** (Indeks Kepanikan $> 60\%$): Kepanikan tinggi, disarankan intervensi pasar valas. Latar belakang berwarna merah solid (`#7f1d1d`).
*   **File Kode**: Logika EWS berada di `app.py` baris 299-317.

---

### Row 1.5: Sampel Opini Publik & Analisis Model ABSA (Table)
*   **Tujuan**: Memberikan bukti transparan (*transparency*) dan sampel prediktif model AI secara *real-time* kepada analis untuk memvalidasi teks asli tweet terhadap kelas aspek/sentimen yang ditunjuk.
*   **Fungsionalitas**: Menampilkan 5 opini acak menggunakan tombol "Acak Sampel 🔄" (terkunci stabil menggunakan `st.session_state` agar tidak berubah saat filter diubah).
*   **Pemuatan Model Live**:
    Dashboard memanggil tokenizer dan weights asli `pytorch_model.bin` menggunakan `@st.cache_resource` (hanya loading sekali di awal startup). Saat sampel diacak, sistem menjalankan fungsi `predict()` secara *live*.
*   **Tingkat Keyakinan (Confidence Score)**:
    Bukan simulasi hash, melainkan nilai probabilitas riil hasil kalkulasi dari fungsi *softmax* di dalam output model biner untuk teks tersebut:
    $$\text{Confidence} = \frac{\text{Softmax(Aspect\_Logit)} + \text{Softmax(Sentiment\_Logit)}}{2} \times 100\%$$
*   **File Kode**: Dijalankan di `app.py` baris 360-440 memanfaatkan `utils/model_loader.py`.

---

### Row 2: Distribusi Sentimen & Aspek (Bar Charts)
Dua grafik kolom berdampingan untuk melihat struktur data secara demografis.

#### A. Grafik Kiri: Sebaran Sentimen Publik
*   **Tujuan**: Memetakan persepsi publik secara umum ke dalam kelompok polaritas: Negatif, Netral, atau Positif.
*   **Kalkulasi**: Menghitung frekuensi kemunculan masing-masing sentimen pada data terfilter.
*   **Visual**: Batang bar vertikal berwarna merah (Negatif), kuning/orange (Netral), dan hijau (Positif) dengan tinggi headroom sumbu Y dilebihkan 15% untuk menampilkan label angka secara utuh.
*   **File Kode**: Dirender di `app.py` baris 513-550.

#### B. Grafik Kanan: Sebaran Aspek yang Dibahas
*   **Tujuan**: Mengidentifikasi sektor atau topik ekonomi apa saja yang paling banyak didiskusikan oleh masyarakat ketika kurs rupiah bergejolak.
*   **Kalkulasi**: Menghitung frekuensi kemunculan masing-masing aspek (`Ekonomi nasional`, `Umum`, `Harga barang`, `Investasi`, `Ekspor`).
*   **Visual**: Grafik batang vertikal dengan skema warna aspek terstandarisasi (`COLORS_ASPECT`).
*   **File Kode**: Dirender di `app.py` baris 551-594.

---

### Row 2.5: Rata-Rata Keterlibatan Publik per Aspek (Horizontal Bar Chart)
*   **Tujuan**: Menemukan topik ekonomi mana yang paling viral dan memancing interaksi terbanyak warganet secara rata-rata, meskipun volume tweet aspek tersebut belum tentu paling mendominasi.
*   **Kalkulasi**:
    $$\text{Rata-Rata Engagement Aspek } A = \frac{\sum \text{Engagement Aspek } A}{\text{Total Tweet Aspek } A}$$
*   **Visual**: Grafik batang horizontal dengan label presisi satu angka di belakang koma (misal: `157.3`). Tooltip hover juga diformat bersih membulatkan nilai engagement ke desimal satu angka (`%{x:.1f}`).
*   **File Kode**: Dirender di `app.py` baris 596-652.

---

### Row 3: Analisis Tren & Risiko Kuadran (Double Layout)
Menyajikan analisis peramalan dan pemetaan tingkat prioritas penanganan isu.

#### A. Grafik Kiri: Tren Indeks Kepanikan Publik Harian (Line Chart)
*   **Tujuan**: Memantau perkembangan fluktuasi indeks kepanikan publik dari hari ke hari dan melihat kapan terjadi puncak-puncak (*spikes*) histeria massal.
*   **Kalkulasi**: Menghitung rasio sentimen negatif harian (`panic_index`), kemudian menerapkan rumus rata-rata bergerak 3-hari (`panic_index_ma`) untuk melunakkan gejolak ekstrem agar tren utama terbaca lebih stabil.
*   **File Kode**: Dirender di `app.py` baris 660-685.

#### B. Grafik Kanan: Matriks Prioritas Risiko Aspek (Scatter Chart)
*   **Tujuan**: Menentukan aspek mana yang paling berbahaya bagi stabilitas ekonomi makro dan opini publik untuk segera ditangani.
*   **Kalkulasi Pemetaan 4 Kuadran**:
    *   **Sumbu X (Tingkat Keparahan / Severity)**: Persentase tweet bersentimen negatif ($\% \text{ Negatif}$).
    *   **Sumbu Y (Tingkat Urgensi / Urgency)**: Total volume postingan aspek tersebut.
    *   **Ukuran Bulatan (Bubble Size)**: Akumulasi total engagement (likes, retweets, replies).
    *   *Pembatas Kuadran*: Garis vertikal di tingkat keparahan $50\%$ dan garis horizontal di nilai rata-rata volume aspek. Kuadran kanan-atas (keparahan tinggi & volume tinggi) adalah **Risiko Prioritas Utama** (diisi oleh aspek Ekonomi Nasional).
*   **File Kode**: Dirender di `app.py` baris 686-735.

---

### Row 4: Korelasi Tren Sentimen vs Pergerakan Kurs USD/IDR Aktual (Dual-Axis Chart)
*   **Tujuan**: Membuktikan secara empiris hubungan sebab-akibat antara fluktuasi nilai tukar Rupiah di dunia nyata dengan histeria opini negatif publik di media sosial X.
*   **Kalkulasi & Sumbu Ganda**:
    *   **Sumbu Y Kiri (Batang Merah Transparan)**: Volume tweet negatif harian.
    *   **Sumbu Y Kanan (Garis Biru Tebal)**: Nilai nominal penutupan kurs harian USD/IDR yang ditarik secara dinamis dari API Yahoo Finance (`yfinance`).
*   **Hasil Analisis**: Visualisasi ini menunjukkan bahwa setiap kali garis biru melonjak menembus level psikologis baru (misal Rp16.200 atau Rp16.500), selalu diikuti oleh lonjakan batang merah volume tweet negatif warganet secara instan.
*   **💡 Insight Tambahan**: Menegaskan adanya korelasi positif searah yang kuat antara tingkat kepanikan digital dengan pelemahan nilai tukar rupiah riil.
*   **File Kode**: Dirender di `app.py` baris 703-771.

---

### Row 5: Ringkasan Implikasi untuk Stakeholder (Bento-Grid Section)
*   **Tujuan**: Memberikan rekomendasi aksi strategis dan implikasi bisnis yang konkret kepada tiga kelompok stakeholder terdampak utama berdasarkan analisis dashboard.
*   **Pembagian Stakeholder**:
    1.  **🏦 Otoritas Moneter**: BI dan Pemerintah diimbau memantau indeks kepanikan media sosial sebagai indikator tambahan sebelum melakukan intervensi spot atau DNDF guna menenangkan pasar secara psikologis.
    2.  **🏬 Pelaku Industri & Importir**: Didorong untuk melakukan lindung nilai (*hedging*) valas secara aktif guna mengompensasi kenaikan biaya produksi barang akibat tingginya kekhawatiran aspek 'harga barang'.
    3.  **💼 Investor & Pelaku Pasar Keuangan**: Disarankan melakukan penyesuaian (*rebalancing*) alokasi portofolio ke aset defensif secara dini karena puncak histeria digital sering kali menjadi sinyal awal terjadinya aksi jual masif di pasar modal domestik.
*   **File Kode**: Dirender di `app.py` baris 773-825.

---

## 5. Cara Menjalankan Dashboard

Untuk menjalankan aplikasi ini secara lokal di sistem Anda:

1.  Buka terminal PowerShell pada direktori proyek:
    ```powershell
    cd "c:\Users\ARV\Downloads\rupiah\absa-dashboard-indobert-main\absa-dashboard-indobert-main"
    ```
2.  Pastikan dependensi di `requirements.txt` telah terinstal:
    ```powershell
    pip install -r requirements.txt
    ```
3.  Jalankan aplikasi Streamlit:
    ```powershell
    streamlit run app.py
    ```
4.  Browser akan otomatis terbuka menampilkan dashboard di alamat: `http://localhost:8501`.
