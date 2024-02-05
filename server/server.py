import argparse
import os

from flask import Blueprint, Flask, jsonify, request

from intent_classifier import load_intent_classifier
from model_package import ModelPackage

DEFAULT_MODEL_PATH = os.getenv("MODEL")
try:
    from _version import VERSION
except ImportError:
    VERSION = None


api = Blueprint("main", __name__)
models = ModelPackage()


@api.route("/ready")
def ready():
    if not models.ready:
        return "Not ready", 423
    return "OK", 200


@api.route("/info")
def info():
    return jsonify(
        {
            "models": models.info(),
            "ready": models.ready,
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
        intents = models.classify(data["text"], data.get("requested_model"))
        return (
            jsonify(
                {
                    "intents": [{"label": label} for label in intents],
                }
            ),
            200,
        )
    # except ValueError as e:
    #     return (
    #         jsonify(
    #             {
    #                 "label": "BAD_REQUEST",
    #                 "message": f"Incorrect request parameters: {e}",
    #             }
    #         ),
    #         400,
    #     )
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


def create_app(model_paths=DEFAULT_MODEL_PATH):
    """
    Function to create a Flask app by loading the models specified.

    :param model_paths: Paths to the model files.
    This parameter can be a string or a list of strings;
    each string can contain several semicolon-separated paths.
    Default is DEFAULT_MODEL_PATH.
    :return: The Flask app object.
    :raises ValueError: If model_paths is not provided or is empty.
    """
    if not model_paths:
        raise ValueError("Please provide model path as a MODEL environment variable")

    app = Flask(__name__)
    app.register_blueprint(api)

    if isinstance(model_paths, str):
        model_paths = [model_paths]

    for model_path in model_paths:
        for model_path_split in model_path.split(":"):
            models.add(load_intent_classifier(model_path_split))

    return app


def main():
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL_PATH,
        required=not DEFAULT_MODEL_PATH,
        nargs="+",
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
