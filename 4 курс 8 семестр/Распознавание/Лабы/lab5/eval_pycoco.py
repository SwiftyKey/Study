import json
import os
from pathlib import Path
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval


BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))


def evaluate_with_pycocotools(gt_path: str, pred_path: str):
    """Оценка с использованием официальной pycocotools"""
    coco_gt = COCO(gt_path)

    with open(pred_path, 'r') as f:
        predictions = json.load(f)

    temp_pred_path = 'temp_predictions.json'
    with open(temp_pred_path, 'w') as f:
        json.dump(predictions, f)

    coco_dt = coco_gt.loadRes(temp_pred_path)
    coco_eval = COCOeval(coco_gt, coco_dt, iouType='bbox')

    coco_eval.evaluate()
    coco_eval.accumulate()
    coco_eval.summarize()

    print("\n" + "=" * 60)
    print("COCO Evaluation Results")
    print("=" * 60)
    print(f"mAP@0.5:0.95: {coco_eval.stats[0]:.4f}")
    print(f"mAP@0.5:      {coco_eval.stats[1]:.4f}")
    print(f"mAP@0.75:    {coco_eval.stats[2]:.4f}")
    print(f"mAP (small): {coco_eval.stats[3]:.4f}")
    print(f"mAP (medium):{coco_eval.stats[4]:.4f}")
    print(f"mAP (large): {coco_eval.stats[5]:.4f}")

    return coco_eval.stats


if __name__ == '__main__':
    evaluate_with_pycocotools(BASE_DIR / 'data/annotations/instances_val.json',
                              BASE_DIR / 'data/predictions/detections.json')
