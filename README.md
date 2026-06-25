# ABSA Dashboard

Dashboard Aspect-Based Sentiment Analysis (ABSA) terhadap respons publik mengenai kenaikan kurs Dolar AS terhadap Rupiah menggunakan IndoBERT dan Explainable AI (SHAP).

## Persiapan Model

Repository ini tidak menyertakan model IndoBERT hasil fine-tuning karena ukuran file melebihi batas GitHub.

Sebelum menjalankan dashboard:

1. Jalankan notebook training:

```bash
IndoBERT_ABSA_Train.ipynb
```

2. Simpan hasil fine-tuning model.

3. Buat folder berikut:

```text
model/
└── model_indobert_absa/
```

4. Letakkan file model hasil training ke dalam folder tersebut:

```text
model/model_indobert_absa/
├── pytorch_model.bin
├── tokenizer.json
├── tokenizer_config.json
```

---

## Instalasi

Clone repository:

```bash
git clone https://github.com/USERNAME/absa-dashboard.git
cd absa-dashboard
```

Install dependency:

```bash
pip install -r requirements.txt
```

---

## Menjalankan Dashboard

```bash
python -m streamlit run app.py
```

Dashboard akan berjalan pada:

```text
http://localhost:8501
```

---

## Teknologi yang Digunakan

* Python
* Streamlit
* Pandas
* Plotly
* Scikit-Learn
* Hugging Face Transformers
* IndoBERT
* SHAP

---
