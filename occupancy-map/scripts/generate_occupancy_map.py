# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unified occupancy-map generation with automatic fallback.

Attempts the PhysX-collider-based omap extension (Path 1) first.  When that
fails — missing colliders, extension not available, or empty map — falls back
to the direct USD-projection pipeline (Path 2).

Usage (standalone):
    python generate_occupancy_map.py <scene.usd> --output_dir ./maps

Usage (inside Isaac Sim runtime):
    from generate_occupancy_map import generate_occupancy_map
    grid = generate_occupancy_map(usd_path, output_dir="./maps")
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


def _try_collider_omap(
    origin: tuple[float, float, float],
    lower_bound: tuple[float, float, float],
    upper_bound: tuple[float, float, float],
    cell_size: float,
    z_min: float,
    z_max: float,
) -> Optional[np.ndarray]:
    """Attempt PhysX-collider-based occupancy map generation (Path 1).

    Returns the occupancy buffer as a 2D numpy array, or None if the
    extension is unavailable or the result is empty.
    """
    try:
        import omni.physx
        import omni.usd
        from isaacsim.asset.gen.omap.bindings import _omap
    except (ImportError, ModuleNotFoundError):
        logger.info("omap extension not available — skipping collider path")
        return None

    try:
        physx = omni.physx.acquire_physx_interface()
        stage_id = omni.usd.get_context().get_stage_id()

        generator = _omap.Generator(physx, stage_id)
        generator.update_settings(
            cell_size=cell_size,
            z_min=z_min,
            z_max=z_max,
            occupancy_threshold=0.5,
        )

        lo_offset = (
            lower_bound[0] - origin[0],
            lower_bound[1] - origin[1],
            lower_bound[2] - origin[2],
        )
        hi_offset = (
            upper_bound[0] - origin[0],
            upper_bound[1] - origin[1],
            upper_bound[2] - origin[2],
        )
        generator.set_transform(origin=origin, lo_offset=lo_offset, hi_offset=hi_offset)
        generator.generate2d()
        buf = generator.get_buffer()
    except Exception as exc:
        logger.warning("Collider-based omap failed: %s", exc)
        return None

    if buf is None:
        return None

    arr = np.array(buf, dtype=np.float32)
    dims = generator.get_dimensions()
    if dims[0] == 0 or dims[1] == 0:
        logger.warning("Collider omap returned empty dimensions")
        return None

    arr = arr.reshape(dims[1], dims[0])

    occupied_count = np.count_nonzero(arr == 1.0)
    if occupied_count == 0:
        logger.warning("Collider omap found zero occupied cells — scene likely lacks colliders")
        return None

    grid = np.ones_like(arr, dtype=np.uint8)  # 1=free
    grid[arr == 1.0] = 2  # occupied
    return grid


def generate_occupancy_map(
    usd_path: str,
    output_dir: str = "./maps",
    resolution: float = 0.1,
    facility_width: float = 220.0,
    facility_depth: float = 180.0,
    robot_height_min: float = 0.05,
    robot_height_max: float = 2.0,
    robot_radius: float = 0.5,
    origin: tuple[float, float, float] = (0.0, 0.0, 0.0),
    skip_prefixes: tuple = ("Floor", "FL", "AR", "HR", "FR", "AMR", "Exit", "Hum", "Divider", "Stair"),
) -> np.ndarray:
    """Generate an occupancy map, trying colliders first then USD projection.

    Args:
        usd_path: Path to the USD scene file.
        output_dir: Directory for output map.png and map.yaml.
        resolution: Meters per pixel (cell size).
        facility_width: Width of the mapped area in meters (X extent).
        facility_depth: Depth of the mapped area in meters (Y extent).
        robot_height_min: Ignore geometry below this height.
        robot_height_max: Ignore geometry above this height.
        robot_radius: Robot inscribed radius for buffer dilation.
        origin: Start location for collider-based flood fill.
        skip_prefixes: Prim name prefixes to skip in USD projection.

    Returns:
        uint8 grid: 1=free, 2=occupied (with robot buffer applied).
    """
    lower_bound = (
        origin[0] - facility_width / 2,
        origin[1] - facility_depth / 2,
        robot_height_min,
    )
    upper_bound = (
        origin[0] + facility_width / 2,
        origin[1] + facility_depth / 2,
        robot_height_max,
    )

    grid = _try_collider_omap(
        origin=origin,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
        cell_size=resolution,
        z_min=robot_height_min,
        z_max=robot_height_max,
    )

    if grid is not None:
        logger.info("Using collider-based occupancy map (Path 1)")
    else:
        logger.info("Falling back to USD projection pipeline (Path 2)")
        from usd_projection_pipeline import (
            apply_robot_buffer,
            export_ros_map,
            extract_obstacles_from_usd,
        )

        grid = extract_obstacles_from_usd(
            usd_path,
            resolution=resolution,
            facility_width=facility_width,
            facility_depth=facility_depth,
            robot_height_min=robot_height_min,
            robot_height_max=robot_height_max,
            skip_prefixes=skip_prefixes,
        )
        buffered = apply_robot_buffer(grid, robot_radius=robot_radius, resolution=resolution)
        grid[buffered & (grid != 2)] = 2

    from usd_projection_pipeline import export_ros_map

    export_ros_map(grid, output_dir, resolution=resolution)
    logger.info("Occupancy map exported to %s", output_dir)
    return grid


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate occupancy map with collider→USD-projection fallback.")
    parser.add_argument("usd_path", help="Path to the USD scene file")
    parser.add_argument("--output_dir", default="./maps", help="Output directory")
    parser.add_argument("--resolution", type=float, default=0.1, help="Meters per pixel")
    parser.add_argument("--facility_width", type=float, default=220.0, help="Facility X extent (m)")
    parser.add_argument("--facility_depth", type=float, default=180.0, help="Facility Y extent (m)")
    parser.add_argument("--robot_height_min", type=float, default=0.05, help="Min obstacle height (m)")
    parser.add_argument("--robot_height_max", type=float, default=2.0, help="Max obstacle height (m)")
    parser.add_argument("--robot_radius", type=float, default=0.5, help="Robot radius for buffer (m)")
    parser.add_argument("--origin", type=float, nargs=3, default=[0.0, 0.0, 0.0], help="Origin x y z")

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    generate_occupancy_map(
        usd_path=args.usd_path,
        output_dir=args.output_dir,
        resolution=args.resolution,
        facility_width=args.facility_width,
        facility_depth=args.facility_depth,
        robot_height_min=args.robot_height_min,
        robot_height_max=args.robot_height_max,
        robot_radius=args.robot_radius,
        origin=tuple(args.origin),
    )


if __name__ == "__main__":
    main()
