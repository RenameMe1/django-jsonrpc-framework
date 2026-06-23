from collections.abc import Callable
from pathlib import Path
from typing import Any, override

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseBase
from django.http.response import FileResponse
from django.views import View
from django.views.generic.base import TemplateView

from jsonrpc_framework.controller.openrpc.collectors import OpenRpcCollector


class OpenRpcJsonView(View):
    http_method_names = ["get"]
    path = "openrpc.json"
    collector: OpenRpcCollector = OpenRpcCollector()

    def __init__(self, *args: tuple[Any], **kwargs: dict[str, Any]):
        super().__init__(*args, **kwargs)

    def get(
        self, request: HttpRequest, *args: tuple[Any], **kwargs: dict[str, Any]
    ) -> HttpResponse | FileResponse:
<<<<<<< HEAD
        file_path = getattr(settings, "DJANGO_JSONRPC_DOCS", {}).get("FILE_PATH", None)
=======
        file_path = getattr(settings, "DJANGO_JSONRPC_DOCS", {}).get(
            "FILE_PATH", None
        )
>>>>>>> 041d11d (Ruff format)

        if file_path is not None and Path(file_path).exists():
            return FileResponse(
                Path(file_path).open("rb"),
                filename=Path(file_path).name,
            )

        if not self.collector.is_collected:
            self.collector.collect()

        document = self.collector.build_document()

        return HttpResponse(
            content=document,
            content_type="application/json; charset=utf-8",
        )

    @classmethod
    @override
    def as_view(
        cls,
        *,
        collector: OpenRpcCollector | None = None,
        **initkwargs: Any,
    ) -> Callable[..., HttpResponseBase]:
        return super().as_view(collector=collector, **initkwargs)


class OpenRpcDocView(TemplateView):
    template_name = "openrpc_docs.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)

        docs_cfg = getattr(settings, "DJANGO_JSONRPC_DOCS", {})

        schema_path = docs_cfg.get("SCHEMA_PATH", "/openrpc.json")
        schema_url = self.request.build_absolute_uri(schema_path)

        ctx.update(
            {
                "openrpc_schema_url": schema_url,
                "page_title": docs_cfg.get("TITLE", "OpenRPC Docs"),
                "docs_react_css_url": docs_cfg.get(
                    "DOCS_REACT_CSS_URL",
                    "https://cdn.jsdelivr.net/npm/@open-rpc/docs-react@2.1.1/dist/docs-react.css",
                ),
                "esm_react_url": docs_cfg.get(
                    "ESM_REACT_URL",
                    "https://esm.sh/react@18.3.1",
                ),
                "esm_react_dom_url": docs_cfg.get(
                    "ESM_REACT_DOM_URL",
                    "https://esm.sh/react-dom@18.3.1/client?deps=react@18.3.1",
                ),
                "esm_openrpc_docs_url": docs_cfg.get(
                    "ESM_OPENRPC_DOCS_URL",
                    "https://esm.sh/@open-rpc/docs-react@2.1.1?deps=react@18.3.1,react-dom@18.3.1",
                ),
                "esm_mui_styles_url": docs_cfg.get(
                    "ESM_MUI_STYLES_URL",
                    "https://esm.sh/@mui/material@6.3.1/styles?deps=react@18.3.1,react-dom@18.3.1",
                ),
                "esm_mui_css_baseline_url": docs_cfg.get(
                    "ESM_MUI_CSS_BASELINE_URL",
                    "https://esm.sh/@mui/material@6.3.1/CssBaseline?deps=react@18.3.1,react-dom@18.3.1",
                ),
                "openrpc_theme_mode": docs_cfg.get("THEME_MODE", "dark"),
            }
        )
        return ctx
