from collections import defaultdict
from collections.abc import Callable
from typing import Any

from jsonrpc_framework.controller._base import BaseController


class RouteController(BaseController):
    """The conroller that collects BaseControllers to merge
    their methods into a single controller.

    Args:
        path: The path to use in urlconfig.
        controllers: The list of BaseControllers to merge.
    """

    controllers: list[type[BaseController] | BaseController] = []

    def __init__(
        self,
        path: str,
        controllers: list[type[BaseController] | BaseController],
    ):
        super().__init__()
        self.path = path
        self.controllers = controllers

        merged_registry: dict[str, Callable[..., Any]] = {}
        key_sources: dict[str, list[str]] = defaultdict(list)

        for raw_controller in controllers:
            controller = (
                raw_controller()
                if isinstance(raw_controller, type)
                else raw_controller
            )

            if not isinstance(controller, BaseController):
                raise TypeError(
                    "Each controller must be a BaseController instance or subclass"
                )

            controller_name = controller.__class__.__name__
            for method_name, callback in controller.registry.items():
                key_sources[method_name].append(controller_name)
                if method_name in merged_registry:
                    continue
                merged_registry[method_name] = callback

        conflicts = {
            method_name: names
            for method_name, names in key_sources.items()
            if len(names) > 1
        }
        if conflicts:
            details = "; ".join(
                f"{method!r} -> {sources}"
                for method, sources in sorted(conflicts.items())
            )
            raise ValueError(f"Duplicate JSON-RPC methods detected: {details}")

        self.registry = merged_registry

    def as_view(self, **initkwargs: Any) -> Any:  # type: ignore[override]
        return BaseController.as_view.__func__(  # type: ignore[attr-defined]
            self.__class__,
            path=self.path,
            controllers=self.controllers,
            **initkwargs,
        )
