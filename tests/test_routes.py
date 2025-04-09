# No need to import pytest if using fixtures like test_client
# No need to import test_app fixture directly if only using test_client

def test_ping(test_client):
    """Test the /ping route."""
    response = test_client.get('/ping')
    assert response.status_code == 200
    assert response.data == b'pong' # Response data is bytes