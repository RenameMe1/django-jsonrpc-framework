from jsonrpc_framework.controller._base import BaseController
from jsonrpc_framework.controller.openrpc.collectors._method_collector import (
    MethodsCollector,
)
from jsonrpc_framework.openrpc.builder.builder import OpenRpcBuilder
<<<<<<< HEAD
from jsonrpc_framework.openrpc.document.info import OpenRpcContact, OpenRpcLicense

from jsonrpc_framework.controller.openrpc.collectors._method_collector import (
    MethodsCollector,
=======
from jsonrpc_framework.openrpc.document.info import (
    OpenRpcContact,
    OpenRpcLicense,
>>>>>>> 041d11d (Ruff format)
)

type ControllerType = type[BaseController] | BaseController


class OpenRpcCollector:
    controllers: tuple[type[BaseController] | BaseController, ...]
    builder: OpenRpcBuilder
    is_collected: bool

    method_collector: MethodsCollector

    def __init__(
        self,
        *controllers: ControllerType,
        title: str = "Django-jsonrpc API",
        version: str = "1.0.0",
        description: str | None = None,
        terms_of_service: str | None = None,
        contact: OpenRpcContact | None = None,
        license: OpenRpcLicense | None = None,
    ):
        self.controllers = controllers

        self.method_collector = MethodsCollector()
        self.builder = OpenRpcBuilder(
            title=title,
            version=version,
            description=description,
            terms_of_service=terms_of_service,
            contact=contact,
            license=license,
        )
        self.is_collected = False

    def collect(self) -> None:
        for controller in self.controllers:
            if isinstance(controller, type):
                controller = controller()

            self.method_collector.collect(controller)

        for method in self.method_collector.methods:
            self.builder.add_method(method)

        self.builder.add_components(self.method_collector.components)
        self.is_collected = True

    def build_document(self) -> str:

        return self.builder.build_json()
