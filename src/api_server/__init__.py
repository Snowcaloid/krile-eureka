from __future__ import annotations

from abc import abstractmethod
from os import getenv
from threading import Thread
from typing import override
from centralized_data import Bindable, PythonAsset, PythonAssetLoader, Singleton
from flask import Blueprint, Flask
from flask_restx import Api, Namespace
from waitress import serve

class ApiServer(Bindable, Flask):
    @override
    def constructor(self) -> None:
        super(Bindable, self).constructor()
        super(Flask, self).__init__(__name__)
        self._blueprint = Blueprint('api', __name__, url_prefix='/api')
        self.config["JWT_SECRET_KEY"] = getenv("JWT_SECRET_KEY")
        self.config["PROPAGATE_EXCEPTIONS"] = True
        ApiEndpoint()
        self.register_blueprint(self._blueprint)
        self.thread = Thread(target=serve, args=[self], kwargs={"port": 6066})

    def start(self) -> None:
        self.thread.start()

class ApiNamespace(PythonAsset, Singleton):
    @classmethod
    def base_asset_class_name(cls): return 'ApiNamespace'

    @override
    def constructor(self) -> None:
        auth = None
        if self.use_jwt():
            auth = {
                "jsonWebToken": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "Authorization"
                }
            }
        self.namespace = Namespace(
            self.get_name(),
            description=self.get_description(),
            path='/' + self.get_path(),
            authorizations=auth)
        ApiEndpoint().api.add_namespace(self.namespace)

    @abstractmethod
    def get_name(self) -> str: ...

    @abstractmethod
    def get_path(self) -> str: ...

    @abstractmethod
    def get_description(self) -> str: ...

    def use_jwt(self) -> bool: return False

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