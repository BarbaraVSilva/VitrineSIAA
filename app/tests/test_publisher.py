import os
from app.core.database import get_connection
from app.publisher.update_vitrine import generate_html_vitrine
from unittest.mock import patch

@patch('app.publisher.update_vitrine.git_push_vitrine')
def test_vitrine_generation_empty(mock_git_push, test_db):
    """Test if the vitrine generator logic handles an empty database gracefully."""
    
    # Should not raise exception
    try:
        generate_html_vitrine()
        success = True
    except Exception as e:
        success = False
        
    assert success == True
    # Verify it called the git push mock
    mock_git_push.assert_called_once()
