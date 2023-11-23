from pydantic import BaseModel, field_serializer

from uuid import UUID
from .general_configs import ALLOWABLE_UNITS


class data_value_with_unit(BaseModel, extra = "forbid"):
    value: float
    unit: ALLOWABLE_UNITS


class analysis_input_data(BaseModel, extra="forbid"):
    target_overpull: data_value_with_unit | None = None
    bop_L2: data_value_with_unit | None = None
    lmrp_submerged_weight: data_value_with_unit | None = None
    flex_joint_stiffness: data_value_with_unit | None = None
    OD_riser_adapter: data_value_with_unit | None = None
    ID_riser_adapter: data_value_with_unit | None = None


class analysis_input(BaseModel, extra="forbid"):
    id: UUID | None = None
    vessel_id: UUID
    input_data_file_location: str
    tally_sheet_name: str | None = None
    comments: str | None = None
    data: analysis_input_data | None = None

    @field_serializer('vessel_id')
    def vessel_id_serializer(self, vessel_id: UUID, _info):
        if vessel_id is None:
            return None
        return str(vessel_id)


