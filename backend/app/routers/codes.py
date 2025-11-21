"""
API routes for CSI and ICC code operations.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import crud, schemas
from ..database import get_db

router = APIRouter()


# CSI Code Endpoints
@router.get("/csi-codes", response_model=List[schemas.CSICode])
def list_csi_codes(
    skip: int = 0,
    limit: int = 100,
    division: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get a list of CSI codes.
    Optionally filter by division.
    """
    if division is not None:
        return crud.get_csi_codes_by_division(db, division=division)
    return crud.get_csi_codes(db, skip=skip, limit=limit)


@router.get("/csi-codes/{code}", response_model=schemas.CSICode)
def get_csi_code(code: str, db: Session = Depends(get_db)):
    """Get a specific CSI code by its code string (e.g., '03 30 00')."""
    db_csi_code = crud.get_csi_code(db, code=code)
    if db_csi_code is None:
        raise HTTPException(status_code=404, detail="CSI code not found")
    return db_csi_code


@router.post("/csi-codes", response_model=schemas.CSICode, status_code=201)
def create_csi_code(csi_code: schemas.CSICodeCreate, db: Session = Depends(get_db)):
    """Create a new CSI code."""
    # Check if code already exists
    existing = crud.get_csi_code(db, code=csi_code.code)
    if existing:
        raise HTTPException(status_code=400, detail="CSI code already exists")
    return crud.create_csi_code(db, csi_code=csi_code)


@router.get("/csi-codes/{code}/icc-sections", response_model=List[schemas.ICCSection])
def get_icc_sections_for_csi(
    code: str,
    state: Optional[str] = Query(None, description="Filter by state (e.g., 'CO', 'NY')"),
    year: Optional[int] = Query(None, description="Filter by year (e.g., 2021, 2024)"),
    icc_document: Optional[str] = Query(None, description="Filter by ICC document type (e.g., 'IBC')"),
    db: Session = Depends(get_db)
):
    """
    Get all ICC sections mapped to a specific CSI code.
    Supports filtering by state, year, and ICC document type.
    """
    # Verify CSI code exists
    csi = crud.get_csi_code(db, code=code)
    if not csi:
        raise HTTPException(status_code=404, detail="CSI code not found")

    return crud.get_icc_sections_for_csi_code(
        db,
        csi_code=code,
        state=state,
        year=year,
        icc_document=icc_document
    )


