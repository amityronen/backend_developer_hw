from fastapi.testclient import TestClient


def test_list_items_is_ordered_by_id(client: TestClient) -> None:
    response = client.get("/api/catalog/items")
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [1, 2, 3, 4]


def test_list_items_formats_money_as_two_decimals(client: TestClient) -> None:
    first = client.get("/api/catalog/items").json()[0]
    assert first["price"] == "24.90"
    assert first["currency"] == "ILS"
    assert first["approx_usd"] == "6.72"


def test_out_of_stock_availability(client: TestClient) -> None:
    items = {item["id"]: item for item in client.get("/api/catalog/items").json()}
    assert items[4]["availability"] == "out_of_stock"
    assert items[1]["availability"] == "in_stock"


def test_get_item_unknown_returns_error_json(client: TestClient) -> None:
    response = client.get("/api/catalog/items/999")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_quote_validation_error_shape(client: TestClient) -> None:
    response = client.post("/api/catalog/quote", json={"items": []})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_health(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "ok"}
