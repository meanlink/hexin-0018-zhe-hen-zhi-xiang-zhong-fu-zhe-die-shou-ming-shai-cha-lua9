"""Station vocabularies shared by typed write inputs and workflow policy."""
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Format(StrEnum):
    SMALL = "A40"
    LARGE = "A60"


class Depot(StrEnum):
    NORTH = "north"
    SOUTH = "south"


class RepairMethod(StrEnum):
    CREASE = "crease_tape"
    GRIP = "handle_patch"
    TAB = "tab_replace"


class StationInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, allow_inf_nan=False)


class BoxInput(StationInput):
    label: str = Field(pattern=r"^[A-Z][A-Z0-9-]{2,45}$")
    format: Format
    depot: Depot
    fold_count: int = Field(ge=0, le=2999)


class Measurements(StationInput):
    cycle_no: int = Field(ge=1, le=3000)
    left_set_mm: float = Field(ge=0, le=60)
    right_set_mm: float = Field(ge=0, le=60)
    grip_drift_mm: float = Field(ge=0, le=40)
    closure_force_n: float = Field(ge=0, le=200)
    crease_crack_mm: float = Field(ge=0, le=100)


class FoldInput(Measurements):
    bench: str = Field(pattern=r"^[A-Z][A-Z0-9-]{2,40}$")


class ControlInput(Measurements):
    sample_code: str = Field(pattern=r"^[A-Z][A-Z0-9-]{2,45}$")
    format: Format
    source: str = Field(min_length=3, max_length=160)


class NoteInput(StationInput):
    note: str = Field(min_length=2, max_length=240)


class RepairInput(NoteInput):
    method: RepairMethod


class DispatchInput(StationInput):
    ticket: str = Field(pattern=r"^[A-Z][A-Z0-9-]{2,45}$")
    route_code: str = Field(pattern=r"^[A-Z][A-Z0-9-]{2,45}$")
