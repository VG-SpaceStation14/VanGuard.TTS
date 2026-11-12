import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch
import numpy as np

@pytest.fixture(autouse=True)
def mock_model_loading():
    with patch('torch.hub.download_url_to_file') as mock_download, \
         patch('torch.package.PackageImporter.load_pickle') as mock_load, \
         patch('torch.package.PackageImporter.__init__', return_value=None) as mock_init:
        
        class MockModel:
            speakers = ['ru_aigul', 'ru_alexandr', 'ru_albina', 'aidar', 'random']
            def to(self, device): pass
            def apply_tts(self, **kwargs):
                return np.zeros(24000, dtype=np.float32)
                
        mock_load.return_value = MockModel()
        yield
