from dropship.auto_debug_diagnose import diagnose
def test_import_error():
    assert diagnose("ModuleNotFoundError: No module named 'dropship'")["category"]=="python_import"
def test_rate_limit():
    assert diagnose("429 Client Error: https://developers.cjdropshipping.com/api2.0/")["category"]=="cj_rate_limit"
def test_tests():
    assert diagnose("FAILED tests/test_x.py::test_case - AssertionError")["category"]=="test_assertion"
def test_no_raw_secrets():
    result=diagnose("Authorization: Bearer some-sensitive-value")
    assert "some-sensitive-value" not in str(result)
    assert result["safe_to_retry"] is False
