from __future__ import annotations

import argparse

from travelwise.app.api.server import create_app
from travelwise.src.evaluation.run_eval import run_evaluation
from travelwise.src.utils.bootstrap import build_index
from travelwise.src.utils.config import settings, validate_settings


def main() -> None:
    parser = argparse.ArgumentParser(description="TravelWise NYC prototype runner")
    parser.add_argument(
        "command",
        choices=["build-index", "eval", "api", "doctor"],
        help="Command to run",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    if args.command == "build-index":
        stats = build_index(settings)
        print("Index build complete:")
        for k, v in stats.items():
            print(f"- {k}: {v}")
        return

    if args.command == "eval":
        run_evaluation()
        return

    if args.command == "doctor":
        warnings = validate_settings(settings)
        print("TravelWise environment check:")
        print(f"- vector_index_dir: {settings.vector_index_dir}")
        print(f"- web_fallback: {settings.use_web_fallback}")
        print(f"- gemini_key_set: {bool(settings.gemini_api_key)}")
        print(f"- tavily_key_set: {bool(settings.tavily_api_key)}")
        if warnings:
            print("\nWarnings:")
            for w in warnings:
                print(f"- {w}")
        else:
            print("\nNo configuration warnings detected.")
        return

    if args.command == "api":
        app = create_app()
        app.run(host=args.host, port=args.port, debug=args.debug)
        return


if __name__ == "__main__":
    main()
