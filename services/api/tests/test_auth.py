def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["phase"] == 1


def test_login_seeded_admin(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email_or_username": "admin", "password": "FindShareAdmin!dev"},
    )
    assert response.status_code == 200
    assert response.json()["user"]["role"] == "admin"
    assert response.json()["tokens"]["access_token"]


def test_register_requires_invite(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "new@example.com", "username": "newshopper", "password": "TestUser1!ok"},
    )
    assert response.status_code == 403
    assert response.json()["code"] == "INVITE_REQUIRED"


def test_register_with_invite_and_ignore_role(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "invited@example.com",
            "username": "invited",
            "password": "TestUser1!ok",
            "invitation_code": "FINDSHARE-DEV-INVITE",
            "role": "admin",
        },
    )
    assert response.status_code == 201
    assert response.json()["user"]["role"] == "user"
    token = response.json()["local_verify_token"]
    verified = client.post("/api/v1/auth/verify-email", json={"token": token})
    assert verified.status_code == 204


def test_beta_full(client, db_session):

    from app.models.platform import BetaConfiguration

    config = db_session.get(BetaConfiguration, 1)
    config.maximum_active_users = 3
    db_session.commit()
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "overflow@example.com",
            "username": "overflow",
            "password": "TestUser1!ok",
            "invitation_code": "FINDSHARE-DEV-INVITE",
        },
    )
    assert response.status_code == 403
    assert response.json()["code"] == "BETA_FULL"


def test_invalid_login(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email_or_username": "admin", "password": "wrong-password!"},
    )
    assert response.status_code == 401


def test_beta_status_invite_only(client):
    data = client.get("/api/v1/beta/status").json()
    assert data["registration_mode"] == "invite_only"
    assert data["maximum_active_users"] == 10


def test_account_deletion_hides_identity(client):
    registered = client.post(
        "/api/v1/auth/register",
        json={
            "email": "gone-user@example.com",
            "username": "gone_user",
            "password": "ValidPass!123",
            "invitation_code": "FINDSHARE-DEV-INVITE",
        },
    )
    assert registered.status_code == 201, registered.text
    token = registered.json()["tokens"]["access_token"]
    verify_token = registered.json()["local_verify_token"]
    client.post("/api/v1/auth/verify-email", json={"token": verify_token})
    deleted = client.delete("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert deleted.status_code == 204
    lookup = client.get("/api/v1/users/gone_user")
    assert lookup.status_code == 404
