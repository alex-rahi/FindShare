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


def test_register_open_without_invite(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "new@example.com", "username": "newshopper", "password": "TestUser1!ok"},
    )
    assert response.status_code == 201, response.text
    assert response.json()["user"]["role"] == "user"


def test_register_ignores_client_supplied_role(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "invited@example.com",
            "username": "invited",
            "password": "TestUser1!ok",
            "role": "admin",
        },
    )
    assert response.status_code == 201
    assert response.json()["user"]["role"] == "user"
    token = response.json()["local_verify_token"]
    verified = client.post("/api/v1/auth/verify-email", json={"token": token})
    assert verified.status_code == 204


def test_invite_only_enforced_when_configured(client, db_session):
    from app.models.platform import BetaConfiguration

    config = db_session.get(BetaConfiguration, 1)
    config.registration_mode = "invite_only"
    config.maximum_active_users = 3
    db_session.commit()
    missing = client.post(
        "/api/v1/auth/register",
        json={"email": "needs-invite@example.com", "username": "needsinvite", "password": "TestUser1!ok"},
    )
    assert missing.status_code == 403
    assert missing.json()["code"] == "INVITE_REQUIRED"
    overflow = client.post(
        "/api/v1/auth/register",
        json={
            "email": "overflow@example.com",
            "username": "overflow",
            "password": "TestUser1!ok",
            "invitation_code": "FINDSHARE-DEV-INVITE",
        },
    )
    assert overflow.status_code == 403
    assert overflow.json()["code"] == "BETA_FULL"


def test_invalid_login(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email_or_username": "admin", "password": "wrong-password!"},
    )
    assert response.status_code == 401


def test_beta_status_is_open(client):
    data = client.get("/api/v1/beta/status").json()
    assert data["registration_mode"] == "open"
    assert data["registration_enabled"] is True


def test_account_deletion_hides_identity(client):
    registered = client.post(
        "/api/v1/auth/register",
        json={
            "email": "gone-user@example.com",
            "username": "gone_user",
            "password": "ValidPass!123",
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
