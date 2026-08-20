#!/usr/bin/env python3
"""Evaluate JavaScript from a UTF-8 file in an existing CDP browser page."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expression-file", required=True, type=Path)
    parser.add_argument("--endpoint", default="http://127.0.0.1:9222")
    parser.add_argument("--url-contains", default="")
    parser.add_argument("--timeout-ms", type=int, default=30_000)
    args = parser.parse_args()

    if args.timeout_ms <= 0:
        parser.error("--timeout-ms must be positive")

    try:
        expression = args.expression_file.read_text(encoding="utf-8")
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            browser = playwright.chromium.connect_over_cdp(
                args.endpoint,
                timeout=args.timeout_ms,
            )
            pages = [page for context in browser.contexts for page in context.pages]
            matches = [page for page in pages if args.url_contains in page.url]
            if not matches:
                target = args.url_contains or "<any page>"
                raise RuntimeError(f"CDP page not found: {target} (open pages: {len(pages)})")
            result = matches[-1].evaluate(expression)
            print(json.dumps(result, ensure_ascii=False, default=str))
        return 0
    except Exception as exc:  # Playwright exposes multiple environment-specific errors.
        print(f"CDP evaluation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
