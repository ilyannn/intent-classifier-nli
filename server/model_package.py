class ModelPackage:
    """Several models that can be requested dynamically."""

    def __init__(self):
        self.models = []

    @property
    def ready(self):
        return self.models and all(model.is_ready() for model in self.models)

    def add(self, model):
        self.models.append(model)

    def info(self) -> list:
        return [
            {"key": str(ix), "name": model.model_name, "path": model.model_path}
            for ix, model in enumerate(self.models)
        ]

    def model_index(self, key=None):
        """Find a model by a key which could be an index, name or path.

        The returned index is guaranteed to exist in the model list.
        If the model is not found, returns None.
        """
        if not self.models:
            return None

        if key is None:
            return 0

        try:
            ix = int(key)
            return ix % len(self.models)
        except ValueError:
            pass

        try:
            return next(
                ix
                for ix, model in enumerate(self.models)
                if key in (model.model_name, model.model_path)
            )
        except StopIteration:
            return None

    def classify(self, data, model_key: str):
        """Forward the classification task to the appropriate model.

        This checks that the requested model exists and is ready.
        """
        ix = self.model_index(model_key)
        if ix is None:
            raise ValueError(f"No model found for {model_key}")

        model = self.models[ix]
        if not model.is_ready():
            raise ValueError(f"The specified model {model_key} was not ready")

        return self.models[ix].classify(data)
