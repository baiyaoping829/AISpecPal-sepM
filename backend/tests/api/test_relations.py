import pytest

@pytest.mark.asyncio
async def test_relations(test_client, setup_database):
    """测试关联关系管理功能"""
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

    # 创建两个规范标准
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
    spec1_id = response.json()["id"]

    response = test_client.post(
        "/specifications/",
        json={
            "name": "混凝土结构设计规范",
            "code": "GB 50010-2010",
            "type": "GB",
            "level": 1,
            "status": 1,
            "compilation_unit": "中华人民共和国住房和城乡建设部",
            "description": "混凝土结构设计规范",
            "keywords": "混凝土,结构,设计",
            "file_path": "/standards/specs/GB_50010-2010.pdf",
            "file_size": 1024000,
            "file_hash": "testhash456"
        },
        headers=headers
    )
    spec2_id = response.json()["id"]

    # 测试创建关联关系
    response = test_client.post(
        "/relations/",
        json={
            "source_id": spec1_id,
            "target_id": spec2_id,
            "relation_type": "reference",
            "description": "参考关系"
        },
        headers=headers
    )
    assert response.status_code == 200
    relation_id = response.json()["id"]

    # 测试获取源规范标准的关联关系
    response = test_client.get(f"/relations/source/{spec1_id}", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) > 0

    # 测试获取目标规范标准的关联关系
    response = test_client.get(f"/relations/target/{spec2_id}", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) > 0

    # 测试获取关联关系详情
    response = test_client.get(f"/relations/{relation_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["source_id"] == spec1_id
    assert response.json()["target_id"] == spec2_id
    assert response.json()["relation_type"] == "reference"

    # 测试更新关联关系
    response = test_client.put(
        f"/relations/{relation_id}",
        json={
            "relation_type": "supplement",
            "description": "补充关系"
        },
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["relation_type"] == "supplement"
    assert response.json()["description"] == "补充关系"

    # 测试删除关联关系
    response = test_client.delete(f"/relations/{relation_id}", headers=headers)
    assert response.status_code == 200
    assert "Relation deleted successfully" in response.json()["message"]

    # 测试获取已删除的关联关系
    response = test_client.get(f"/relations/{relation_id}", headers=headers)
    assert response.status_code == 404
    assert "Relation not found" in response.json()["detail"]
