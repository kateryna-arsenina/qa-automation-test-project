from .reqres import ReqresProvider
from .dummyjson import DummyJsonProvider
from .jsonplaceholder import JsonPlaceholderProvider

REGISTRY = {
    "reqres": ReqresProvider,
    "dummyjson": DummyJsonProvider,
    "jsonplaceholder": JsonPlaceholderProvider,
}


def get_provider(name: str = "reqres") -> "Provider":
    if name not in REGISTRY:
        raise ValueError(f"Unknown provider '{name}'. Available: {list(REGISTRY)}")
    return REGISTRY[name]()
