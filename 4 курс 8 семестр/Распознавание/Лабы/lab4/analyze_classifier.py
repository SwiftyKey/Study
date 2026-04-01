import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path


USE_SKLEARN = False

if USE_SKLEARN:
    print("Используем метрики из sklearn")
    from sklearn.metrics import (
        accuracy_score, precision_score, recall_score, f1_score,
        confusion_matrix, roc_curve, auc, precision_recall_curve,
        average_precision_score
    )
else:
    print("Используем собственную реализацию метрик")
    from utils.metrics import (
        accuracy_score, precision_score, recall_score, f1_score,
        confusion_matrix, roc_curve, auc, precision_recall_curve,
        average_precision_score
    )

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

plt.style.use('seaborn-v0_8')
plt.rcParams['figure.figsize'] = (12, 5)
plt.rcParams['font.size'] = 12

df = pd.read_csv(BASE_DIR / 'dataset.csv')
print("=" * 60)
print("ИСХОДНЫЕ ДАННЫЕ")
print("=" * 60)
print(f"Общее количество примеров: {len(df)}")
print(f"Класс 0 (нет дефекта): {(df['label'] == 0).sum()}")
print(f"Класс 1 (дефект): {(df['label'] == 1).sum()}")
print(f"Дисбаланс классов: {(df['label'] == 0).sum() / (df['label'] == 1).sum():.1f}:1")

threshold = 0.5
y_true = df['label'].values
y_pred = (df['pred_prob'] >= threshold).astype(int)

print("\n" + "=" * 60)
print(f"МЕТРИКИ ПРИ ПОРОГЕ {threshold}")
print("=" * 60)

accuracy = accuracy_score(y_true, y_pred)
precision = precision_score(y_true, y_pred)
recall = recall_score(y_true, y_pred)
f1 = f1_score(y_true, y_pred)

