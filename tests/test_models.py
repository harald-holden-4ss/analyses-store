import os, glob, json
from app.models.vessel import vessel
from app.models.analyses import analysis_result
from app.models.soil import soil_data
from app.models.analysis_input import analysis_input
import pytest
TEST_FILE_LOCATION = r'tests/testfiles/models'

# def test_dummy():
#     with open(r'tests/testfiles/models/analyses/analysis_1.json', 'r+') as f:
#         obj_dict = json.load(f)
#         print(obj_dict)
#         analysis_result(**obj_dict)

@pytest.mark.parametrize("path_to_json_files, validation_object",[
    ('vessel', vessel),
    ('soil', soil_data),
    ('analysis_input', analysis_input),
    ('analyses', analysis_result)
])
# )
def test_json_files(path_to_json_files, validation_object):
    json_files = glob.glob(os.path.join(
        TEST_FILE_LOCATION, 
        path_to_json_files, 
        '*.json'))
    for file in json_files:
        with open(file, 'r+') as f:
            obj_dict = json.load(f)
            validation_object(**obj_dict)