# ICC Document Endpoints
@router.get("/icc-documents", response_model=List[schemas.ICCDocument])
def list_icc_documents(
    code: Optional[str] = Query(None, description="Filter by document code (e.g., 'IBC')"),
    year: Optional[int] = Query(None, description="Filter by year"),
    state: Optional[str] = Query(None, description="Filter by state"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get a list of ICC documents with optional filtering."""
    return crud.get_icc_documents(
        db,
        code=code,
        year=year,
        state=state,
        skip=skip,
        limit=limit
    )


@router.get("/icc-documents/{document_id}", response_model=schemas.ICCDocument)
def get_icc_document(document_id: int, db: Session = Depends(get_db)):
    """Get a specific ICC document by ID."""
    db_doc = crud.get_icc_document(db, document_id=document_id)
    if db_doc is None:
        raise HTTPException(status_code=404, detail="ICC document not found")
    return db_doc


@router.post("/icc-documents", response_model=schemas.ICCDocument, status_code=201)
def create_icc_document(
    icc_doc: schemas.ICCDocumentCreate,
    db: Session = Depends(get_db)
):
    """Create a new ICC document."""
    return crud.create_icc_document(db, icc_doc=icc_doc)


# ICC Section Endpoints
@router.get("/icc-sections/{section_id}", response_model=schemas.ICCSection)
def get_icc_section(section_id: int, db: Session = Depends(get_db)):
    """Get a specific ICC section by ID."""
    db_section = crud.get_icc_section(db, section_id=section_id)
    if db_section is None:
        raise HTTPException(status_code=404, detail="ICC section not found")
    return db_section


@router.post("/icc-sections", response_model=schemas.ICCSection, status_code=201)
def create_icc_section(
    icc_section: schemas.ICCSectionCreate,
    db: Session = Depends(get_db)
):
    """Create a new ICC section."""
    # Verify document exists
    doc = crud.get_icc_document(db, document_id=icc_section.document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="ICC document not found")
    return crud.create_icc_section(db, icc_section=icc_section)


# Mapping Endpoints
@router.post("/mappings", response_model=schemas.CSIICCMapping, status_code=201)
def create_mapping(
    mapping: schemas.CSIICCMappingCreate,
    db: Session = Depends(get_db)
):
    """Create a new mapping between CSI code and ICC section."""
    # Verify both CSI code and ICC section exist
    csi = crud.get_csi_code_by_id(db, csi_id=mapping.csi_code_id)
    if not csi:
        raise HTTPException(status_code=404, detail="CSI code not found")

    icc_section = crud.get_icc_section(db, section_id=mapping.icc_section_id)
    if not icc_section:
        raise HTTPException(status_code=404, detail="ICC section not found")

    return crud.create_mapping(db, mapping=mapping)


# Search Endpoint
@router.post("/search", response_model=schemas.SearchResult)
def search_codes(search_req: schemas.SearchRequest, db: Session = Depends(get_db)):
    """
    Search for ICC sections based on CSI code.

    First checks for existing manual mappings, then falls back to
    keyword-based matching if no mappings exist.

    Supports filtering by state, year, and ICC document type.
    """
    # Try to get existing mapped results
    result = crud.search_csi_to_icc(
        db,
        csi_code=search_req.csi_code,
        state=search_req.state,
        year=search_req.year,
        icc_document=search_req.icc_document
    )

    if result is None:
        raise HTTPException(status_code=404, detail="CSI code not found")

    # If no existing mappings, use keyword matching
    if len(result.get("icc_sections", [])) == 0:
        from app.keyword_matcher import KeywordMatcher
        from app.models import CSICode

        # Get the CSI code object
        csi_code_obj = db.query(CSICode).filter(
            CSICode.code == search_req.csi_code
        ).first()

        if csi_code_obj:
            try:
                # Initialize keyword matcher
                matcher = KeywordMatcher()
                matcher.initialize(
                    db,
                    icc_document_code=search_req.icc_document  # Filter by document if specified
                )

                # Find matches
                matches = matcher.find_matches(
                    csi_code_obj,
                    top_n=10,
                    min_score=0.1
                )

                # Convert matches to ICC sections with metadata
                suggested_sections = []
                for match in matches:
                    section = match['section']
                    # Manually load the document relationship if not already loaded
                    from app.models import ICCDocument
                    if not hasattr(section, 'document') or section.document is None:
                        section.document = db.query(ICCDocument).filter(
                            ICCDocument.id == section.document_id
                        ).first()

                    suggested_sections.append(section)

                result["icc_sections"] = suggested_sections
                result["total_results"] = len(suggested_sections)
                result["source"] = "keyword_matching"

            except Exception as e:
                # If keyword matching fails, just return empty results
                print(f"Keyword matching failed: {e}")
                result["source"] = "no_mappings"
        else:
            result["source"] = "no_mappings"
    else:
        result["source"] = "manual_mappings"

    return result


# State Amendment Endpoints
@router.post("/state-amendments", response_model=schemas.StateAmendment, status_code=201)
def create_state_amendment(
    amendment: schemas.StateAmendmentCreate,
    db: Session = Depends(get_db)
):
    """Create a new state amendment for an ICC section."""
    # Verify section exists
    section = crud.get_icc_section(db, section_id=amendment.icc_section_id)
    if not section:
        raise HTTPException(status_code=404, detail="ICC section not found")

    return crud.create_state_amendment(db, amendment=amendment)


@router.get("/icc-sections/{section_id}/amendments", response_model=List[schemas.StateAmendment])
def get_section_amendments(
    section_id: int,
    state: Optional[str] = Query(None, description="Filter by state"),
    db: Session = Depends(get_db)
):
    """Get all amendments for a specific ICC section."""
    # Verify section exists
    section = crud.get_icc_section(db, section_id=section_id)
    if not section:
        raise HTTPException(status_code=404, detail="ICC section not found")

    return crud.get_amendments_for_section(db, section_id=section_id, state=state)
