"""Direct USD-projection occupancy map pipeline (Path 2 fallback).

Extracts obstacles from USD geometry, applies a robot buffer, and exports
a ROS-compatible map.png + map.yaml pair.  Use when the scene lacks PhysX
colliders or you need a deterministic offline projection.
"""

import os

import numpy as np
import yaml
from PIL import Image
from scipy.ndimage import binary_dilation


def extract_obstacles_from_usd(
    usd_path: str,
    resolution: float = 0.1,
    facility_width: float = 220.0,
    facility_depth: float = 180.0,
    robot_height_min: float = 0.05,
    robot_height_max: float = 2.0,
    skip_prefixes: tuple = ("Floor", "FL", "AR", "HR", "FR", "AMR", "Exit", "Hum", "Divider", "Stair"),
) -> np.ndarray:
    """Rasterize USD prims into a 2D occupancy grid.

    Args:
        usd_path: Path to the USD scene file.
        resolution: Meters per pixel.
        facility_width: Width of the facility in meters (X extent).
        facility_depth: Depth of the facility in meters (Y extent).
        robot_height_min: Ignore prims with max-Z below this (floor markings).
        robot_height_max: Ignore prims with min-Z above this (overhead geometry).
        skip_prefixes: Prim name prefixes to skip (navigable/non-obstacle geometry).

    Returns:
        uint8 grid: 1=free, 2=occupied.
    """
    from pxr import Usd, UsdGeom

    stage = Usd.Stage.Open(usd_path)
    mpu = UsdGeom.GetStageMetersPerUnit(stage)
    bbox_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), [UsdGeom.Tokens.default_])

    grid_w = int(facility_width / resolution)
    grid_h = int(facility_depth / resolution)
    grid = np.ones((grid_h, grid_w), dtype=np.uint8)  # 1=free

    for prim in stage.TraverseAll():
        if not prim.IsA(UsdGeom.Gprim):
            continue
        name = prim.GetName()
        if any(name.startswith(p) for p in skip_prefixes):
            continue

        bbox = bbox_cache.ComputeWorldBound(prim)
        rng = bbox.ComputeAlignedRange()
        lo, hi = rng.GetMin(), rng.GetMax()

        if hi[2] * mpu < robot_height_min or lo[2] * mpu > robot_height_max:
            continue

        x_min = max(0, int(lo[0] * mpu / resolution))
        x_max = min(grid_w, int(hi[0] * mpu / resolution) + 1)
        y_min = max(0, int(lo[1] * mpu / resolution))
        y_max = min(grid_h, int(hi[1] * mpu / resolution) + 1)

        r_min = grid_h - y_max  # flip Y for image coords
        r_max = grid_h - y_min
        grid[r_min:r_max, x_min:x_max] = 2  # occupied

    return grid


def apply_robot_buffer(grid: np.ndarray, robot_radius: float = 0.5, resolution: float = 0.1) -> np.ndarray:
    """Dilate occupied cells by robot_radius to create a navigation buffer.

    Args:
        grid: Occupancy grid with 1=free, 2=occupied.
        robot_radius: Robot inscribed radius in meters.
        resolution: Meters per pixel.

    Returns:
        Boolean mask of dilated occupied cells.
    """
    buffer_px = int(robot_radius / resolution)
    kernel_size = 2 * buffer_px + 1
    kernel = np.zeros((kernel_size, kernel_size), dtype=bool)
    for r in range(kernel_size):
        for c in range(kernel_size):
            if (r - buffer_px) ** 2 + (c - buffer_px) ** 2 <= buffer_px**2:
                kernel[r, c] = True
    return binary_dilation((grid == 2), structure=kernel)


def export_ros_map(grid: np.ndarray, output_dir: str, resolution: float = 0.1) -> None:
    """Export a ROS-compatible map.png + map.yaml pair.

    Args:
        grid: Occupancy grid with 1=free, 2=occupied.
        output_dir: Directory to write map.png and map.yaml.
        resolution: Meters per pixel.
    """
    os.makedirs(output_dir, exist_ok=True)

    img_data = np.full_like(grid, 205)  # grey=unknown
    img_data[grid == 1] = 254  # white=free
    img_data[grid == 2] = 0  # black=occupied
    Image.fromarray(img_data, "L").save(os.path.join(output_dir, "map.png"))

    yaml_data = {
        "image": "map.png",
        "resolution": resolution,
        "origin": [0.0, 0.0, 0.0],
        "negate": 0,
        "occupied_thresh": 0.65,
        "free_thresh": 0.196,
    }
    with open(os.path.join(output_dir, "map.yaml"), "w") as f:
        yaml.dump(yaml_data, f, default_flow_style=False)
