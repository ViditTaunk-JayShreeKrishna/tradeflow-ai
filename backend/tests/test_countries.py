def test_get_countries_empty(client):
    response = client.get("/countries/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)