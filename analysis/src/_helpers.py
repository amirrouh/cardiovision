from pathlib import Path
import sys
import os

# this_directory = os.path.abspath(os.path.dirname(__file__))
working_dir = os.path.join('..', '..')
sys.path.append(working_dir)

from config import output_dir


output_dir = Path(output_dir)
cusps = ["left", "right", "non"]


def create_folders():
    analysis_dir = output_dir / 'analysis'
    analysis_dir.mkdir(parents=True, exist_ok=True)

    islands_dir = analysis_dir / 'islands'
    islands_dir.mkdir(parents=True, exist_ok=True)

    left_cusp_islands = islands_dir / "left_cusp"
    right_cusp_islands = islands_dir / "right_cusp"
    non_cusp_islands = islands_dir / "non_cusp"
    left_cusp_islands.mkdir(parents=True, exist_ok=True)
    right_cusp_islands.mkdir(parents=True, exist_ok=True)
    non_cusp_islands.mkdir(parents=True, exist_ok=True)


calcium_on_cusps_ply = list(output_dir.rglob("*calcium_*.ply"))
calcium_on_cusps_ply = list(map(str, calcium_on_cusps_ply))

calcium_on_cusps_stl = list(output_dir.rglob("*calcium_*.stl"))
calcium_on_cusps_stl = list(map(str, calcium_on_cusps_stl))


