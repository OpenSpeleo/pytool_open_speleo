import datetime
import uuid
from pathlib import Path
from typing import Any
from typing import Self

from pydantic import UUID4
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import field_serializer
from pydantic import field_validator

from openspeleo_lib.formats.ariane.parser import ArianeParser
from openspeleo_lib.mixins import AutoIdModelMixin
from openspeleo_lib.mixins import BaseMixin
from openspeleo_lib.mixins import NameIdModelMixin
from openspeleo_lib.utils import str2bool


class RadiusVector(BaseModel):
    tension_corridor: float
    tension_profile: float
    angle: float
    norm: float  # Euclidian Norm aka. length

    model_config = ConfigDict(extra="forbid")

    @field_serializer("norm", "angle", "tension_profile", "tension_corridor")
    def serialize_numeric(self, value: float) -> str:
        return str(value)

    @field_validator("*", mode="before")
    @classmethod
    def convert_to_float(cls, v: str | float | None ) -> float:
        if isinstance(v, str):
            return float(v)
        return v


class RadiusCollection(BaseModel):
    radius_vector: list[RadiusVector] = []

    model_config = ConfigDict(extra="forbid")

    @field_validator("radius_vector", mode="before")
    @classmethod
    def ensure_list_type(cls, v: list | dict | None) -> list:
        if isinstance(v, dict):
            return [v]
        return v


class Shape(BaseModel):
    radius_collection: RadiusCollection
    has_profile_azimuth: bool
    has_profile_tilt: bool
    profile_azimuth: float
    profile_tilt: float

    model_config = ConfigDict(extra="forbid")

    @field_serializer("has_profile_tilt", "has_profile_azimuth")
    def serialize_bool(self, value: bool) -> str:
        return "true" if value else "false"

    @field_serializer("profile_tilt", "profile_azimuth")
    def serialize_numeric(self, value: float) -> str:
        return str(value)

    @field_validator("has_profile_azimuth", "has_profile_tilt", mode="before")
    @classmethod
    def convert_to_bool(cls, v: str | bool | None) -> bool:
        if isinstance(v, str):
            return str2bool(v)
        return v

    @field_validator("profile_azimuth", "profile_tilt", mode="before")
    @classmethod
    def convert_to_float(cls, v: str | float | None) -> float:
        if isinstance(v, str):
            return float(v)
        return v


class LayerStyle(BaseModel):
    dash_scale: float
    fill_color_string: str
    line_type: str
    line_type_scale: float
    opacity: float
    size_mode: str
    stroke_color_string: str
    stroke_thickness: float

    model_config = ConfigDict(extra="forbid")

    @field_serializer("stroke_thickness", "opacity", "line_type_scale", "dash_scale")
    def serialize_numeric(self, value: float) -> str:
        return str(value)

    @field_validator("dash_scale", "line_type_scale", "opacity", "stroke_thickness",
                     mode="before")
    @classmethod
    def convert_to_float(cls, v: str | float | None) -> float:
        if isinstance(v, str):
            return float(v)
        return v


class Layer(BaseModel):
    constant: bool = True
    locked_layer: bool = False
    layer_name: str
    style: LayerStyle
    visible: bool = True

    model_config = ConfigDict(extra="forbid")

    @field_serializer("visible", "locked_layer", "constant")
    def serialize_bool(self, value: bool) -> str:
        return "true" if value else "false"

    @field_validator("constant", "locked_layer", "visible", mode="before")
    @classmethod
    def convert_to_bool(cls, v: str | bool | None) -> bool:
        if isinstance(v, str):
            return str2bool(v)
        return v


class LayerCollection(BaseModel):
    layer_list: list[Layer] = []

    model_config = ConfigDict(extra="forbid")

    @field_validator("layer_list", mode="before")
    @classmethod
    def ensure_list_type(cls, v : list | dict | None) -> list:
        if isinstance(v, dict):
            return [v]
        return v


