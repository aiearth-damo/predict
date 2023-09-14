import os
import ray
import rasterio
import fiona
from rasterio import features
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon, mapping, shape

from aiearth.predict.utils import Box


@ray.remote
class Polygonization:
    def __init__(self, chunk_size=20000):
        self.chunk_size = chunk_size

    def polygonization_to_shapes(
        self,
        tiff_path,
        window=None,
        geojson_mapping=False,
        mask_zeros=False,
        simplify_tolerance=None,
    ):
        with rasterio.open(tiff_path) as src:
            if window:
                band = src.read(window=window)
                transform = src.window_transform(window)
            else:
                band = src.read()
                transform = src.transform
            shape_crs = src.crs

            if mask_zeros:
                mask = band != 0
                shapes = features.shapes(band, mask=mask, transform=transform)
            else:
                shapes = features.shapes(band, transform=transform)

        result = [
            {
                "geometry": shape(shape),
                "properties": {"value": int(value)},
            }
            for shape, value in shapes
        ]

        if simplify_tolerance is not None:
            for i in result:
                i["geometry"] = i["geometry"].simplify(tolerance=simplify_tolerance)

        if geojson_mapping:
            for i in result:
                i["geometry"] = mapping(i["geometry"])

        return (shape_crs, result)

    def polygonization_to_shapes_look_once(
        self,
        tiff_path,
        window=None,
        geojson_mapping=False,
        mask_zeros=False,
        simplify_tolerance=None,
    ):
        with rasterio.open(tiff_path) as src:
            if window:
                band = src.read(window=window)
                transform = src.window_transform(window)
            else:
                band = src.read()
                transform = src.transform
            shape_crs = src.crs

            if mask_zeros:
                shapes = features.shapes(band, transform=transform)
            else:
                mask = band != 0
                shapes = features.shapes(band, mask=mask, transform=transform)

        if geojson_mapping:
            if simplify_tolerance:
                result = [
                    {
                        "geometry": mapping(
                            shape(shape).simplify(tolerance=simplify_tolerance)
                        ),
                        "properties": {"value": int(value)},
                    }
                    for shape, value in shapes
                ]
            else:
                result = [
                    {
                        "geometry": shape,
                        "properties": {"value": int(value)},
                    }
                    for shape, value in shapes
                ]
        else:
            if simplify_tolerance:
                result = [
                    {
                        "geometry": shape(shape).simplify(tolerance=simplify_tolerance),
                        "properties": {"value": int(value)},
                    }
                    for shape, value in shapes
                ]
            else:
                result = [
                    {
                        "geometry": shape(shape),
                        "properties": {"value": int(value)},
                    }
                    for shape, value in shapes
                ]

        return (shape_crs, result)

    def write_with_fiona(self, path, crs, fc):
        schema = {"geometry": "Polygon", "properties": dict([("value", "int")])}

        with fiona.open(
            path,
            mode="w",
            driver="ESRI Shapefile",
            schema=schema,
            crs=crs.to_string(),
            encoding="utf-8",
        ) as dst:
            dst.writerecords(fc)

    def write_with_geopandas(self, path, crs, fc):
        gdf = gpd.GeoDataFrame.from_features(fc)
        gdf.set_crs(epsg=crs.to_epsg(), inplace=True)
        gdf.to_file(gpkg_path, driver="GPKG")

    def get_tiff_extent(self, tiff_path):
        with rasterio.open(tiff_path) as dataset:
            return Box(0, 0, dataset.width, dataset.height)

    def tiff_to_gpkg_file(
        self,
        tiff_path,
        gpkg_path,
        extent: Box = None,
        simplify_tolerance=None,
        mask_zeros=False,
    ):
        output_dir = os.path.dirname(gpkg_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        if extent is None:
            extent = self.get_tiff_extent(tiff_path)
        windows, indexes = self.get_chunk_windows(extent)

        filename = os.path.splitext(gpkg_path)[0]
        for window, index in zip(windows, indexes):
            out_path = f"{filename}-{index[0]}.{index[1]}.gpkg"
            crs, fc = self.polygonization_to_shapes(
                tiff_path,
                window.to_window(),
                geojson_mapping=False,
                simplify_tolerance=simplify_tolerance,
                mask_zeros=mask_zeros,
            )

            self.write_with_geopandas(out_path, crs, fc)

    def tiff_to_shape_file(
        self,
        tiff_path,
        shape_path,
        extent=None,
        simplify_tolerance=None,
        mask_zeros=False,
    ):
        output_dir = os.path.dirname(shape_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        if extent is None:
            extent = self.get_tiff_extent(tiff_path)

        crs, fc = self.polygonization_to_shapes_look_once(
            tiff_path,
            extent.to_window(),
            geojson_mapping=True,
            simplify_tolerance=simplify_tolerance,
            mask_zeros=mask_zeros,
        )

        self.write_with_fiona(shape_path, crs, fc)
