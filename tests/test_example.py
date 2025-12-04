def test_example():
    """Simple example test"""
    assert 2 + 2 == 4


def test_with_fixture(sample_data):
    """Test with fixture"""
    assert sample_data["key"] == "value"
