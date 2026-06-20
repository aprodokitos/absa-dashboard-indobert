import pandas as pd
import torch

from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix
)

from utils.model_loader import (
    load_model,
    predict,
    ASPECT_MAP,
    SENTIMENT_MAP
)


def evaluate_model():

    df_test = pd.read_csv(
        "data/dolar_rupiah_test.csv"
    )

    model, tokenizer = load_model()

    aspect_true = []
    aspect_pred = []

    sentiment_true = []
    sentiment_pred = []

    for _, row in df_test.iterrows():

        text = str(row["clean_text"])

        pred_aspect, pred_sentiment = predict(
            text,
            model,
            tokenizer
        )

        aspect_true.append(
            row["aspect"]
        )

        sentiment_true.append(
            row["sentiment"]
        )

        aspect_pred.append(
            pred_aspect
        )

        sentiment_pred.append(
            pred_sentiment
        )

    aspect_acc = accuracy_score(
        aspect_true,
        aspect_pred
    )

    sentiment_acc = accuracy_score(
        sentiment_true,
        sentiment_pred
    )

    aspect_pr, aspect_rc, aspect_f1, _ = (
        precision_recall_fscore_support(
            aspect_true,
            aspect_pred,
            average="macro"
        )
    )

    sentiment_pr, sentiment_rc, sentiment_f1, _ = (
        precision_recall_fscore_support(
            sentiment_true,
            sentiment_pred,
            average="macro"
        )
    )

    cm_aspect = confusion_matrix(
        aspect_true,
        aspect_pred,
        labels=list(ASPECT_MAP.keys())
    )

    cm_sentiment = confusion_matrix(
        sentiment_true,
        sentiment_pred,
        labels=list(SENTIMENT_MAP.keys())
    )

    return {
        "aspect_acc": aspect_acc,
        "aspect_precision": aspect_pr,
        "aspect_recall": aspect_rc,
        "aspect_f1": aspect_f1,

        "sentiment_acc": sentiment_acc,
        "sentiment_precision": sentiment_pr,
        "sentiment_recall": sentiment_rc,
        "sentiment_f1": sentiment_f1,

        "cm_aspect": cm_aspect,
        "cm_sentiment": cm_sentiment
    }