from pydantic import BaseModel, Field, field_serializer
from uuid import uuid4, UUID
from typing import List, Literal, Optional
from .general_configs import ALLOWABLE_UNITS

DEFAULT_UNITS = {
    "angle rx": "deg",
    "angle ry": "deg",
    "angle rz": "deg",
    "angle dominant direction": "deg",
    "bending moment local x": "kNm",
    "bending moment local y": "kNm",
    "bending moment dominant direction": "kNm",
    "shear force local x": "kN",
    "shear force local y": "kN",
    "shear force dominant direction": "kN",
    "effective tension": "kN",
    "displacement x": "m",
    "displacement y": "m",
    "displacement z": "m",
    "position x": "m",
    "position y": "m",
    "position z": "m",
    "velocity x": "m/s",
    "velocity y": "m/s",
    "velocity z": "m/s",
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
    "angle dominant direction",
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
    "velocity z",
]

#ALLOWABLE_UNITS = Literal["m", "N", "kN", "Nm", "kNm", "deg", "rad", "m/s"]


class update_analysis_summary_input(BaseModel, extra="forbid"):
    hs: float = Field(gt=0.0)
    tp: float = Field(gt=0.0)
    location: ALLOWABLE_LOCATIONS
    result_type: ALLOWABLE_RESULT_TYPES
    method: str
    value: float


class update_analyses_summary_input(BaseModel, extra="forbid"):
    id: UUID
    updates: List[update_analysis_summary_input]


class general_results(BaseModel, extra="forbid"):
    m_eq_dominant_direction: Optional[float] = Field(None, ge=0.0)
    m_eq_local_scatter_dom_dir: Optional[float] = Field(None, ge=0.0)
    m_eq_NORSOK_scatter_dom_dir: Optional[float] = Field(None, ge=0.0)
    m_extreme_drilling: Optional[float] = Field(None, ge=0.0)
    m_extreme_nondrilling:  Optional[float] = Field(None, ge=0.0)

    # class Config:
    #     schema_extra = {"example": {"M_eq_dominant_direction": 1000.0}}


class lon_lat_location(BaseModel, extra="forbid"):
    longitude: float = Field(None, ge=-180.0, le=180.0)
    latitude: float = Field(None, ge=-90.0, le=90.0)


class soil_data(BaseModel, extra="forbid"):
    soil_type: Literal["api", "jeanjean", "zakeri"] | None = None
    soil_version: Literal["high", "low", "best"] | None = None
    soil_sensitivity: Literal["clay", "sand"] | None = None


class well_info(BaseModel, extra="forbid"):
    name: str = Field(None, min_length=1)
    well_id_4insight: str | None = None
    well_boundary_type: Literal["fixed", "well_included", "rotational_spring"]
    design_type: Literal["can", "satelite", "template"] | None = None
    location: lon_lat_location | None = None
    stiffness: float = Field(ge=0.0)
    feature: Literal["wlr", "rfj"] | None = None
    soil: soil_data | None = None


class analyses_metadata(BaseModel, extra="forbid"):
    responsible_engineer: str
    project_id: int = Field(gt=1000)
    well: well_info
    analysis_input_id: Optional[UUID] = None
    version: str = Field(min_length=1)
    analysis_type: str
    simulation_length: float = Field(gt=0.0)
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
    comment: str  | None = None
    offset_percent_of_wd: float = Field(ge=0.0)
    client: str = Field(None, min_length=1)

    @field_serializer('analysis_input_id')
    def analysis_input_id_serializer(self, analysis_input_id: UUID, _info):
        if analysis_input_id is None:
            return None
        return str(analysis_input_id)


class summary_value_type(BaseModel, extra="forbid"):
    method: Literal["std", "max", "min", "mean", "m_eq"]
    value: float


class one_seastate_result(BaseModel, extra="forbid"):
    summary_values: List[summary_value_type]
    time_series_id: Optional[str] = None


class seastate_result_data(BaseModel, extra="forbid"):
    hs: float = Field(gt=0.0)
    tp: float = Field(gt=0.0)
    result: one_seastate_result


class scatter_result_metadata(BaseModel, extra="forbid"):
    location: ALLOWABLE_LOCATIONS
    result_type: ALLOWABLE_RESULT_TYPES
    unit: ALLOWABLE_UNITS


class result_scatter(BaseModel, extra="forbid"):
    meta: scatter_result_metadata
    data: List[seastate_result_data]


class analysis_result(BaseModel, extra="forbid"):
    id: UUID = None
    metadata: analyses_metadata
    general_results: general_results
    all_seastate_results: List[result_scatter]
