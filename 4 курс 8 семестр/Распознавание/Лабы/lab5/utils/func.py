import json
import numpy as np
from typing import List, Dict, Tuple


def iou(box1: List[float], box2: List[float]) -> float:
    """
    Вычисляет IoU между двумя боксами [x, y, w, h].
    """
    x1_min, y1_min = box1[0], box1[1]
    x1_max, y1_max = box1[0] + box1[2], box1[1] + box1[3]

    x2_min, y2_min = box2[0], box2[1]
    x2_max, y2_max = box2[0] + box2[2], box2[1] + box2[3]

    inter_x_min = max(x1_min, x2_min)
    inter_y_min = max(y1_min, y2_min)
    inter_x_max = min(x1_max, x2_max)
    inter_y_max = min(y1_max, y2_max)

    inter_w = max(0, inter_x_max - inter_x_min)
    inter_h = max(0, inter_y_max - inter_y_min)
    inter_area = inter_w * inter_h

    area1 = box1[2] * box1[3]
    area2 = box2[2] * box2[3]

    union_area = area1 + area2 - inter_area

    if union_area == 0:
        return 0.0

    return inter_area / union_area


def bbox_xywh_to_xyxy(bbox: List[float]) -> List[float]:
    """Конвертирует [x, y, w, h] → [x_min, y_min, x_max, y_max]"""
    return [bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3]]


def load_coco_annotations(path: str) -> Dict:
    """Загружает Ground Truth в формате COCO"""
    with open(path, 'r') as f:
        return json.load(f)


def load_predictions(path: str) -> List[Dict]:
    """Загружает предсказания модели"""
    with open(path, 'r') as f:
        return json.load(f)


def compute_ap_at_iou_threshold(
    gt_annotations: List[Dict],
    predictions: List[Dict],
    category_id: int,
    iou_threshold: float
) -> float:
    """
    Вычисляет Average Precision для одного класса при заданном пороге IoU.
    """
    gt_boxes = [ann for ann in gt_annotations if ann['category_id'] == category_id]
    pred_boxes = [pred for pred in predictions if pred['category_id'] == category_id]
    pred_boxes.sort(key=lambda x: x['score'], reverse=True)
    gt_matched = [False] * len(gt_boxes)
    tp = []
    fp = []

    for pred in pred_boxes:
        pred_box = pred['bbox']
        image_id = pred['image_id']

        gt_candidates = [
            (i, gt) for i, gt in enumerate(gt_boxes)
            if gt['image_id'] == image_id and not gt_matched[i]
        ]

        if not gt_candidates:
            fp.append(1)
            tp.append(0)
            continue

        best_iou = 0.0
        best_gt_idx = -1

        for gt_idx, gt in gt_candidates:
            iou_val = iou(pred_box, gt['bbox'])
            if iou_val > best_iou:
                best_iou = iou_val
                best_gt_idx = gt_idx

        if best_iou >= iou_threshold:
            tp.append(1)
            fp.append(0)
            gt_matched[best_gt_idx] = True
        else:
            tp.append(0)
            fp.append(1)

    tp = np.array(tp)
    fp = np.array(fp)

    if len(tp) == 0:
        return 0.0

    cum_tp = np.cumsum(tp)
    cum_fp = np.cumsum(fp)

    recall = cum_tp / len(gt_boxes) if len(gt_boxes) > 0 else np.zeros_like(cum_tp)
    precision = cum_tp / (cum_tp + cum_fp)

    for i in range(len(precision) - 1, 0, -1):
        precision[i - 1] = max(precision[i - 1], precision[i])

    ap = 0.0
    for i in range(1, len(recall)):
        dr = recall[i] - recall[i - 1]
        ap += dr * precision[i]

    return ap


