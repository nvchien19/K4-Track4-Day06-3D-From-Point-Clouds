"""Topic A: measure how yaw calibration drift changes LiDAR-to-camera overlays."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np

from starter.datasets import load_frame
from starter.projection import overlay_points, perturb_extrinsic, project_velo_to_image


def _box_membership(uv: np.ndarray, labels) -> tuple[np.ndarray, list[dict]]:
    """Return unique projected points inside any labeled 2D box and per-object counts."""
    all_members = np.zeros(len(uv), dtype=bool)
    objects = []
    for index, obj in enumerate(labels):
        x1, y1, x2, y2 = obj.bbox
        inside = (
            (uv[:, 0] >= x1) & (uv[:, 0] <= x2)
            & (uv[:, 1] >= y1) & (uv[:, 1] <= y2)
        )
        all_members |= inside
        objects.append({
            "object_index": index,
            "class": obj.type,
            "points_in_box": int(inside.sum()),
            "box_area_px": float(max(0, x2 - x1) * max(0, y2 - y1)),
        })
    return all_members, objects


def run(data_root: str, frame_id: str, yaw_degs: list[float], out_dir: Path) -> list[dict]:
    frame = load_frame(data_root, frame_id)
    image = frame["image"]
    raw_points = np.asarray(frame["points"])
    finite_xyz = np.isfinite(raw_points[:, :3]).all(axis=1)
    rows = []
    overlays = []

    for yaw in yaw_degs:
        calib = perturb_extrinsic(frame["calib"], yaw_deg=yaw)
        uv, depth, valid = project_velo_to_image(raw_points, calib, image.shape)
        members, _ = _box_membership(uv, frame["labels"])
        n_projected = int(valid.sum())
        n_box = int(members.sum())
        rows.append({
            "frame": frame_id,
            "yaw_deg": yaw,
            "input_points": int(len(raw_points)),
            "finite_xyz_points": int(finite_xyz.sum()),
            "inside_image_points": n_projected,
            "inside_image_pct_of_finite": 100.0 * n_projected / max(1, int(finite_xyz.sum())),
            "points_in_any_gt_2d_box": n_box,
            "gt_box_pct_of_projected": 100.0 * n_box / max(1, n_projected),
            "labeled_objects": len(frame["labels"]),
        })
        vis = overlay_points(image, uv, depth)
        for obj in frame["labels"]:
            x1, y1, x2, y2 = (int(round(v)) for v in obj.bbox)
            cv2.rectangle(vis, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(vis, obj.type, (x1, max(16, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(vis, f"yaw drift = {yaw:.1f} deg | in FOV = {n_projected} | in GT boxes = {n_box}",
                    (18, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)
        overlays.append((yaw, vis))

    out_dir.mkdir(parents=True, exist_ok=True)
    results_dir = out_dir.parent
    with (results_dir / "yaw_perturb_sweep.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    baseline_idx = min(range(len(overlays)), key=lambda i: abs(overlays[i][0]))
    baseline = overlays[baseline_idx][1]
    cv2.imwrite(str(out_dir / f"topic_a_overlay_{frame_id}.png"), baseline)
    worst_idx = max(range(len(overlays)), key=lambda i: abs(overlays[i][0]))
    if worst_idx == baseline_idx and len(overlays) > 1:
        worst_idx = len(overlays) - 1
    yaw_fail, fail_img = overlays[worst_idx]
    cv2.imwrite(str(out_dir / f"fail_01_yaw_{yaw_fail:g}deg_{frame_id}.png"), fail_img)

    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.plot([r["yaw_deg"] for r in rows], [r["inside_image_pct_of_finite"] for r in rows],
            "o-", label="inside image / finite points")
    ax.plot([r["yaw_deg"] for r in rows], [r["gt_box_pct_of_projected"] for r in rows],
            "s-", label="inside labeled 2D boxes / projected")
    ax.set(xlabel="Injected LiDAR yaw error (degrees)", ylabel="Points (%)",
           title=f"Calibration yaw sweep — {frame_id}")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "yaw_perturb_sweep.png", dpi=160)
    plt.close(fig)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", default="data/synthetic")
    parser.add_argument("--frame", default="000000")
    parser.add_argument("--yaw-degs", nargs="+", type=float, default=[0, 0.5, 1, 2, 3])
    parser.add_argument("--out-dir", type=Path, default=Path("results/figures"))
    args = parser.parse_args()
    rows = run(args.data_root, args.frame, args.yaw_degs, args.out_dir)
    print("yaw_deg  inside_image_points  in_gt_boxes  fov_pct  gt_box_pct")
    for row in rows:
        print(f"{row['yaw_deg']:>7.2f} {row['inside_image_points']:>19} "
              f"{row['points_in_any_gt_2d_box']:>12} "
              f"{row['inside_image_pct_of_finite']:>8.3f} "
              f"{row['gt_box_pct_of_projected']:>11.4f}")
    print(f"Saved CSV: {args.out_dir.parent / 'yaw_perturb_sweep.csv'}")
    print(f"Saved figures: {args.out_dir}")


if __name__ == "__main__":
    main()
