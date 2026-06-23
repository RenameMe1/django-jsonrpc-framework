import inspect
import types
from collections.abc import Callable
from typing import Any, get_type_hints, is_typeddict

from jsonrpc_framework.controller._base import BaseController
from jsonrpc_framework.core.error import RpcError
from jsonrpc_framework.openrpc.document.common import (
    OpenRcpContentDescriptorObject,
    OpenRcpTypeSchema,
    OpenRpcDataSchema,
    OpenRpcErrorObject,
    OpenRpcRefSchema,
    OpenRpcTag,
    validate_type_name,
)
from jsonrpc_framework.openrpc.document.components import OpenRpcComponents
from jsonrpc_framework.openrpc.document.method._method import OpenRpcMethod


class ExampleCollector: ...


class InputCollector:
    components: OpenRpcComponents

    def __init__(self, components: OpenRpcComponents):
        self.components = components

    def collect(
        self, method: Callable[..., Any], openrpc_method: OpenRpcMethod
    ) -> None:
        sig = inspect.signature(method)
        params = sig.parameters

        for param in params.values():
            if is_typeddict(param.annotation):
                openrpc_method.params.append(
                    self._collect_content_descriptor(param)
                )
            else:
                openrpc_method.params.append(
                    OpenRcpContentDescriptorObject(
                        name=param.name,
                        schema_={
                            "type": validate_type_name(
                                param.annotation.__name__
                            ),
                        },
                        required=True
                        if param.default is param.empty
                        else False,
                        # TODO: How define deprecated params?
                    )
                )

    def _collect_content_descriptor(
        self, param: inspect.Parameter
    ) -> OpenRcpContentDescriptorObject:
        type_hints = get_type_hints(param.annotation)
        component_name = param.annotation.__name__

        schema: dict[str, Any] = {
            "type": "object",
            "required": [],
            "properties": {},
        }

        for key, value in type_hints.items():
            schema["properties"][key] = {
                "type": validate_type_name(value.__name__),
            }
            if value.__name__ == "Optional":
                schema["required"].append(key)

        if self.components.schemas is None:
            self.components.schemas = {}
        self.components.schemas[component_name] = schema

        return OpenRcpContentDescriptorObject(
            name=component_name,
            schema_=OpenRpcRefSchema(
                ref=f"#/components/schemas/{component_name}",
            ),
            required=True if param.default is param.empty else False,
            deprecated=False,
        )


class OutputCollector:
    components: OpenRpcComponents

    def __init__(self, components: OpenRpcComponents):
        self.components = components

    def collect(
        self, method: Callable[..., Any], openrpc_method: OpenRpcMethod
    ) -> None:
        return_sig = inspect.signature(method).return_annotation

        if isinstance(return_sig, types.UnionType):
            for return_type in return_sig.__args__:
                self._collect_single_output(return_type, openrpc_method)
        else:
            self._collect_single_output(return_sig, openrpc_method)

    def _collect_single_output(
        self, return_type: type, openrpc_method: OpenRpcMethod
    ) -> None:

        if issubclass(return_type, RpcError):
            self._collect_error_object(return_type, openrpc_method)
        else:
            self._collect_result(return_type, openrpc_method)

    def _collect_error_object(
        self, return_type: type, openrpc_method: OpenRpcMethod
    ) -> None:
        if openrpc_method.errors is None:
            openrpc_method.errors = []

        openrpc_method.errors.append(
            OpenRpcErrorObject(
                code=return_type().code,
                message=return_type().message,
                data=return_type().data,
            )
        )

    def _collect_result(
        self, return_type: type, openrpc_method: OpenRpcMethod
    ) -> None:
        if is_typeddict(return_type):
            self._collect_complex_context_descriptor(
                return_type, openrpc_method
            )
        else:
            openrpc_method.result = OpenRcpContentDescriptorObject(
                name=return_type.__name__,
                schema_=OpenRcpTypeSchema(
                    type=validate_type_name(return_type.__name__)
                ),
            )

    def _collect_complex_context_descriptor(
        self, return_type: type, openrpc_method: OpenRpcMethod
    ) -> None:
        schema = OpenRpcDataSchema(
            type="object",
            required=[],
            properties={},
        )

        for key, value in get_type_hints(return_type).items():
            if schema.properties is None:
                schema.properties = {}

            schema.properties[key] = {
                "type": validate_type_name(value.__name__),
            }

        if self.components.schemas is None:
            self.components.schemas = {}
        self.components.schemas[return_type.__name__] = schema

        openrpc_method.result = OpenRcpContentDescriptorObject(
            name=return_type.__name__,
            schema_=OpenRpcRefSchema(
                ref=f"#/components/schemas/{return_type.__name__}",
            ),
        )


class MethodsCollector:
    methods: list[OpenRpcMethod]
    components: OpenRpcComponents

    input_collector: InputCollector
    output_collector: OutputCollector

    def __init__(self) -> None:
        self.methods = []
        self.components = OpenRpcComponents()

        self.input_collector = InputCollector(self.components)
        self.output_collector = OutputCollector(self.components)

    def collect(self, controller: BaseController) -> None:
        for method_name, method in controller.registry.items():
            self.methods.append(self._create_method(method_name, method))

    def _create_method(
        self, method_name: str, method: Callable[..., Any]
    ) -> OpenRpcMethod:
        openrpc_method = OpenRpcMethod(  # type: ignore[call-arg]
            name=method_name,
            summary=getattr(method, "__rpc_method_summary__", None),
            description=getattr(method, "__rpc_method_description__", None),
            deprecated=getattr(method, "__rpc_method_deprecated__", False),
        )

        self._collect_tags(method, openrpc_method)

        self.input_collector.collect(method, openrpc_method)
        self.output_collector.collect(method, openrpc_method)

        return openrpc_method

    def _collect_tags(
        self, method: Callable[..., Any], openrpc_method: OpenRpcMethod
    ) -> None:
        __rpc_method_tags__ = getattr(method, "__rpc_method_tags__", [])

        if __rpc_method_tags__:
            openrpc_method.tags = [
                OpenRpcTag(name=tag) for tag in __rpc_method_tags__
            ]

    def _collect_errors(self, method: Callable[..., Any]) -> None:
        return None

    def _collect_links(self, method: Callable[..., Any]) -> None:
        return None

    def _collect_examples(self, method: Callable[..., Any]) -> None:
        return None

    def _collect_external_docs(self, method: Callable[..., Any]) -> None:
        return None
