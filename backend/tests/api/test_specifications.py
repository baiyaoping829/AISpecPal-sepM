import pytest

@pytest.mark.asyncio
async def test_specifications(test_client, setup_database):
    """测试规范标准的CRUD功能"""
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

    # 测试创建规范标准
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
    assert response.status_code == 200
    spec_id = response.json()["id"]

    # 测试获取规范标准列表
    response = test_client.get("/specifications/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) > 0

    # 测试获取规范标准详情
    response = test_client.get(f"/specifications/{spec_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "建筑设计防火规范"
    assert response.json()["code"] == "GB 50016-2014"

    # 测试更新规范标准
    response = test_client.put(
        f"/specifications/{spec_id}",
        json={
            "name": "建筑设计防火规范(2014年版)",
            "description": "建筑设计防火规范(2014年版)"
        },
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "建筑设计防火规范(2014年版)"
    assert response.json()["description"] == "建筑设计防火规范(2014年版)"

    # 测试删除规范标准
    response = test_client.delete(f"/specifications/{spec_id}", headers=headers)
    assert response.status_code == 200
    assert "Specification deleted successfully" in response.json()["message"]

    # 测试获取已删除的规范标准
    response = test_client.get(f"/specifications/{spec_id}", headers=headers)
    assert response.status_code == 404
    assert "Specification not found" in response.json()["detail"]
