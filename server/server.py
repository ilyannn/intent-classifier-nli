# -*- coding: utf-8 -*-

import argparse
import os

from flask import Blueprint, Flask, jsonify, request

from intent_classifier import IntentClassifier

DEFAULT_MODEL_PATH = os.getenv("MODEL")
try:
    from _version import VERSION
except ImportError:
    VERSION = None

api = Blueprint("main", __name__)
model = IntentClassifier()


@api.route("/ready")
def ready():
    if model.is_ready():
        return "OK", 200
    else:
        return "Not ready", 423


@api.route("/info")
def info():
    return jsonify(
        {
            "model": {"name": model.model_name, "path": model.model_path},
            "ready": model.is_ready(),
            "version": VERSION,
        }
    )


@api.route("/intent", methods=["POST"])
def intent():
    if not request.is_json:
        return (
            jsonify(
                {
                    "label": "BODY_MISSING",
                    "message": "Request doesn't have a body.",
                }
            ),
            400,
        )

    data = request.get_json()
    if not isinstance(data, dict) or "text" not in data:
        return (
            jsonify(
                {
                    "label": "TEXT_MISSING",
                    "message": '"text" missing from request body.',
                }
            ),
            400,
        )

    try:
        intents = model.classify(data["text"])
        return (
            jsonify(
                {
                    "intents": [{"label": label} for label in intents],
                }
            ),
            200,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "label": "INTERNAL_ERROR",
                    "message": f"Something went wrong: {e}",
                }
            ),
            500,
        )


def create_app(model_path=DEFAULT_MODEL_PATH):
    if not model_path:
        raise ValueError("Please provide model path as a MODEL environment variable")

    app = Flask(__name__)
    app.register_blueprint(api)
    model.load(model_path)
    return app


def main():
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL_PATH,
        required=not DEFAULT_MODEL_PATH,
        help="Path to model directory or file.",
    )

    arg_parser.add_argument(
        "--port",
        type=int,
        default=os.getenv("PORT") or 8080,
        help="Server port number.",
    )

    args = arg_parser.parse_args()
    app = create_app(args.model)
    app.run(port=args.port)


if __name__ == "__main__":
    main()