class SurveyShot(BaseMixin, AutoIdModelMixin, NameIdModelMixin, BaseModel):
    azimuth: float
    closure_to_id: int
    color: str
    comment: str | None = None
    date: datetime.date
    depth: float
    depth_in: float
    excluded: bool
    explorer: str
    from_id: int
    inclination: float
    latitude: float
    length: float
    locked: bool
    longitude: float
    profiletype: str
    section: str
    type: str

    # SubModel
    shape: Shape

    # LRUD
    left: float
    right: float
    up: float
    down: float

    model_config = ConfigDict(extra="forbid")

    @field_serializer("date")
    def serialize_dt(self, dt: datetime.date, _info):
        return dt.strftime("%Y-%m-%d")

    @field_serializer("locked", "excluded")
    def serialize_bool(self, value: bool) -> str:
        return "true" if value else "false"

    @field_serializer("left", "right", "up", "down", "longitude", "latitude", "length",
                      "inclination", "id", "from_id", "depth_in", "depth",
                      "closure_to_id", "azimuth")
    def serialize_numeric(self, value: float) -> str:
        return str(value)

    # model_config = ConfigDict(use_enum_values=True)


    @field_validator("azimuth", "depth", "depth_in", "down", "inclination", "latitude",
                     "left", "length", "longitude", "right", "up", mode="before")
    @classmethod
    def convert_to_float(cls, v: str | float | None) -> float:
        if isinstance(v, str):
            return float(v)
        return v

    @field_validator("closure_to_id", "from_id", "id", mode="before")
    @classmethod
    def convert_to_int(cls, v : str | int | None) -> int:
        if isinstance(v, str):
            return int(v)
        return v

    @field_validator("excluded", "locked", mode="before")
    @classmethod
    def convert_to_bool(cls, v: bool | str | None) -> bool:
        if isinstance(v, str):
            return str2bool(v)
        return v

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v : datetime.date | str | None) -> datetime.date:
        if isinstance(v, str):
            return datetime.date.fromisoformat(v)
        return v

# class Section(BaseMixin, UniqueSubFieldMixin, BaseModel):
#     id: int
#     shots: list[Shot] = []

#     @field_validator("shots")
#     @classmethod
#     def validate_shots_unique(cls, values: list[Shot]):
#         return cls.validate_unique(field="id", values=values)

class ShotCollection(BaseModel):
    shot_list: list[SurveyShot] = []

    model_config = ConfigDict(extra="forbid")

    @field_validator("shot_list", mode="before")
    @classmethod
    def ensure_list_type(cls, v: list| dict | None) -> list:
        if isinstance(v, dict):
            return [v]
        return v


class Survey(BaseMixin, BaseModel):
    speleodb_id: UUID4 = Field(default_factory=uuid.uuid4)
    cave_name: str
    unit: str = "m"
    data: ShotCollection = Field(default_factory=lambda: ShotCollection())
    layers: LayerCollection = Field(default_factory=lambda: LayerCollection())
    first_start_absolute_elevation: float = 0.0
    use_magnetic_azimuth: bool = True

    carto_ellipse: str | None = None
    carto_line: str | None = None
    carto_linked_surface: str | None = None
    carto_overlay: str | None = None
    carto_page: str | None = None
    carto_rectangle: str | None = None
    carto_selection: str | None = None
    carto_spline: str | None = None
    constraints: str | None = None
    list_annotation: str | None = None

    @field_serializer("use_magnetic_azimuth")
    def serialize_bool(self, value: bool) -> str:
        return "true" if value else "false"

    @field_serializer("speleodb_id", "first_start_absolute_elevation")
    def serialize_to_str(self, value: Any) -> str:
        return str(value)

    model_config = ConfigDict(extra="forbid")

    @field_validator("use_magnetic_azimuth", mode="before")
    @classmethod
    def convert_to_bool(cls, v):
        if isinstance(v, str):
            return str2bool(v)
        return v

    @field_validator("first_start_absolute_elevation", mode="before")
    @classmethod
    def convert_to_float(cls, v):
        if isinstance(v, str):
            return float(v)
        return v

    @classmethod
    def from_ariane_file(cls, filepath: Path, debug=False) -> Self:
        data = ArianeParser.from_ariane_file(filepath=filepath, debug=True)
        return cls.from_ariane_dict(data, debug=debug)

    def to_ariane_file(self, filepath: Path, debug=False) -> None:

        ariane_data = self.to_ariane_dict(debug=debug)

        ArianeParser.to_ariane_file(
            data=ariane_data,
            filepath=filepath,
            debug=debug
        )
