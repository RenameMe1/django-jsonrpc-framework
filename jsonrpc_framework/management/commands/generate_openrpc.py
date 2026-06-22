from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.module_loading import import_string
from jsonrpc_framework.controller.openrpc.collectors import OpenRpcCollector
from typing import Any
from argparse import ArgumentParser


class Command(BaseCommand):
    help = "Generate OpenRPC JSON from a collector object"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--collector",
            required=True,
            help=(
                'Dotted path to collector instance, e.g. "myproject.openrpc.collector"'
            ),
        )
        parser.add_argument(
            "--output",
            default=None,
            help='Output file path (default: DJANGO_JSONRPC_DOCS["FILE_PATH"] or ./openrpc.json)',
        )

    def handle(self, *args: tuple[Any], **options: dict[str, Any]) -> None:
        collector_path = str(options["collector"])
        try:
            collector = import_string(collector_path)
        except Exception as exc:
            raise CommandError(
                f'Cannot import collector "{collector_path}": {exc}'
            ) from exc
        if not isinstance(collector, OpenRpcCollector):
            raise CommandError(
                f'"{collector_path}" must be an OpenRpcCollector instance'
            )
        output = str(
            options["output"]
            or getattr(settings, "DJANGO_JSONRPC_DOCS", {}).get("FILE_PATH")
            or "openrpc.json"
        )
        output_path = Path(output)
        try:
            document = collector.build_document()
        except Exception as exc:
            raise CommandError(f"Failed to build OpenRPC document: {exc}") from exc
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(document, encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"OpenRPC saved to: {output_path}"))
