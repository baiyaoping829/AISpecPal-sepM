import pytest

@pytest.mark.asyncio
async def test_versions(test_client, setup_database):
    """测试版本管理功能"""
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

    # 创建一个规范标准
    response = test_client.post(
        "/specifications/",
        json={
            "name": "建筑设计防火规范",
            "code": "GB 50016-2014",
            "type": "GB",
            "level": 1,
            "status": 1,
            "compilation_unit": "中华人民共和国住房和城乡建设部",
            "description": "建筑设计防火规范",
            "keywords": "建筑,设计,防火",
            "file_path": "/standards/specs/GB_50016-2014.pdf",
            "file_size": 1024000,
            "file_hash": "testhash123"
        },
        headers=headers
    )
    spec_id = response.json()["id"]

    # 测试创建版本
    response = test_client.post(
        "/versions/",
        json={
            "specification_id": spec_id,
            "version_number": "1.1",
            "file_path": "/standards/specs/GB_50016-2014_v1.1.pdf",
            "change_log": "更新了部分条款",
            "is_current": 1
        },
        headers=headers
    )
    assert response.status_code == 200
    version_id = response.json()["id"]

    # 测试获取规范标准的所有版本
    response = test_client.get(f"/versions/specification/{spec_id}", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) > 0

    # 测试获取版本详情
    response = test_client.get(f"/versions/{version_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["version_number"] == "1.1"
    assert response.json()["is_current"] == 1

    # 测试更新版本
    response = test_client.put(
        f"/versions/{version_id}",
        json={
            "change_log": "更新了部分条款和附录",
            "is_current": 1
        },
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["change_log"] == "更新了部分条款和附录"

    # 测试删除版本
    response = test_client.delete(f"/versions/{version_id}", headers=headers)
    assert response.status_code == 200
    assert "Version deleted successfully" in response.json()["message"]

    # 测试获取已删除的版本
    response = test_client.get(f"/versions/{version_id}", headers=headers)
    assert response.status_code == 404
    assert "Version not found" in response.json()["detail"]
