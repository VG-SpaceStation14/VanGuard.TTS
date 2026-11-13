import pytest
from unittest.mock import patch, MagicMock
import numpy as np

@pytest.fixture(autouse=True)
def mock_model_loading():
    mock_model = MagicMock()
    mock_model.speakers = ['aidar', 'baya', 'kseniya', 'eugene', 'xenia']
    mock_model.apply_tts.return_value = np.zeros(24000, dtype=np.float32)
    
    
    with patch('ss14tts.model', mock_model):
        yield
