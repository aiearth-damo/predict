import os
from pathlib import Path
from zipfile import ZipFile
from typing import Optional, Union, List
from ray._private.runtime_env.packaging import _zip_directory, unzip_package


class Package:
    @staticmethod
    def zip_directory(directory, output_path, excludes=[], **kwargs):
        include_parent_dir = kwargs.pop("include_parent_dir", False)
        _zip_directory(directory, excludes, output_path, include_parent_dir)

    @staticmethod
    def zip_files(files: Union[str, List[str]], output_path, **kwargs):
        if isinstance(files, str):
            files = [files]

        include_parent_dir = kwargs.pop("include_parent_dir", False)

        pkg_file = Path(output_path).absolute()
        parent_dir = os.path.splitext(Path(output_path).name)[0]
        with ZipFile(pkg_file, "w") as zip_handler:
            for file in files:
                path = Path(file).absolute()
                to_path = Path(file).name
                if include_parent_dir:
                    to_path = os.path.join(parent_dir, to_path)
                zip_handler.write(path, to_path)

    @staticmethod
    def unzip(package_path, target_dir, **kwargs):
        remove_top_level_directory = kwargs.pop("remove_top_level_directory", False)
        unlink_zip = kwargs.pop("unlink_zip", False)

        unzip_package(package_path, target_dir, remove_top_level_directory, unlink_zip)

    @staticmethod
    def unlink(package_path):
        Path(package_path).unlink()
