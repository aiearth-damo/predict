import ray
from rasterio.merge import merge
from typing import Any, Dict, List, Optional, Union, Callable, Tuple


@ray.remote
def merge_tiffs(tiff_files: List[str], merged_tiff_file):
    merge(tiff_files, dst_path=merged_tiff_file)
