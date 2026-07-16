import pytest
from httpx import AsyncClient


@pytest.fixture
async def auth_token(client: AsyncClient) -> str:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "resume-test@example.com",
            "password": "SecurePass123!",
            "full_name": "Resume Test User",
        },
    )
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_create_resume(client: AsyncClient, auth_token: str):
    response = await client.post(
        "/api/v1/resumes",
        json={
            "title": "Software Engineer Resume",
            "target_job_title": "Senior Software Engineer",
            "target_company": "Tech Corp",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Software Engineer Resume"
    assert data["target_job_title"] == "Senior Software Engineer"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_resumes(client: AsyncClient, auth_token: str):
    await client.post(
        "/api/v1/resumes",
        json={"title": "Resume 1"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    await client.post(
        "/api/v1/resumes",
        json={"title": "Resume 2"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    response = await client.get(
        "/api/v1/resumes",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


@pytest.mark.asyncio
async def test_duplicate_resume(client: AsyncClient, auth_token: str):
    create_response = await client.post(
        "/api/v1/resumes",
        json={"title": "Original Resume"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    resume_id = create_response.json()["id"]
    response = await client.post(
        f"/api/v1/resumes/{resume_id}/duplicate",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    assert "Copy" in response.json()["title"]


@pytest.mark.asyncio
async def test_delete_resume(client: AsyncClient, auth_token: str):
    create_response = await client.post(
        "/api/v1/resumes",
        json={"title": "To Delete"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    resume_id = create_response.json()["id"]
    response = await client.delete(
        f"/api/v1/resumes/{resume_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_resume_not_found(client: AsyncClient, auth_token: str):
    response = await client.get(
        "/api/v1/resumes/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 404
