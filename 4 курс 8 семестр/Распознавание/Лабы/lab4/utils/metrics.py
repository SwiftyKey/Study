import numpy as np
from typing import Tuple


def confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    """
    Вычисляет матрицу ошибок для бинарной классификации.
    """

    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    # TN: (фактически 0, предсказано 0)
    tn = np.sum((y_true == 0) & (y_pred == 0))

    # FP: (фактически 0, предсказано 1)
    fp = np.sum((y_true == 0) & (y_pred == 1))

    # FN: (фактически 1, предсказано 0)
    fn = np.sum((y_true == 1) & (y_pred == 0))

    # TP: (фактически 1, предсказано 1)
    tp = np.sum((y_true == 1) & (y_pred == 1))

    return np.array([[tn, fp], [fn, tp]])


def accuracy_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Вычисляет долю правильных предсказаний.

    (TP + TN) / (TP + TN + FP + FN)
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    correct = np.sum(y_true == y_pred)
    total = len(y_true)

    return correct / total if total > 0 else 0.0


def precision_score(y_true: np.ndarray, y_pred: np.ndarray, zero_division: float = 0.0) -> float:
    """
    Вычисляет точность (precision) для положительного класса.

    TP / (TP + FP)
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    tp = np.sum((y_true == 1) & (y_pred == 1))
    fp = np.sum((y_true == 0) & (y_pred == 1))

    denominator = tp + fp

    if denominator == 0:
        return zero_division

    return tp / denominator


def recall_score(y_true: np.ndarray, y_pred: np.ndarray, zero_division: float = 0.0) -> float:
    """
    Вычисляет полноту (recall) для положительного класса.

    TP / (TP + FN)
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    tp = np.sum((y_true == 1) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))

    denominator = tp + fn

    if denominator == 0:
        return zero_division

    return tp / denominator


def f1_score(y_true: np.ndarray, y_pred: np.ndarray, zero_division: float = 0.0) -> float:
    """
    Вычисляет F1-меру (гармоническое среднее precision и recall).

    2 * (Precision * Recall) / (Precision + Recall)
    """
    prec = precision_score(y_true, y_pred, zero_division=zero_division)
    rec = recall_score(y_true, y_pred, zero_division=zero_division)

    denominator = prec + rec

    if denominator == 0:
        return zero_division

    return 2 * (prec * rec) / denominator


def roc_curve(y_true: np.ndarray, y_prob: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Вычисляет ROC-кривую (FP Rate vs TP Rate).
    """
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)

    # Сортируем по убыванию вероятности
    desc_score_indices = np.argsort(y_prob)[::-1]
    y_true_sorted = y_true[desc_score_indices]
    y_prob_sorted = y_prob[desc_score_indices]

    # Уникальные пороги + границы
    thresholds = np.unique(y_prob_sorted)[::-1]
    thresholds = np.concatenate([thresholds, [thresholds[-1] - 0.001]])

    n_neg = np.sum(y_true == 0)

    fpr = []
    tpr = []

    for thresh in thresholds:
        y_pred = (y_prob >= thresh).astype(int)

        fp = np.sum((y_true == 0) & (y_pred == 1))

        tpr.append(recall_score(y_true, y_pred))
        fpr.append(fp / n_neg if n_neg > 0 else 0.0)

    fpr = [0.0] + fpr
    tpr = [0.0] + tpr
    thresholds = np.concatenate([[1.0 + 0.001], thresholds])

    return np.array(fpr), np.array(tpr), thresholds


def auc(x: np.ndarray, y: np.ndarray) -> float:
    """
    Вычисляет площадь под кривой (Area Under Curve) методом трапеций.
    """
    x = np.asarray(x)
    y = np.asarray(y)

    sort_indices = np.argsort(x)
    x_sorted = x[sort_indices]
    y_sorted = y[sort_indices]

    area = 0.0
    for i in range(1, len(x_sorted)):
        dx = x_sorted[i] - x_sorted[i - 1]
        avg_height = (y_sorted[i] + y_sorted[i - 1]) / 2
        area += dx * avg_height

    return area


def precision_recall_curve(y_true: np.ndarray, y_prob: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Вычисляет Precision-Recall кривую.
    """
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)

    # Сортируем по убыванию вероятности
    desc_score_indices = np.argsort(y_prob)[::-1]
    y_prob_sorted = y_prob[desc_score_indices]

    # Уникальные пороги
    thresholds = np.unique(y_prob_sorted)[::-1]

    precision = []
    recall = []
    n_pos = np.sum(y_true == 1)

    for thresh in thresholds:
        y_pred = (y_prob >= thresh).astype(int)

        prec = precision_score(y_true, y_pred)
        rec = recall_score(y_true, y_pred)

        precision.append(prec)
        recall.append(rec)

    precision.append(n_pos / len(y_true) if len(y_true) > 0 else 0.0)
    recall.append(1.0)

    return np.array(precision), np.array(recall), thresholds


def average_precision_score(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """
    Вычисляет среднюю точность (Area Under PR Curve).

    Использует аппроксимацию через сумму прямоугольников.
    """
    precision, recall, _ = precision_recall_curve(y_true, y_prob)

    # Вычисляем площадь под PR кривой
    # Сортируем по recall для правильного интегрирования
    sort_indices = np.argsort(recall)
    recall_sorted = recall[sort_indices]
    precision_sorted = precision[sort_indices]

    ap = 0.0
    for i in range(1, len(recall_sorted)):
        dr = recall_sorted[i] - recall_sorted[i - 1]
        ap += dr * precision_sorted[i]

    return ap
