from __future__ import annotations
from abc import abstractmethod
from os import path, walk
import sys
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec
from typing import List

class Asset:
    def __init_subclass__(cls):
        super().__init_subclass__()
        if cls == Asset: return
        if cls.__name__ == cls.base_asset_class_name(): return
        instance = cls()
        AssetHolder.current_loader.register(instance)
        print(f"Asset {cls.__name__} registered to {AssetHolder.current_loader.__class__.__name__}.")

    @classmethod
    def base_asset_class_name(cls): return 'Asset'


class AssetHolder[T: Asset]:
    current_loader: AssetHolder[T] = None
    registered_assets: List[T]
    def __init__(self):
        self.registered_assets: List[T] = []
        self.load_asset_modules(self.asset_folder_name())

    @abstractmethod
    def asset_folder_name(self) -> str: pass

    def register(self, obj: T) -> None:
        self.registered_assets.append(obj)

    def load_asset_modules(self, directory_name):
        if AssetHolder.current_loader is not None:
            raise Exception("Cannot load assets from multiple loaders at the same time.")

        # Start from the root directory and search the whole filesystem
        for root, dirs, files in walk("/"):
            if "assets/" + directory_name in root:
                for file in files:
                    if file.endswith(".py"):
                        module_path = Path(path.join(root, file))
                        module_name = module_path.stem  # Get filename without .py
                        module_path = str(module_path.resolve())

                        spec = spec_from_file_location(module_name, module_path)
                        if spec and spec.loader:
                            module = module_from_spec(spec)
                            sys.modules[module_name] = module
                            AssetHolder.current_loader = self
                            try:
                                spec.loader.exec_module(module)
                            finally:
                                AssetHolder.current_loader = None
