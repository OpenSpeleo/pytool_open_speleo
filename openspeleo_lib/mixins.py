import json

from iteration_utilities import duplicates
from pydantic import Field
from pydantic import field_validator
from pydantic import model_validator

from openspeleo_lib.errors import DuplicateValueError
from openspeleo_lib.utils import UniqueNameGenerator


class UniqueSubFieldMixin:

    @classmethod
    def validate_unique(cls, field: str, values: list) -> list:
        vals2check = [getattr(val, field) for val in values]
        dupl_vals = list(duplicates(vals2check))
        if dupl_vals:
            raise DuplicateValueError(
                f"[{cls.__name__}] Duplicate value found for `{field}`: "
                f"{dupl_vals}"
            )
        return values

class BaseMixin:
    name: str = Field(
        default_factory=lambda: UniqueNameGenerator.get(str_len=6),
        min_length=2,
        max_length=32
    )

    @model_validator(mode="before")
    @classmethod
    def enforce_snake_and_remove_none(cls, data: dict) -> dict:
        return {k: v for k, v in data.items() if v is not None}
        # return {camel2snakecase(k): v for k, v in data.items()}

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, value: str | None) -> str:
        """Note: Validators are only ran with custom fed values.
        Not autogenerated ones. Hence we need to register the name."""

        if value is None or value == "":
            return cls.name.default_factory()

        # 1. Verify the name is only composed of valid chars.
        for char in value:
            if char.upper() not in [
                *UniqueNameGenerator.VOCAB,
                *list("#-_@!~%&*[]{}()|: ")
            ]:
                raise ValueError(f"The character `{char}` is not allowed as `name`.")

        # 2. Register the name to avoid re-using it.
        UniqueNameGenerator.register(name=value)

        return value

    def to_json(self) -> str:
        """
        Serialize the model to a JSON string with indentation and sorted keys.

        Returns:
            str: The JSON representation of the model.
        """
        return json.dumps(self.model_dump(), indent=4, sort_keys=True)
