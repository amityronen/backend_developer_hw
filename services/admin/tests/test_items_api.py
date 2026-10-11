from fastapi.testclient import TestClient

from tests.conftest import FakeRepository


def test_list_requires_token(client: TestClient) -> None:
    assert client.get("/api/admin/items").status_code == 401


def test_create_requires_token(client: TestClient) -> None:
    body = {"name": "X", "weight_kg": "2.00", "price": "9.90"}
    assert client.post("/api/admin/items", json=body).status_code == 401


def test_list_with_token(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.get("/api/admin/items", headers=auth_headers)
    assert response.status_code == 200
    assert [i["id"] for i in response.json()] == [1, 2, 3]
    assert response.json()[0]["price"] == "24.90"


def test_create_whole_item_records_audit(client: TestClient, auth_headers: dict[str, str],
                                         repo: FakeRepository) -> None:
    body = {"name": "Mini Melon", "weight_kg": "2.00", "price": "9.90", "quantity": 5}
    response = client.post("/api/admin/items", json=body, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["name"] == "Mini Melon"
    assert ("admin", "create", response.json()["id"]) in repo.audit


def test_create_half_item_derives_price(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post("/api/admin/items", json={"half_of": 2, "quantity": 3}, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["price"] == "6.00"
    assert response.json()["name"] == "Sugar Baby - Half"


def test_price_update_validation(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.patch("/api/admin/items/1/price", json={"price": "0"}, headers=auth_headers)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_price_update_changes_price(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.patch("/api/admin/items/2/price", json={"price": "11.50"}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["price"] == "11.50"


def test_quantity_delta_applies_sequentially(client: TestClient, auth_headers: dict[str, str]) -> None:
    for _ in range(3):
        response = client.patch("/api/admin/items/2/quantity", json={"delta": -5}, headers=auth_headers)
        assert response.status_code == 200
    assert response.json()["quantity"] == 45


def test_quantity_absolute_set(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.patch("/api/admin/items/3/quantity", json={"quantity": 40}, headers=auth_headers)
    assert response.json()["quantity"] == 40


def test_unknown_item_returns_not_found(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.patch("/api/admin/items/999/quantity", json={"delta": 1}, headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
