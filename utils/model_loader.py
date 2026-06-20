import torch
import torch.nn as nn
import torch.nn.functional as F

from transformers import (
    BertModel,
    AutoTokenizer
)

# =====================================================
# CONFIG
# =====================================================

MODEL_NAME = "indobenchmark/indobert-base-p1"

# =====================================================
# LABEL MAP
# =====================================================

ASPECT_MAP = {
    "Harga barang": 0,
    "Investasi": 1,
    "Ekspor": 2,
    "Ekonomi nasional": 3,
    "Umum": 4
}

INV_ASPECT_MAP = {
    v: k for k, v in ASPECT_MAP.items()
}

SENTIMENT_MAP = {
    "Negatif": 0,
    "Netral": 1,
    "Positif": 2
}

INV_SENTIMENT_MAP = {
    v: k for k, v in SENTIMENT_MAP.items()
}

# =====================================================
# MODEL
# =====================================================

class IndoBERTABSA(nn.Module):

    def __init__(self):

        super().__init__()

        self.bert = BertModel.from_pretrained(
            MODEL_NAME
        )

        self.dropout = nn.Dropout(0.3)

        self.aspect_classifier = nn.Linear(
            self.bert.config.hidden_size,
            5
        )

        self.sentiment_classifier = nn.Linear(
            self.bert.config.hidden_size,
            3
        )

    def forward(
        self,
        input_ids,
        attention_mask
    ):

        outputs = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask
        )

        pooled_output = outputs.pooler_output

        pooled_output = self.dropout(
            pooled_output
        )

        aspect_logits = self.aspect_classifier(
            pooled_output
        )

        sentiment_logits = self.sentiment_classifier(
            pooled_output
        )

        return (
            aspect_logits,
            sentiment_logits
        )

# =====================================================
# LOAD MODEL
# =====================================================

def load_model():
    import os
    import urllib.request
    import streamlit as st

    model_path = "model/model_indobert_absa/pytorch_model.bin"
    
    # Check if the weight file is missing
    if not os.path.exists(model_path):
        # Read from streamlit secrets, fallback to default Hugging Face repository URL
        download_url = st.secrets.get("MODEL_URL", "https://huggingface.co/azzriala/indobert-absa/resolve/main/pytorch_model.bin")
        
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            
            # Show a download info message in Streamlit
            st.info("ℹ️ Mengunduh bobot model IndoBERT ABSA (~498 MB) untuk pertama kalinya. Proses ini memerlukan waktu beberapa menit...")
            
            # Download file
            urllib.request.urlretrieve(download_url, model_path)
            st.success("✅ Bobot model berhasil diunduh!")
        except Exception as e:
            # Raise exception so app fallback takes over in app.py
            raise FileNotFoundError(f"Gagal mengunduh bobot model dari {download_url}: {e}")

    tokenizer = AutoTokenizer.from_pretrained(
        "model/model_indobert_absa"
    )

    model = IndoBERTABSA()

    model.load_state_dict(
        torch.load(
            model_path,
            map_location=torch.device("cpu")
        )
    )

    model.eval()

    return model, tokenizer

# =====================================================
# PREDICTION
# =====================================================

@torch.no_grad()
def predict(
    text,
    model,
    tokenizer
):

    encoded = tokenizer(
        text,
        max_length=128,
        padding="max_length",
        truncation=True,
        return_tensors="pt"
    )

    input_ids = encoded["input_ids"]
    attention_mask = encoded["attention_mask"]

    aspect_logits, sentiment_logits = model(
        input_ids,
        attention_mask
    )

    # -----------------------------
    # Softmax Probabilities
    # -----------------------------

    aspect_probs = F.softmax(
        aspect_logits,
        dim=1
    )

    sentiment_probs = F.softmax(
        sentiment_logits,
        dim=1
    )

    # -----------------------------
    # Predicted Class
    # -----------------------------

    aspect_idx = torch.argmax(
        aspect_probs,
        dim=1
    ).item()

    sentiment_idx = torch.argmax(
        sentiment_probs,
        dim=1
    ).item()

    # -----------------------------
    # Confidence Score
    # -----------------------------

    aspect_confidence = (
        aspect_probs[0][aspect_idx].item()
        * 100
    )

    sentiment_confidence = (
        sentiment_probs[0][sentiment_idx].item()
        * 100
    )

    return (
        INV_ASPECT_MAP[aspect_idx],
        INV_SENTIMENT_MAP[sentiment_idx],
        aspect_confidence,
        sentiment_confidence
    )

# model_loader successfully loaded