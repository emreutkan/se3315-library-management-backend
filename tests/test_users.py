def test_list_users_unauthenticated(client):
    res = client.get("/api/users")
    assert res.status_code == 401

def test_list_users_forbidden(client, user_token):
    res = client.get("/api/users", headers={
        "Authorization": f"Bearer {user_token}"
    })
    assert res.status_code == 403

def test_list_users_success(client, admin_token):
    res = client.get("/api/users", headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert res.status_code == 200
    users = res.get_json()
    assert isinstance(users, list)
    assert any(u["username"] == "admin" for u in users)

def test_add_user_success(client, admin_token):
    res = client.post("/api/users", json={
        "username": "newuser", "password": "pass", "is_admin": False
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 201
    u = res.get_json()
    assert u["username"] == "newuser"

def test_add_user_conflict(client, admin_token):
    # adding existing admin again
    res = client.post("/api/users", json={
        "username": "admin", "password": "pass"
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 400
