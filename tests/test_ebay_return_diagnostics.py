import requests
from dropship.ebay_account_policy_provider import EbayAccountPolicyProvider

class FakeSession:
    def __init__(self, response):
        self.response = response
    def get(self, *args, **kwargs):
        return self.response

def test_return_api_http_error_safe_diagnostics():
    response = requests.Response()
    response.status_code = 403
    response._content = b'{"errors":[{"errorId":12345,"message":"private string"}]}'
    response.url = "https://api.ebay.com/sell/account/v1/return_policy"
    provider = EbayAccountPolicyProvider(user_token="test-secret", session=FakeSession(response))
    result = provider.fetch_return_policy_evidence()
    assert result["status"] == "unknown"
    assert result["http_status"] == 403
    assert result["ebay_error_ids"] == [12345]
    assert "private string" not in str(result)
    assert "test-secret" not in str(result)
    assert result["live_execution_allowed"] is False
