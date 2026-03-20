import pytest

@pytest.mark.asyncio
async def test_register(test_client, setup_database):
    """测试用户注册"""
    # 测试注册新用户
    response = test_client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "is_active" in data

    # 测试注册已存在的用户名
    response = test_client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test2@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]

    # 测试注册已存在的邮箱
    response = test_client.post(
        "/auth/register",
        json={
            "username": "testuser2",
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

@pytest.mark.asyncio
async def test_login(test_client, setup_database):
    """测试用户登录"""
    # 先注册用户
    test_client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )

    # 测试正确的登录凭据
    response = test_client.post(
        "/auth/login",
        data={
            "username": "testuser",
            "password": "testpassword123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # 测试错误的用户名
    response = test_client.post(
        "/auth/login",
        data={
            "username": "wronguser",
            "password": "testpassword123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

    # 测试错误的密码
    response = test_client.post(
        "/auth/login",
        data={
            "username": "testuser",
            "password": "wrongpassword"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]