print(f"Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"Precision: {precision:.4f} ({precision*100:.2f}%)")
print(f"Recall:    {recall:.4f} ({recall*100:.2f}%)")
print(f"F1-Score:  {f1:.4f} ({f1*100:.2f}%)")

cm = confusion_matrix(y_true, y_pred)
print(f"\nМатрица ошибок:")
print(f"                Предсказано 0  Предсказано 1")
print(f"Фактически 0:   {cm[0, 0]:>12}  {cm[0, 1]:>12} <- Ложные срабатывания: {cm[0, 1]}")
print(f"Фактически 1:   {cm[1, 0]:>12}  {cm[1, 1]:>12} <- Пропущенные дефекты: {cm[1, 0]}")

print("\n" + "=" * 60)
print("ROC И PR КРИВЫЕ")
print("=" * 60)

fpr, tpr, roc_thresholds = roc_curve(y_true, df['pred_prob'])
roc_auc = auc(fpr, tpr)

precision_curve, recall_curve, pr_thresholds = precision_recall_curve(y_true, df['pred_prob'])
pr_auc = average_precision_score(y_true, df['pred_prob'])

print(f"ROC-AUC: {roc_auc:.4f}")
print(f"PR-AUC:  {pr_auc:.4f}")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC кривая (AUC = {roc_auc:.2f})')
axes[0].plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Случайный классификатор')
axes[0].set_xlim([0.0, 1.0])
axes[0].set_ylim([0.0, 1.05])
axes[0].set_xlabel('False Positive Rate (FPR)')
axes[0].set_ylabel('True Positive Rate (TPR / Recall)')
axes[0].set_title('ROC Кривая')
axes[0].legend(loc='lower right')
axes[0].grid(alpha=0.3)

axes[1].plot(recall_curve, precision_curve, color='blue', lw=2, label=f'PR кривая (AUC = {pr_auc:.2f})')
axes[1].set_xlim([0.0, 1.0])
axes[1].set_ylim([0.0, 1.05])
axes[1].set_xlabel('Recall (Полнота)')
axes[1].set_ylabel('Precision (Точность)')
axes[1].set_title('Precision-Recall Кривая')
axes[1].legend(loc='lower left')
axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig(BASE_DIR / 'roc_pr_curves.png', dpi=150)
plt.show()

print("\n" + "=" * 60)
print("ПОИСК ОПТИМАЛЬНОГО ПОРОГА (Recall >= 0.95)")
print("=" * 60)

thresholds = np.arange(0.01, 1.0, 0.01)
results = []

for thresh in thresholds:
    y_pred_temp = (df['pred_prob'] >= thresh).astype(int)
    rec = recall_score(y_true, y_pred_temp)
    prec = precision_score(y_true, y_pred_temp, zero_division=0)
    f1_temp = f1_score(y_true, y_pred_temp, zero_division=0)
    acc = accuracy_score(y_true, y_pred_temp)

    results.append({
        'threshold': thresh,
        'recall': rec,
        'precision': prec,
        'f1': f1_temp,
        'accuracy': acc
    })

results_df = pd.DataFrame(results)

valid_thresholds = results_df[results_df['recall'] >= 0.95]

if len(valid_thresholds) > 0:
    optimal = valid_thresholds.loc[valid_thresholds['precision'].idxmax()]

    print(f"\nОптимальный порог: {optimal['threshold']:.2f}")
    print(f"   Recall:    {optimal['recall']:.4f} ({optimal['recall']*100:.2f}%)")
    print(f"   Precision: {optimal['precision']:.4f} ({optimal['precision']*100:.2f}%)")
    print(f"   F1-Score:  {optimal['f1']:.4f} ({optimal['f1']*100:.2f}%)")
    print(f"   Accuracy:  {optimal['accuracy']:.4f} ({optimal['accuracy']*100:.2f}%)")

    y_pred_optimal = (df['pred_prob'] >= optimal['threshold']).astype(int)
    cm_optimal = confusion_matrix(y_true, y_pred_optimal)

    print(f"\n   Матрица ошибок при пороге {optimal['threshold']:.2f}:")
    print(f"                   Предсказано 0  Предсказано 1")
    print(f"   Фактически 0:   {cm_optimal[0, 0]:>12}  {cm_optimal[0, 1]:>12}")
    print(f"   Фактически 1:   {cm_optimal[1, 0]:>12}  {cm_optimal[1, 1]:>12}")
    print(f"   -> Пропущено дефектов: {cm_optimal[1, 0]}")
    print(f"   -> Ложных срабатываний: {cm_optimal[0, 1]}")
else:
    print("Не удалось найти порог с Recall >= 0.95")
    optimal = results_df.loc[results_df['recall'].idxmax()]
    print(f"   Лучший доступный Recall: {optimal['recall']:.4f} при пороге {optimal['threshold']:.2f}")

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(results_df['threshold'], results_df['recall'], label='Recall', color='red', linewidth=2)
ax.plot(results_df['threshold'], results_df['precision'], label='Precision', color='blue', linewidth=2)
ax.plot(results_df['threshold'], results_df['f1'], label='F1-Score', color='green', linewidth=2)
ax.axhline(y=0.95, color='red', linestyle='--', alpha=0.5, label='Recall >= 0.95')
if len(valid_thresholds) > 0:
    ax.axvline(x=optimal['threshold'], color='black', linestyle=':', linewidth=2, label=f'Оптимальный порог ({optimal["threshold"]:.2f})')
ax.set_xlabel('Порог классификации')
ax.set_ylabel('Значение метрики')
ax.set_title('Зависимость метрик от порога классификации')
ax.legend(loc='best')
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(BASE_DIR / 'metrics_vs_threshold.png', dpi=150)
plt.show()

print("\n" + "=" * 60)
print("ПОЧЕМУ ACCURACY БЕСПОЛЕЗЕН ПРИ ДИСБАЛАНСЕ?")
print("=" * 60)

y_pred_always_0 = np.zeros(len(y_true))
accuracy_always_0 = accuracy_score(y_true, y_pred_always_0)
recall_always_0 = recall_score(y_true, y_pred_always_0)

print(f"\nЕсли модель предсказывает ВСЕГДА 'нет дефекта' (класс 0):")
print(f"   Accuracy: {accuracy_always_0:.4f} ({accuracy_always_0*100:.2f}%) <- ВЫСОКАЯ!")
print(f"   Recall:   {recall_always_0:.4f} ({recall_always_0*100:.2f}%) <- КРИТИЧЕСКИ НИЗКАЯ!")
print(f"   -> Все дефекты будут пропущены!")

print(f"\nНаша модель при пороге 0.5:")
print(f"   Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"   Recall:   {recall:.4f} ({recall*100:.2f}%)")
print(f"   -> Accuracy похож, но модель реально находит дефекты!")

print(f"\nНаша модель при оптимальном пороге {optimal['threshold']:.2f}:")
print(f"   Accuracy: {optimal['accuracy']:.4f} ({optimal['accuracy']*100:.2f}%) <- УПАЛА!")
print(f"   Recall:   {optimal['recall']:.4f} ({optimal['recall']*100:.2f}%) <- ВЫСОКАЯ!")
print(f"   -> Accuracy снизился, но модель выполняет свою задачу!")

print("\n" + "=" * 60)
print("КЛЮЧЕВЫЕ ВЫВОДЫ")
print("=" * 60)
print("""
1. Accuracy вводит в заблуждение при дисбалансе классов
   - Можно достичь 95%+ точности, просто предсказывая мажоритарный класс
   - Это скрывает полную неспособность находить дефекты

2. При поиске дефектов приоритет у Recall (полноты)
   - Пропуск дефекта = критическая ошибка
   - Ложное срабатывание = дополнительная проверка (менее критично)

3. Используйте правильные метрики:
   - Recall — для оценки полноты обнаружения
   - Precision — для оценки качества срабатываний
   - F1 / Fb-мера — для баланса
   - PR-AUC — вместо ROC-AUC при сильном дисбалансе
   - Матрица ошибок — всегда смотрите на неё!

4. Выбор порога — бизнес-решение
   - Зависит от стоимости пропуска дефекта vs ложного срабатывания
   - В данном случае: Recall >= 0.95 — требование безопасности
""")

results_df.to_csv(BASE_DIR / 'threshold_analysis.csv', index=False)
print(f"\nРезультаты анализа порогов сохранены в 'threshold_analysis.csv'")

print("\n" + "=" * 60)
print("АНАЛИЗ ЗАВЕРШЁН")
print("=" * 60)
