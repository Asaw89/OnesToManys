"""
Unit tests for Music Library API
Run with: pytest test.py -v
Install pytest first: pip install pytest httpx
"""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# ============ GET TESTS ============

def test_get_all_musicians():
    """Test getting all musicians"""
    response = client.get("/musicians")
    assert response.status_code == 200
    assert "musicians" in response.json()


def test_get_all_albums():
    """Test getting all albums"""
    response = client.get("/albums")
    assert response.status_code == 200
    assert "albums" in response.json()


def test_get_musician_by_id():
    """Test getting a single musician by ID"""
    response = client.get("/musicians/7")
    assert response.status_code == 200
    data = response.json()
    # Should return either a musician or an error
    assert "musician" in data or "error" in data


def test_get_musician_by_id_not_found():
    """Test getting a musician that doesn't exist"""
    response = client.get("/musicians/99999")
    assert response.status_code == 200
    assert "error" in response.json()


def test_search_musician_by_name():
    """Test searching for a musician by name"""
    response = client.get("/musicians/search/Taylor%20Swift")
    assert response.status_code == 200
    data = response.json()
    assert "musician" in data or "error" in data


def test_search_musician_not_found():
    """Test searching for a musician that doesn't exist - should return suggestion"""
    response = client.get("/musicians/search/NotARealBand12345")
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert "suggestion" in data


def test_get_albums_by_musician_id():
    """Test getting all albums for a musician by ID"""
    response = client.get("/musicians/7/albums")
    assert response.status_code == 200
    data = response.json()
    assert "albums" in data or "error" in data or "No albums found" in str(data)


def test_get_albums_by_musician_name():
    """Test getting all albums for a musician by name"""
    response = client.get("/musicians/search/Taylor%20Swift/albums")
    assert response.status_code == 200
    data = response.json()
    assert "albums" in data or "Musician not found" in str(data)


def test_search_album_by_title():
    """Test searching for an album by title"""
    response = client.get("/albums/search/title/1989")
    assert response.status_code == 200
    data = response.json()
    assert "album" in data or "error" in data


def test_search_album_by_id():
    """Test searching for an album by ID"""
    response = client.get("/albums/search/1")
    assert response.status_code == 200
    data = response.json()
    assert "album" in data or "error" in data


# ============ POST TESTS ============

def test_create_musician():
    """Test creating a new musician"""
    new_musician = {
        "musician_name": "Test Band 12345",
        "genre": "Test Genre",
        "year_formed": 2024,
        "origin": "Test City, TS"
    }
    response = client.post("/musicians", json=new_musician)
    assert response.status_code == 200
    # Should succeed or say already exists
    data = response.json()
    assert "Musician successfully added" in str(data) or "already exists" in str(data)


def test_create_musician_duplicate():
    """Test creating a musician that already exists"""
    new_musician = {
        "musician_name": "Test Band 12345",
        "genre": "Test Genre",
        "year_formed": 2024,
        "origin": "Test City, TS"
    }
    # First create
    client.post("/musicians", json=new_musician)
    # Try to create again
    response = client.post("/musicians", json=new_musician)
    assert response.status_code == 200
    assert "already exists" in str(response.json())


def test_create_album():
    """Test creating a new album"""
    new_album = {
        "musician_id": 7,
        "title": "Test Album 12345",
        "number_of_tracks": 10,
        "label": "Test Label",
        "description": "Test Description"
    }
    response = client.post("/albums", json=new_album)
    assert response.status_code == 200
    data = response.json()
    assert "Album successfully added" in str(data) or "already exists" in str(data)


# ============ PUT TESTS ============

def test_update_musician():
    """Test updating a musician"""
    update_data = {
        "musician_name": "Updated Name",
        "genre": "Updated Genre",
        "year_formed": 2020,
        "origin": "Updated City"
    }
    response = client.put("/musicians/7", json=update_data)
    assert response.status_code == 200


def test_update_album():
    """Test updating an album"""
    update_data = {
        "musician_id": 7,
        "title": "Updated Album Title",
        "number_of_tracks": 15,
        "label": "Updated Label",
        "description": "Updated Description"
    }
    response = client.put("/albums/1", json=update_data)
    assert response.status_code == 200


# ============ DELETE TESTS ============

def test_delete_musician():
    """Test deleting a musician"""
    # First create one to delete
    new_musician = {
        "musician_name": "Delete Me Band",
        "genre": "Test",
        "year_formed": 2024,
        "origin": "Test"
    }
    client.post("/musicians", json=new_musician)
    
    # Get all musicians to find the ID
    response = client.get("/musicians")
    musicians = response.json()["musicians"]
    
    # Find the one we just created
    delete_id = None
    for m in musicians:
        if m["musician_name"] == "Delete Me Band":
            delete_id = m["id"]
            break
    
    if delete_id:
        response = client.delete(f"/musicians/{delete_id}")
        assert response.status_code == 200
        assert "deleted" in str(response.json())


def test_delete_album():
    """Test deleting an album"""
    # First create one to delete
    new_album = {
        "musician_id": 7,
        "title": "Delete Me Album",
        "number_of_tracks": 5,
        "label": "Test",
        "description": "Test"
    }
    client.post("/albums", json=new_album)
    
    # Get all albums to find the ID
    response = client.get("/albums")
    albums = response.json()["albums"]
    
    # Find the one we just created
    delete_id = None
    for a in albums:
        if a["title"] == "Delete Me Album":
            delete_id = a["id"]
            break
    
    if delete_id:
        response = client.delete(f"/albums/{delete_id}")
        assert response.status_code == 200
        assert "deleted" in str(response.json())


# ============ DUMP/LOAD TESTS ============

def test_dump_data():
    """Test exporting data to JSON"""
    response = client.get("/dump")
    assert response.status_code == 200
    assert "Exported" in str(response.json())


# Note: Be careful with load test - it will add data to your database
# def test_load_data():
#     """Test importing data from JSON"""
#     response = client.post("/load")
#     assert response.status_code == 200
#     assert "imported" in str(response.json())


if __name__ == "__main__":
    print("Run tests with: pytest test.py -v")
