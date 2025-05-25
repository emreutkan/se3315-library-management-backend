def test_login_success(client):
    res = client.post("/api/auth/login", json={
        "username": "admin", "password": "admin123"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert "access_token" in data

def test_login_failure(client):
    res = client.post("/api/auth/login", json={
        "username": "admin", "password": "wrongpass"
    })
    assert res.status_code == 401
