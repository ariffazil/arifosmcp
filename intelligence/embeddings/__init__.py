import logging
import os

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)
_model = None
_DEFAULT_MODEL_NAME = "BAAI/bge-m3"
_BAKED_MODEL_PATHS = (
    "/usr/src/app/models/bge/bge-arifOS",
    "/app/models/bge/bge-arifOS",
)


def get_embedder():
    global _model
    if _model is None:
        model_name = _DEFAULT_MODEL_NAME
        for baked_in_path in _BAKED_MODEL_PATHS:
            if os.path.exists(baked_in_path):
                model_name = baked_in_path
                logger.info(f"Using baked-in BGE model at {baked_in_path}")
                break
        else:
            logger.info(f"Downloading BGE model: {model_name}")

        _model = SentenceTransformer(model_name)
    return _model


def embed(text: str) -> list[float]:
    model = get_embedder()
    return model.encode(text, normalize_embeddings=True).tolist()
