from __future__ import annotations

from abc import abstractmethod
from typing import override
from centralized_data import Bindable, PythonAsset, PythonAssetLoader, Singleton
from flask import Blueprint, Flask
from flask_restx import Api, Namespace

class ApiServer(Bindable, Flask):
    @override
    def constructor(self) -> None:
        super(Bindable, self).constructor()
        super(Flask, self).__init__(__name__)
        self._blueprint = Blueprint('api', __name__, url_prefix='/api')
        ApiEndpoint()
        self.register_blueprint(self._blueprint)

class ApiNamespace(PythonAsset, Singleton):
    @classmethod
    def base_asset_class_name(cls): return 'ApiNamespace'

    @override
    def constructor(self) -> None:
        self.namespace = Namespace(self.get_name(), description=self.get_description(), path=self.get_path())
        ApiEndpoint().api.add_namespace(self.namespace)

    @abstractmethod
    def get_name(self) -> str: ...

    @abstractmethod
    def get_path(self) -> str: ...

    @abstractmethod
    def get_description(self) -> str: ...

class ApiEndpoint(PythonAssetLoader[ApiNamespace]):
    @ApiServer.bind
    def api_server(self) -> ApiServer: ...

    @override
    def asset_folder_name(self):
        return 'api_namespaces'

    @override
    def constructor(self) -> None:
        self.api = Api(self.api_server._blueprint, version="1.0", title="Krile API", description="Backend API for Krile.")
        super().constructor()