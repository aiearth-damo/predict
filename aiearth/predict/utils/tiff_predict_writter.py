import os
import ray
import rasterio
import pandas as pd

from aiearth.predict.utils import Box

from aiearth.predict.logging import root_logger as logger


@ray.remote
class TiffPredictWritter:
    def __init__(self, output_file, width, height, count, dtype, crs, transform):
        output_dir = os.path.dirname(output_file)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        with rasterio.Env(GDAL_CACHEMAX=200):
            self.writter = rasterio.open(
                output_file,
                "w",
                driver="GTiff",
                width=width,
                height=height,
                count=count,
                dtype=dtype,
                crs=crs,
                transform=transform,
                BIGTIFF="YES",
                tiled=True,
                compress="lzw",
            )

        self.count = count

    def write(self, df: pd.DataFrame, feature_column, meta_column, origin: Box = None):
        for _, row in df.iterrows():
            image = row["image"]
            box = row["box"]
            pad_bounds = row["pad_bounds"]

            if origin is not None:
                box = box.subtract_origin(origin)

            x, y, width, height = box.to_xywh()
            if image.ndim == 2:
                image = image[
                    pad_bounds.top : height - pad_bounds.bottom,
                    pad_bounds.left : width - pad_bounds.right,
                ]
            elif image.ndim == 3:
                image = image[
                    :,
                    pad_bounds.top : height - pad_bounds.bottom,
                    pad_bounds.left : width - pad_bounds.right,
                ]
            else:
                raise RuntimeError(f"image ndim {image.ndim} not support")

            x += pad_bounds.left
            y += pad_bounds.top
            width = width - pad_bounds.right - pad_bounds.left
            height = height - pad_bounds.bottom - pad_bounds.top

            with rasterio.Env(GDAL_CACHEMAX=200):
                # 5% mem cache
                if image.ndim == 2:
                    self.writter.write(
                        image, 1, window=((y, y + height), (x, x + width))
                    )
                elif image.ndim == 3:
                    self.writter.write(image, window=((y, y + height), (x, x + width)))
                else:
                    raise RuntimeError(f"image ndim {image.ndim} not support")

    def finalize(self):
        with rasterio.Env(GDAL_CACHEMAX=200):
            self.writter.close()
