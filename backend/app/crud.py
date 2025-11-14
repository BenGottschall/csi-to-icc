"""
CRUD operations for database models.
"""
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from . import models, schemas


# CSI Code CRUD
def get_csi_code(db: Session, code: str) -> Optional[models.CSICode]:
    """Get a CSI code by its code string."""
    return db.query(models.CSICode).filter(models.CSICode.code == code).first()


def get_csi_code_by_id(db: Session, csi_id: int) -> Optional[models.CSICode]:
    """Get a CSI code by its ID."""
    return db.query(models.CSICode).filter(models.CSICode.id == csi_id).first()


def get_csi_codes(db: Session, skip: int = 0, limit: int = 100) -> List[models.CSICode]:
    """Get a list of CSI codes."""
    return db.query(models.CSICode).offset(skip).limit(limit).all()


def get_csi_codes_by_division(db: Session, division: int) -> List[models.CSICode]:
    """Get all CSI codes in a specific division."""
    return db.query(models.CSICode).filter(models.CSICode.division == division).all()


def create_csi_code(db: Session, csi_code: schemas.CSICodeCreate) -> models.CSICode:
    """Create a new CSI code."""
    db_csi_code = models.CSICode(**csi_code.model_dump())
    db.add(db_csi_code)
    db.commit()
    db.refresh(db_csi_code)
    return db_csi_code


# ICC Document CRUD
def get_icc_document(db: Session, document_id: int) -> Optional[models.ICCDocument]:
    """Get an ICC document by ID."""
    return db.query(models.ICCDocument).filter(models.ICCDocument.id == document_id).first()


def get_icc_documents(
    db: Session,
    code: Optional[str] = None,
    year: Optional[int] = None,
    state: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[models.ICCDocument]:
    """Get ICC documents with optional filtering."""
    query = db.query(models.ICCDocument)

    if code:
        query = query.filter(models.ICCDocument.code == code)
    if year:
        query = query.filter(models.ICCDocument.year == year)
    if state:
        query = query.filter(models.ICCDocument.state == state)

    return query.offset(skip).limit(limit).all()


def create_icc_document(db: Session, icc_doc: schemas.ICCDocumentCreate) -> models.ICCDocument:
    """Create a new ICC document."""
    db_icc_doc = models.ICCDocument(**icc_doc.model_dump())
    db.add(db_icc_doc)
    db.commit()
    db.refresh(db_icc_doc)
    return db_icc_doc


# ICC Section CRUD
def get_icc_section(db: Session, section_id: int) -> Optional[models.ICCSection]:
    """Get an ICC section by ID."""
    return db.query(models.ICCSection).filter(models.ICCSection.id == section_id).first()


def get_icc_sections_by_document(db: Session, document_id: int) -> List[models.ICCSection]:
    """Get all sections for a specific ICC document."""
    return db.query(models.ICCSection).filter(
        models.ICCSection.document_id == document_id
    ).all()


def create_icc_section(db: Session, icc_section: schemas.ICCSectionCreate) -> models.ICCSection:
    """Create a new ICC section."""
    db_icc_section = models.ICCSection(**icc_section.model_dump())
    db.add(db_icc_section)
    db.commit()
    db.refresh(db_icc_section)
    return db_icc_section


# Mapping CRUD
def create_mapping(db: Session, mapping: schemas.CSIICCMappingCreate) -> models.CSIICCMapping:
    """Create a new CSI to ICC mapping."""
    db_mapping = models.CSIICCMapping(**mapping.model_dump())
    db.add(db_mapping)
    db.commit()
    db.refresh(db_mapping)
    return db_mapping


def get_icc_sections_for_csi_code(
    db: Session,
    csi_code: str,
    state: Optional[str] = None,
    year: Optional[int] = None,
    icc_document: Optional[str] = None
) -> List[models.ICCSection]:
    """
    Get all ICC sections mapped to a CSI code with optional filtering.
    """
    # Start with base query joining all necessary tables
    query = db.query(models.ICCSection).join(
        models.CSIICCMapping,
        models.CSIICCMapping.icc_section_id == models.ICCSection.id
    ).join(
        models.CSICode,
        models.CSIICCMapping.csi_code_id == models.CSICode.id
    ).join(
        models.ICCDocument,
        models.ICCSection.document_id == models.ICCDocument.id
    ).filter(
        models.CSICode.code == csi_code
    ).options(
        joinedload(models.ICCSection.document)
    )

    # Apply filters
    if state:
        query = query.filter(models.ICCDocument.state == state)
    if year:
        query = query.filter(models.ICCDocument.year == year)
    if icc_document:
        query = query.filter(models.ICCDocument.code == icc_document)

    return query.all()


def search_csi_to_icc(
    db: Session,
    csi_code: str,
    state: Optional[str] = None,
    year: Optional[int] = None,
    icc_document: Optional[str] = None
) -> Optional[dict]:
    """
    Search for ICC sections based on CSI code with filters.
    Returns a dictionary with CSI code info and related ICC sections.
    """
    # Get the CSI code
    csi = get_csi_code(db, csi_code)
    if not csi:
        return None

    # Get related ICC sections
    icc_sections = get_icc_sections_for_csi_code(
        db, csi_code, state, year, icc_document
    )

    return {
        "csi_code": csi,
        "icc_sections": icc_sections,
        "total_results": len(icc_sections)
    }


# State Amendment CRUD
def create_state_amendment(
    db: Session,
    amendment: schemas.StateAmendmentCreate
) -> models.StateAmendment:
    """Create a new state amendment."""
    db_amendment = models.StateAmendment(**amendment.model_dump())
    db.add(db_amendment)
    db.commit()
    db.refresh(db_amendment)
    return db_amendment


def get_amendments_for_section(
    db: Session,
    section_id: int,
    state: Optional[str] = None
) -> List[models.StateAmendment]:
    """Get amendments for a specific ICC section, optionally filtered by state."""
    query = db.query(models.StateAmendment).filter(
        models.StateAmendment.icc_section_id == section_id
    )

    if state:
        query = query.filter(models.StateAmendment.state == state)

    return query.all()
