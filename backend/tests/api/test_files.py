import pytest
import tempfile

@pytest.mark.asyncio
async def test_files(test_client, setup_database):
    """测试文件上传和下载功能"""
    # 先注册并登录用户
    test_client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    response = test_client.post(
        "/auth/login",
        data={
            "username": "testuser",
            "password": "testpassword123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 创建一个临时文件用于测试上传
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test file for upload")
        temp_file_path = f.name

    try:
        # 测试上传文件
        with open(temp_file_path, 'rb') as f:
            response = test_client.post(
                "/files/upload",
                files={"file": ("test.txt", f, "text/plain")},
                headers=headers
            )
        assert response.status_code == 200
        file_path = response.json()["file_path"]
        assert file_path is not None

        # 提取对象名用于测试下载
        import os
        object_name = os.path.relpath(file_path, "/standards")
        object_name = object_name.lstrip("/")

        # 测试下载文件
        response = test_client.get(f"/files/download/{object_name}", headers=headers)
        assert response.status_code == 200
        assert response.content == b"This is a test file for upload"

        # 测试预览文件
        response = test_client.get(f"/files/preview/{object_name}", headers=headers)
        assert response.status_code == 200
        assert response.content == b"This is a test file for upload"
    finally:
        # 清理临时文件
        import os
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