def compute_map(
    gt_path: str,
    pred_path: str,
    iou_thresholds: List[float] = None
) -> Dict:
    """
    Вычисляет mAP для всех классов и порогов IoU.
    """
    if iou_thresholds is None:
        iou_thresholds = [0.5]

    gt_data = load_coco_annotations(gt_path)
    predictions = load_predictions(pred_path)

    gt_annotations = gt_data['annotations']
    categories = gt_data['categories']

    results = {
        'map_per_iou': {},
        'map_per_class': {},
        'map_summary': {}
    }

    for iou_thresh in iou_thresholds:
        ap_per_class = []

        for cat in categories:
            cat_id = cat['id']
            cat_name = cat['name']
            ap = compute_ap_at_iou_threshold(gt_annotations, predictions, cat_id, iou_thresh)
            ap_per_class.append(ap)

            if iou_thresh not in results['map_per_class']:
                results['map_per_class'][iou_thresh] = {}

            results['map_per_class'][iou_thresh][cat_name] = ap

        map_value = np.mean(ap_per_class) if ap_per_class else 0.0
        results['map_per_iou'][iou_thresh] = map_value

    # mAP@0.5:0.95 (10 порогов)
    iou_range = np.arange(0.5, 0.96, 0.05)
    ap_all_thresholds = []

    for iou_thresh in iou_range:
        ap_per_class = []

        for cat in categories:
            ap = compute_ap_at_iou_threshold(gt_annotations, predictions, cat['id'], iou_thresh)
            ap_per_class.append(ap)

        ap_all_thresholds.append(np.mean(ap_per_class) if ap_per_class else 0.0)

    results['map_summary']['mAP@0.5'] = results['map_per_iou'].get(0.5, 0.0)
    results['map_summary']['mAP@0.5:0.95'] = np.mean(ap_all_thresholds)

    return results


def analyze_errors(
    gt_path: str,
    pred_path: str,
    iou_threshold: float = 0.5
) -> Tuple[List[Dict], List[Dict]]:
    """
    Находит FP и FN примеры.
    """
    gt_data = load_coco_annotations(gt_path)
    predictions = load_predictions(pred_path)
    gt_annotations = gt_data['annotations']
    images = {img['id']: img for img in gt_data['images']}
    fp_examples = []
    fn_examples = []

    gt_by_image = {}
    for ann in gt_annotations:
        img_id = ann['image_id']
        if img_id not in gt_by_image:
            gt_by_image[img_id] = []
        gt_by_image[img_id].append(ann)

    pred_by_image = {}
    for pred in predictions:
        img_id = pred['image_id']
        if img_id not in pred_by_image:
            pred_by_image[img_id] = []
        pred_by_image[img_id].append(pred)

    for img_id, gt_boxes in gt_by_image.items():
        pred_boxes = pred_by_image.get(img_id, [])
        gt_matched = [False] * len(gt_boxes)

        for pred in pred_boxes:
            pred_box = pred['bbox']
            best_iou = 0.0
            best_gt_idx = -1

            for gt_idx, gt in enumerate(gt_boxes):
                if gt_matched[gt_idx]:
                    continue

                iou_val = iou(pred_box, gt['bbox'])
                if iou_val > best_iou:
                    best_iou = iou_val
                    best_gt_idx = gt_idx

            if best_iou >= iou_threshold:
                gt_matched[best_gt_idx] = True
            else:
                fp_examples.append({
                    'image_id': img_id,
                    'image_name': images[img_id]['file_name'],
                    'prediction': pred,
                    'iou': best_iou,
                    'reason': 'no_matching_gt'
                })

        for gt_idx, gt in enumerate(gt_boxes):
            if not gt_matched[gt_idx]:
                fn_examples.append({
                    'image_id': img_id,
                    'image_name': images[img_id]['file_name'],
                    'ground_truth': gt,
                    'category_id': gt['category_id']
                })

    return fp_examples, fn_examples


def analyze_error_patterns(
    fp_examples: List[Dict],
    fn_examples: List[Dict],
    gt_path: str
) -> Dict:
    """
    Анализирует паттерны ошибок и гипотезы.
    """
    gt_data = load_coco_annotations(gt_path)
    gt_annotations = gt_data['annotations']

    gt_areas = [ann['area'] for ann in gt_annotations]
    small_gt = sum(1 for area in gt_areas if area < 1000)
    medium_gt = sum(1 for area in gt_areas if 1000 <= area < 5000)
    large_gt = sum(1 for area in gt_areas if area >= 5000)

    fn_areas = [fn['ground_truth']['area'] for fn in fn_examples]
    fn_small = sum(1 for area in fn_areas if area < 1000)
    fn_medium = sum(1 for area in fn_areas if 1000 <= area < 5000)
    fn_large = sum(1 for area in fn_areas if area >= 5000)

    fp_scores = [fp['prediction']['score'] for fp in fp_examples]
    avg_fp_score = np.mean(fp_scores) if fp_scores else 0

    hypotheses = {
        'fn_small_objects': fn_small / len(fn_examples) if fn_examples else 0,
        'fn_medium_objects': fn_medium / len(fn_examples) if fn_examples else 0,
        'fn_large_objects': fn_large / len(fn_examples) if fn_examples else 0,
        'avg_fp_confidence': avg_fp_score,
        'total_fp': len(fp_examples),
        'total_fn': len(fn_examples)
    }

    return hypotheses
