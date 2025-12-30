from typing import Any, TypeVar

import strawberry
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def input_to_pydantic(input: Any, model: type[T]) -> T:
    return model.model_validate(
        {
            key: value.value if isinstance(value, strawberry.Some) else value
            for key, value in input.__dict__.items()
            if value is not None
        }
    )
