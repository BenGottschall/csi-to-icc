"""
Script to add sample data for testing the API.
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def add_csi_code():
    """Add a sample CSI code."""
    data = {
        "code": "03 30 00",
        "division": 3,
        "title": "Cast-in-Place Concrete",
        "description": "Concrete formwork, reinforcement, and cast-in-place concrete"
    }
    response = requests.post(f"{BASE_URL}/csi-codes", json=data)
    print(f"Added CSI code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def add_icc_document():
    """Add a sample ICC document."""
    data = {
        "code": "IBC",
        "year": 2024,
        "title": "International Building Code",
        "state": None,
        "base_url": "https://codes.iccsafe.org/content/IBC2024"
    }
    response = requests.post(f"{BASE_URL}/icc-documents", json=data)
    print(f"\nAdded ICC document: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def add_icc_section(document_id):
    """Add a sample ICC section."""
    data = {
        "document_id": document_id,
        "section_number": "1905.2",
        "title": "Minimum Specified Compressive Strength",
        "chapter": 19,
        "url": "https://codes.iccsafe.org/content/IBC2024/chapter-19-concrete#IBC2024_Pt05_Ch19_Sec1905.2",
        "description": "Requirements for concrete compressive strength"
    }
    response = requests.post(f"{BASE_URL}/icc-sections", json=data)
    print(f"\nAdded ICC section: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def add_another_icc_section(document_id):
    """Add another ICC section."""
    data = {
        "document_id": document_id,
        "section_number": "1905.12",
        "title": "Curing",
        "chapter": 19,
        "url": "https://codes.iccsafe.org/content/IBC2024/chapter-19-concrete#IBC2024_Pt05_Ch19_Sec1905.12",
        "description": "Concrete shall be maintained above 50°F and in a moist condition for at least the first 7 days"
    }
    response = requests.post(f"{BASE_URL}/icc-sections", json=data)
    print(f"\nAdded another ICC section: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def create_mapping(csi_code_id, icc_section_id, relevance="primary"):
    """Create a mapping between CSI code and ICC section."""
    data = {
        "csi_code_id": csi_code_id,
        "icc_section_id": icc_section_id,
        "relevance": relevance,
        "notes": f"Mapping for concrete requirements - {relevance}"
    }
    response = requests.post(f"{BASE_URL}/mappings", json=data)
    print(f"\nCreated mapping: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def test_search():
    """Test the search endpoint."""
    data = {
        "csi_code": "03 30 00",
        "state": None,
        "year": 2024
    }
    response = requests.post(f"{BASE_URL}/search", json=data)
    print(f"\n{'='*60}")
    print("SEARCH RESULTS:")
    print('='*60)
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    print("Adding sample data to the database...\n")

    # Add CSI code
    csi_code = add_csi_code()

    # Add ICC document
    icc_doc = add_icc_document()

    # Add ICC sections
    icc_section1 = add_icc_section(icc_doc["id"])
    icc_section2 = add_another_icc_section(icc_doc["id"])

    # Create mappings
    mapping1 = create_mapping(csi_code["id"], icc_section1["id"], "primary")
    mapping2 = create_mapping(csi_code["id"], icc_section2["id"], "secondary")

    # Test search
    test_search()

    print("\n" + "="*60)
    print("Sample data added successfully!")
    print("="*60)
    print("\nYou can now:")
    print("- Visit http://localhost:8000/api/docs for interactive API documentation")
    print("- Test the search endpoint with: POST /api/search")
    print("- Browse CSI codes at: GET /api/csi-codes")
