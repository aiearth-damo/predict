import ray
import geopandas as gpd
from typing import Any, Dict, List, Optional, Union, Callable, Tuple


@ray.remote
def merge_shapes(shape_files: List[str], merged_shape_file, dissolve=True, by="value"):
    gpdf = [gpd.read_file(file) for file in shape_files]
    merged = gpd.pd.concat(gpdf)

    if dissolve:
        merged = merged.dissolve(by)
    merged.explode(index_parts=True).to_file(merged_shape_file)
