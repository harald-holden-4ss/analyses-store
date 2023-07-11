from pydantic import BaseModel, Field
from uuid import uuid4, UUID
from typing import Optional, List, Literal, Union
from enum import Enum

DEFAULT_UNITS = {
        "angle rx": "deg",
        "angle ry": "deg",
        "angle rz": "deg",
        "bending moment local x": "kNm",
        "bending moment local y": "kNm",
        "shear force local x": "kN",
        "shear force local y": "kN",
        "effective tension": "kN",
        "displacement x": "m",
        "displacement y": "m",
        "displacement z": "m",
        "position x": "m",
        "position y": "m",
        "position z": "m",
        "velocity x": "m/s",
        "velocity y": "m/s",
        "velocity z": "m/s"

}
ALLOWABLE_LOCATIONS = Literal[
        "wh_datum",
        "lfj_below",
        "lfj_above",
        "ufj_above",
        "ufj_below",
        "rig_center",
        "rig_rkb",
    ]


ALLOWABLE_RESULT_TYPES = Literal[
        "vessel heave",
        "vessel surge",
        "vessel sway",
        "vessel roll",
        "vessel pitch",
        "vessel yaw",
        "angle rx",
        "angle ry",
        "angle rz",
        "bending moment local x",
        "bending moment local y",
        "bending moment dominant direction",
        "shear force local x",
        "shear force local y",
        "shear force dominant direction",
        "effective tension",
        "displacement x",
        "displacement y",
        "displacement z",
        "position x",
        "position y",
        "position z",
        "velocity x",
        "velocity y",
        "velocity z"
    ]

ALLOWABLE_UNITS = Literal["m", "N", "kN", "Nm", "kNm", "deg", "rad", "m/s"]

class update_analysis_summary_input(BaseModel):
    hs: float = Field(gt=0.0)
    tp: float = Field(gt=0.0)
    location: ALLOWABLE_LOCATIONS
    result_type: ALLOWABLE_RESULT_TYPES
    method: str
    value: float


class update_analyses_summary_input(BaseModel):
    id: UUID
    updates: List[update_analysis_summary_input]


class general_results(BaseModel):
    m_eq_dominant_direction: Optional[float] = Field(ge=0.0)
    m_extreme_drilling: Optional[float] = Field(ge=0.0) 
    m_extreme_nondrilling: Optional[float] = Field(ge=0.0)


    class Config:
        schema_extra = {"example": {"M_eq_dominant_direction": 1000.0}}


class lon_lat_location(BaseModel):
    longitude: float = Field(None, ge=-180.0, le=180.0)
    latitude: float = Field(None, ge=-90.0, le=90.0)


class soil_data(BaseModel):
    soil_type: Optional[Literal["api", "jeanjean", "'zakeri"]]
    soil_version: Optional[Literal["high", "low", "best"]]
    soil_sensitivity: Optional[Literal["clay", "sand"]]


class well_info(BaseModel):
    name: Optional[str] = Field(min_length=1)
    well_boundary_type: Literal["fixed", "well_included", "rotational_spring"]
    design_type: Optional[Literal["can", "satelite", "template"]]
    location: Optional[lon_lat_location]
    stiffness: float = Field(ge=0.)
    feature: Union[None, Literal["wlr", "rfj"]]
    soil: Optional[soil_data]

class vessel(BaseModel):
    id: Optional[UUID]
    name: str = Field(min_length=1)
    imo: int = Field(gt=0)


class analyses_metadata(BaseModel):
    responsible_engineer: str
    project_id: int = Field(gt=1000)
    well: well_info
    version: str = Field(min_length=1)
    analysis_type: str
    simulation_lenght: float = Field(gt=0.0)
    water_depth: float = Field(gt=0.0)
    wave_direction: float = Field(ge=0.0, le=360.0)
    vessel_heading: float = Field(ge=0.0, le=360.0)
    current: Literal[
        "None", "1yr", "10yr", "10pct", "25pct", "75pct", "90pct", "median"
    ]
    vessel_id: str = Field(default_factory=uuid4)
    xt: bool
    soil_profile: str = Field(min_length=1)
    overpull: float = Field(ge=0.0)
    drillpipe_tension: float = Field(ge=0.0)
    comment: Optional[str]
    offset_percent_of_wd: float = Field(ge=0.0)
    client: str = Field(min_length=1)


class summary_value_type(BaseModel):
    method: Literal["std", "max", "min", 'mean', 'm_eq']
    value: float


class one_seastate_result(BaseModel):
    summary_values: List[summary_value_type]
    time_series_id: Optional[str]


class seastate_result_data(BaseModel):
    hs: float = Field(gt=0.0)
    tp: float = Field(gt=0.0)
    result: one_seastate_result


class scatter_result_metadata(BaseModel):
    location: ALLOWABLE_LOCATIONS
    result_type: ALLOWABLE_RESULT_TYPES
    unit: ALLOWABLE_UNITS


class result_scatter(BaseModel):
    meta: scatter_result_metadata
    data: List[seastate_result_data]


class analysis_result(BaseModel):
    id: Optional[UUID]
    metadata: analyses_metadata
    general_results: general_results
    all_seastate_results: List[result_scatter]
