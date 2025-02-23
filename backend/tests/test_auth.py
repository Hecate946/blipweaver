import pytest
import uuid
from httpx import AsyncClient
from fastapi import status
from app.main import app  # Adjust the import based on your project structure

BASE_URL = "http://127.0.0.1:8000/auth"

def unique_user():
    """Generate unique username and email for testing."""
    unique_str = uuid.uuid4().hex[:8]
    return {
        "username": f"testuser_{unique_str}",
        "email": f"test_{unique_str}@example.com",
        "password": "testpassword"
    }

@pytest.mark.asyncio
async def test_signup_success():
    user = unique_user()
    async with AsyncClient(base_url=BASE_URL) as ac:
        response = await ac.post("/signup", json=user)
    assert response.status_code == status.HTTP_200_OK
    json_resp = response.json()
    assert "username" in json_resp
    assert json_resp["username"] == user["username"]

@pytest.mark.asyncio
async def test_signup_existing_email():
    user = unique_user()
    async with AsyncClient(base_url=BASE_URL) as ac:
        await ac.post("/signup", json=user)
        # Attempt second signup with same email (different username)
        user2 = unique_user()
        user2["email"] = user["email"]
        response = await ac.post("/signup", json=user2)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Email already registered"

@pytest.mark.asyncio
async def test_signup_existing_username():
    user = unique_user()
    async with AsyncClient(base_url=BASE_URL) as ac:
        await ac.post("/signup", json=user)
        # Attempt second signup with same username (different email)
        user2 = unique_user()
        user2["username"] = user["username"]
        response = await ac.post("/signup", json=user2)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Username already taken"

async def verify_user(ac: AsyncClient, email: str):
    # Request email verification token
    token_resp = await ac.post("/request-email-verification", json={"email": email})
    token = token_resp.json()["verification_token"]
    # Verify email using the token
    verify_resp = await ac.post("/verify-email", json={"access_token": token})
    assert verify_resp.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_request_email_verification():
    user = unique_user()
    async with AsyncClient(base_url=BASE_URL) as ac:
        # Call the endpoint to request verification token
        resp = await ac.post("/request-email-verification", json={"email": user["email"]})
    assert resp.status_code == status.HTTP_200_OK
    assert "verification_token" in resp.json()

@pytest.mark.asyncio
async def test_verify_email_invalid_token():
    async with AsyncClient(base_url=BASE_URL) as ac:
        # Use an invalid token value
        resp = await ac.post("/verify-email", json={"access_token": "invalidtoken"})
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json()["detail"] == "Invalid or expired token"

@pytest.mark.asyncio
async def test_login_unverified():
    user = unique_user()
    async with AsyncClient(base_url=BASE_URL) as ac:
        await ac.post("/signup", json=user)
        # Do not verify the user and attempt login
        login_resp = await ac.post("/login", json={
            "identifier": user["username"],
            "password": user["password"]
        })
    # Should fail because the user is not verified
    assert login_resp.status_code == status.HTTP_403_FORBIDDEN
    assert login_resp.json()["detail"] == "Email not verified"

@pytest.mark.asyncio
async def test_login_success():
    user = unique_user()
    async with AsyncClient(base_url=BASE_URL) as ac:
        await ac.post("/signup", json=user)
        await verify_user(ac, user["email"])
        response = await ac.post("/login", json={
            "identifier": user["username"],
            "password": user["password"]
        })
    assert response.status_code == status.HTTP_200_OK
    json_resp = response.json()
    assert "access_token" in json_resp

@pytest.mark.asyncio
async def test_login_failure():
    async with AsyncClient(base_url=BASE_URL) as ac:
        response = await ac.post("/login", json={
            "identifier": "nonexistent",
            "password": "wrongpassword"
        })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid credentials"

@pytest.mark.asyncio
async def test_protected_route():
    user = unique_user()
    async with AsyncClient(base_url=BASE_URL) as ac:
        await ac.post("/signup", json=user)
        await verify_user(ac, user["email"])
        login_resp = await ac.post("/login", json={
            "identifier": user["username"],
            "password": user["password"]
        })
        token = login_resp.json()["access_token"]
        response = await ac.get("/protected", headers={
            "Authorization": f"Bearer {token}"
        })
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "You have access!"

@pytest.mark.asyncio
async def test_logout():
    async with AsyncClient(base_url=BASE_URL) as ac:
        response = await ac.post("/logout")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Logged out successfully"

@pytest.mark.asyncio
async def test_delete_account():
    user = unique_user()
    async with AsyncClient(base_url=BASE_URL) as ac:
        await ac.post("/signup", json=user)
        await verify_user(ac, user["email"])
        login_resp = await ac.post("/login", json={
            "identifier": user["username"],
            "password": user["password"]
        })
        token = login_resp.json()["access_token"]
        del_resp = await ac.delete("/delete-account", headers={
            "Authorization": f"Bearer {token}"
        })
        assert del_resp.status_code == status.HTTP_200_OK
        assert del_resp.json()["message"] == "Account deleted successfully"
        login_resp_after = await ac.post("/login", json={
            "identifier": user["username"],
            "password": user["password"]
        })
        assert login_resp_after.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND)
