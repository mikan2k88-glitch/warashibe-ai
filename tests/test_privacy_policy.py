from app import app


def test_privacy_policy_public():
    with app.test_client() as client:
        response = client.get("/privacy")
        assert response.status_code == 200
        assert response.mimetype == "text/html"
        assert b"warashibeai@gmail.com" in response.data
        assert b"sell.account.readonly" in response.data
        assert b"Privacy Policy" in response.data
