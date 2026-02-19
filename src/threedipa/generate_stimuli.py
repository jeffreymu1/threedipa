#!/usr/bin/env python3
from __future__ import annotations

import os
import math
from pathlib import Path
import numpy as np
from PIL import Image
import pandas as pd

# --- WINDOW SIZE ---
FINAL_W_PX, FINAL_H_PX = 1800, 1200

# --- MONITOR CALIBRATION ---
# Physical width of each haploscope monitor in cm and its pixel width
MONITOR_PX_W = 1920
MONITOR_CM_W = 34.0
PX_PER_M = (MONITOR_PX_W / MONITOR_CM_W) * 100.0  # pixels per meter

# --- VIEWING GEOMETRY (meters) ---
D = 0.50    # viewing distance from eyes to screen plane
IOD = 0.063 # interocular distance (left eye at -IOD/2, right eye at +IOD/2)

# --- CYLINDER PARAMETERS ---
HALF_HEIGHTS = [0.025, 0.050]  # half-height of cylinder in meters
CYL_WIDTH_M = 0.20             # width of cylinder along x-axis (meters)

DEPTH_FACTORS = [0.70, 0.85, 1.00, 1.15, 1.30]

# --- REPEATS ---
N_REPEATS = 20

# --- DOT FIELD PARAMETERS ---
BASE_W, BASE_H = 1400, 1000
BASE_RADIUS = 8.0
BASE_DOTS = 350
SCALE_FACTOR = FINAL_W_PX / BASE_W
DOT_RADIUS_PX = BASE_RADIUS * SCALE_FACTOR
N_DOTS = int(BASE_DOTS * (SCALE_FACTOR ** 2))

# --- OUTPUT ---
OUT_DIR = Path("johnston_haploscope_200renderings")


def draw_solid_core_pip(canvas: np.ndarray, x_px: float, y_px: float, radius: float) -> None:
    """Renders a dot with a solid white core and anti-aliased edges."""
    x0 = int(math.floor(x_px - radius - 1))
    y0 = int(math.floor(y_px - radius - 1))
    x1 = int(math.ceil(x_px + radius + 1))
    y1 = int(math.ceil(y_px + radius + 1))

    for iy in range(y0, y1 + 1):
        for ix in range(x0, x1 + 1):
            if 0 <= ix < FINAL_W_PX and 0 <= iy < FINAL_H_PX:
                dist = math.sqrt((ix - x_px) ** 2 + (iy - y_px) ** 2)
                if dist < radius:
                    if dist < radius * 0.8:
                        brightness = 1.0
                    else:
                        edge_t = (dist - radius * 0.8) / (radius * 0.2)
                        brightness = 0.5 * (1 + math.cos(math.pi * edge_t))
                    canvas[iy, ix] = max(canvas[iy, ix], brightness)


def world_to_screen(x_m: float, y_m: float, Z_m: float) -> tuple[float, float, float]:
    """
    Professor's corrected haploscope projection (with mirror-angle correction).

        e     = IOD/2
        denom = D*(D+Z) - x*e

        U_R = ( Z*e + x) / denom
        U_L = (-Z*e + x) / denom
        V   = (D/(D+Z)) * y
    """
    e = IOD / 2
    denom = D * (D + Z_m) - x_m * e  # corrected denominator

    U_R_m = ( Z_m * e + x_m) / denom
    U_L_m = (-Z_m * e + x_m) / denom
    V_m   = (D / (D + Z_m)) * y_m

    cx_R = U_R_m * PX_PER_M + FINAL_W_PX / 2
    cx_L = U_L_m * PX_PER_M + FINAL_W_PX / 2
    cy   = V_m   * PX_PER_M + FINAL_H_PX / 2

    return cx_L, cx_R, cy


def generate_stimulus(a: float, df: float, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate left and right eye images for one cylinder condition.

    a  = half-height (meters)
    df = depth factor; b = a*df depth radius
    """
    rng = np.random.default_rng(seed)
    b = a * df

    L_img = np.zeros((FINAL_H_PX, FINAL_W_PX), dtype=np.float32)
    R_img = np.zeros((FINAL_H_PX, FINAL_W_PX), dtype=np.float32)

    max_x_m = (FINAL_W_PX / PX_PER_M) / 2
    max_y_m = (FINAL_H_PX / PX_PER_M) / 2

    for _ in range(N_DOTS):
        x_m = rng.uniform(-max_x_m, max_x_m)
        y_m = rng.uniform(-max_y_m, max_y_m)

        if abs(y_m) < a and abs(x_m) < (CYL_WIDTH_M / 2):
            Z_m = b * math.sqrt(max(0.0, 1.0 - (y_m / a) ** 2))
        else:
            Z_m = 0.0

        cx_L, cx_R, cy = world_to_screen(x_m, y_m, Z_m)

        draw_solid_core_pip(L_img, cx_L, cy, DOT_RADIUS_PX)
        draw_solid_core_pip(R_img, cx_R, cy, DOT_RADIUS_PX)

    return (L_img * 255).astype(np.uint8), (R_img * 255).astype(np.uint8)


def generate_pool(
    out_dir: str | Path = OUT_DIR,
    half_heights: list[float] = HALF_HEIGHTS,
    depth_factors: list[float] = DEPTH_FACTORS,
    n_repeats: int = N_REPEATS,
    overwrite: bool = False,
) -> Path:
    """
    Generate 200 stereo pairs (400 PNGs) + a manifest.csv.

    manifest.csv columns:
      stimulus_id, halfHeight_m, depthFactor, rep, seed,
      left_file, right_file
    where left_file/right_file are RELATIVE to out_dir.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = out_dir / "manifest.csv"
    if manifest_path.exists() and not overwrite:
        return manifest_path

    rows = []
    total = len(half_heights) * len(depth_factors) * n_repeats
    count = 0

    for a_v in half_heights:
        for df_v in depth_factors:
            for rep in range(n_repeats):
                seed = abs(hash((a_v, df_v, rep))) % (2**32)

                l_img, r_img = generate_stimulus(a_v, df_v, seed=seed)

                df_label = f"{df_v:.2f}".replace(".", "p")
                stimulus_id = f"Johnston_a{int(a_v*1000)}_df{df_label}_rep{rep:02d}"

                left_file  = f"{stimulus_id}_L.png"
                right_file = f"{stimulus_id}_R.png"

                Image.fromarray(l_img).save(out_dir / left_file)
                Image.fromarray(r_img).save(out_dir / right_file)

                rows.append({
                    "stimulus_id": stimulus_id,
                    "halfHeight_m": float(a_v),
                    "depthFactor": float(df_v),
                    "rep": int(rep),
                    "seed": int(seed),
                    "left_file": left_file,
                    "right_file": right_file,
                })

                count += 1
                print(
                    f"[{count:>3}/{total}] {stimulus_id} | "
                    f"a={a_v*100:.1f}cm  b={a_v*df_v*100:.2f}cm  df={df_v}  rep={rep:02d}  seed={seed}"
                )

    pd.DataFrame(rows).to_csv(manifest_path, index=False)
    return manifest_path


def ensure_pool(out_dir: str | Path = OUT_DIR) -> Path:
    """Create pool + CSV if missing; otherwise no-op."""
    return generate_pool(out_dir=out_dir, overwrite=False)


if __name__ == "__main__":
    ensure_pool(OUT_DIR)