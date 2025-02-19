from __future__ import annotations
from abc import abstractmethod
from os import path, walk
from yaml import safe_load
import sys
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec
from typing import List, Type, override

class LoadedAsset: pass

class AssetLoader[T: LoadedAsset]:
    _log: str = ''
    loaded_assets: List[T]
    def __init__(self):
        self.loaded_assets: List[T] = []
        self.load_asset_modules()

    @abstractmethod
    def asset_folder_name(self) -> str: pass
    @abstractmethod
    def asset_file_extension(self) -> str: pass
    @abstractmethod
    def load_asset(self, filename: str) -> None: pass

    def log(self, message: str) -> None:
        AssetLoader._log += message + '\n' #test
        print(message)

    def add_asset(self, obj: T, name: str) -> None:
        self.loaded_assets.append(obj)
        self.log(f"Asset {name} loaded by {self.__class__.__name__}.")

    def load_asset_modules(self) -> None:
        directory = self.asset_folder_name()

        # Start from the root directory and search the whole filesystem
        for root, dirs, files in walk("/"):
            if "assets/" + directory in root:
                for file in files:
                    if file.endswith(self.asset_file_extension()):
                        self.load_asset(path.join(root, file))

class PythonAsset(LoadedAsset):
    def __init_subclass__(cls):
        super().__init_subclass__()
        if cls == LoadedAsset: return
        if cls.__name__ == cls.base_asset_class_name(): return
        instance = cls()
        PythonAssetLoader.current_loader.add_asset(instance, cls.__name__)

    @classmethod
    def base_asset_class_name(cls): return 'PythonAsset'


class PythonAssetLoader[T: PythonAsset](AssetLoader[T]):
    current_loader: AssetLoader[T] = None

    @override
    def asset_file_extension(self) -> str:
        return '.py'

    @override
    def load_asset(self, filename):
        if PythonAssetLoader.current_loader is not None:
            raise Exception("Cannot load assets from multiple loaders at the same time.")

        module_path = Path(filename)
        module_name = module_path.stem  # Get filename without .py
        module_path = str(module_path.resolve())

        spec = spec_from_file_location(module_name, module_path)
        if spec and spec.loader:
            module = module_from_spec(spec)
            sys.modules[module_name] = module
            PythonAssetLoader.current_loader = self
            try:
                spec.loader.exec_module(module)
            finally:
                PythonAssetLoader.current_loader = None

class YamlAsset(LoadedAsset):
    source: object
    def __init__(self, filename: str):
        self.source = safe_load(open(filename).read())

    @abstractmethod
    def asset_name(self) -> str: pass


class YamlAssetLoader[T: YamlAsset](AssetLoader[T]):

    def asset_class(self) -> Type[T]: return YamlAsset

    @override
    def asset_file_extension(self) -> str: return '.yaml'

    @override
    def load_asset(self, filename):
        yaml_asset = self.asset_class()(filename)
        self.add_asset(yaml_asset, f'{self.asset_class().__name__}[{yaml_asset.asset_name()}]')