import numpy as np
import matplotlib.pyplot as plt
import cv2
import os

from pathlib import Path
from typing import Dict, List
from utils import compute_map, analyze_errors, analyze_error_patterns


BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))


def visualize_fp_fn(
    fp_examples: List[Dict],
    fn_examples: List[Dict],
    output_dir: str = 'error_visualizations',
    max_samples: int = 5
):
    """
    Визуализирует FP и FN примеры.
    """
    Path(output_dir).mkdir(exist_ok=True)

    if fp_examples:
        fig, axes = plt.subplots(1, min(len(fp_examples), max_samples), figsize=(15, 5))
        if len(fp_examples) == 1:
            axes = [axes]

        for i, fp in enumerate(fp_examples[:max_samples]):
            img = np.ones((480, 640, 3), dtype=np.uint8) * 255

            pred_box = fp['prediction']['bbox']
            x, y, w, h = pred_box

            rect = plt.Rectangle((x, y), w, h, fill=False,
                                  color='red', linewidth=3,
                                  label=f'FP (score={fp["prediction"]["score"]:.2f})')

            axes[i].imshow(img)
            axes[i].add_patch(rect)
            axes[i].set_title(f'False Positive\nIoU={fp["iou"]:.2f}',
                             fontsize=10, color='red')
            axes[i].axis('off')

        plt.tight_layout()
        plt.savefig(f'{output_dir}/false_positives.png', dpi=150)
        plt.close()
        print(f"FP примеры сохранены: {output_dir}/false_positives.png")

    if fn_examples:
        fig, axes = plt.subplots(1, min(len(fn_examples), max_samples), figsize=(15, 5))
        if len(fn_examples) == 1:
            axes = [axes]

        for i, fn in enumerate(fn_examples[:max_samples]):
            img = np.ones((480, 640, 3), dtype=np.uint8) * 255

            gt_box = fn['ground_truth']['bbox']
            x, y, w, h = gt_box

            rect = plt.Rectangle((x, y), w, h, fill=False,
                                  color='green', linewidth=3,
                                  label='FN (missed)')

            axes[i].imshow(img)
            axes[i].add_patch(rect)
            axes[i].set_title(f'False Negative\nCategory={fn["category_id"]}',
                             fontsize=10, color='green')
            axes[i].axis('off')

        plt.tight_layout()
        plt.savefig(f'{output_dir}/false_negatives.png', dpi=150)
        plt.close()
        print(f"FN примеры сохранены: {output_dir}/false_negatives.png")


def print_error_analysis(hypotheses: Dict):
    """Выводит анализ причин ошибок"""
    print("\n" + "=" * 60)
    print("АНАЛИЗ ПРИЧИН ОШИБОК")
    print("=" * 60)

    print(f"\nСтатистика ошибок:")
    print(f"   False Positive: {hypotheses['total_fp']}")
    print(f"   False Negative: {hypotheses['total_fn']}")
    print(f"   Средняя уверенность FP: {hypotheses['avg_fp_confidence']:.2f}")

    print(f"\nРаспределение FN по размерам:")
    print(f"   Малые объекты (<1000 px²): {hypotheses['fn_small_objects']*100:.1f}%")
    print(f"   Средние объекты (1000-5000 px²): {hypotheses['fn_medium_objects']*100:.1f}%")
    print(f"   Крупные объекты (>5000 px²): {hypotheses['fn_large_objects']*100:.1f}%")

    print("\nГипотезы о причинах ошибок:")

    if hypotheses['fn_small_objects'] > 0.5:
        print("   Большинство FN — малые объекты")
        print("      -> Увеличить разрешение входа или использовать FPN")

    if hypotheses['avg_fp_confidence'] > 0.7:
        print("   FP имеют высокую уверенность")
        print("      -> Возможны сложные паттерны фона, похожие на объекты")
        print("      -> Добавить hard negative mining")

    if hypotheses['total_fp'] > hypotheses['total_fn'] * 2:
        print("   Много ложных срабатываний")
        print("      -> Повысить confidence threshold")
        print("      -> Добавить NMS с более строгим IoU")

    if hypotheses['total_fn'] > hypotheses['total_fp'] * 2:
        print("   Много пропущенных объектов")
        print("      -> Понизить confidence threshold")
        print("      -> Проверить аугментации на переобучение")


def main():
    print("=" * 60)
    print("ОЦЕНКА ДЕТЕКТОРА ОБЪЕКТОВ")
    print("=" * 60)

    gt_path = BASE_DIR / 'data/annotations/instances_val.json'
    pred_path = BASE_DIR / 'data/predictions/detections.json'

    if not Path(gt_path).exists():
        print(f"Ground Truth не найден: {gt_path}")
        print("   Создайте пример данных (см. документацию)")
        return

    if not Path(pred_path).exists():
        print(f"Предсказания не найдены: {pred_path}")
        print("   Создайте пример данных (см. документацию)")
        return

    print("\n" + "=" * 60)
    print("ВЫЧИСЛЕНИЕ mAP")
    print("=" * 60)

    # mAP@0.5
    results_05 = compute_map(gt_path, pred_path, iou_thresholds=[0.5])
    print(f"\nmAP@0.5: {results_05['map_summary']['mAP@0.5']:.4f}")

    # mAP@0.5:0.95
    results_range = compute_map(gt_path, pred_path, iou_thresholds=np.arange(0.5, 0.96, 0.05))
    print(f"mAP@0.5:0.95: {results_range['map_summary']['mAP@0.5:0.95']:.4f}")

    print("\nmAP по классам (IoU=0.5):")
    for cat_name, ap in results_05['map_per_class'][0.5].items():
        print(f"   {cat_name}: {ap:.4f}")

    print("\n" + "=" * 60)
    print("АНАЛИЗ ОШИБОК (FP/FN)")
    print("=" * 60)

    fp_examples, fn_examples = analyze_errors(gt_path, pred_path, iou_threshold=0.5)

    print(f"\nНайдено ошибок:")
    print(f"   False Positive: {len(fp_examples)}")
    print(f"   False Negative: {len(fn_examples)}")

    print("\n" + "=" * 60)
    print("ВИЗУАЛИЗАЦИЯ")
    print("=" * 60)

    visualize_fp_fn(fp_examples, fn_examples,
                    output_dir='error_visualizations', max_samples=5)

    hypotheses = analyze_error_patterns(fp_examples, fn_examples, gt_path)
    print_error_analysis(hypotheses)

    print("\n" + "=" * 60)
    print("💡 РЕКОМЕНДАЦИИ")
    print("=" * 60)
    print("""
1. Для малых объектов:
   - Увеличить входное разрешение (640->1280)
   - Использовать FPN (Feature Pyramid Network)
   - Добавить аугментации scale (Copy-Paste)

2. Для FP с высокой уверенностью:
   - Hard Negative Mining
   - Добавить сложные негативные примеры в обучение
   - Использовать более строгий NMS

3. Баланс Precision/Recall:
   - Настроить confidence threshold под задачу
   - Для безопасности: приоритет Recall (ниже порог)
   - Для экономики: приоритет Precision (выше порог)

4. Мониторинг:
   - Отслеживать mAP@0.5:0.95 (честнее чем mAP@0.5)
   - Анализировать ошибки по размерам объектов
   - Вести лог FP/FN для итеративного улучшения
""")

    print("\n" + "=" * 60)
    print("ОЦЕНКА ЗАВЕРШЕНА")
    print("=" * 60)


if __name__ == '__main__':
    main()
