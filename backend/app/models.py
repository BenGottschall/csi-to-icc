"""
SQLAlchemy database models for CSI to ICC code mapping.
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class CSICode(Base):
    """CSI MasterFormat code model."""
    __tablename__ = "csi_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    division = Column(Integer, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)

    # Relationship to mappings
    mappings = relationship("CSIICCMapping", back_populates="csi_code")

    def __repr__(self):
        return f"<CSICode(code='{self.code}', title='{self.title}')>"


class ICCDocument(Base):
    """ICC Document model (e.g., IBC 2024, IRC 2021)."""
    __tablename__ = "icc_documents"
    __table_args__ = (
        UniqueConstraint('code', 'year', 'state', name='uix_code_year_state'),
    )

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), nullable=False, index=True)  # IBC, IRC, IFC, etc.
    year = Column(Integer, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    state = Column(String(50), index=True)  # NULL for model codes, or state abbreviation
    base_url = Column(Text, nullable=False)

    # Relationship to sections
    sections = relationship("ICCSection", back_populates="document")

    def __repr__(self):
        state_info = f", state='{self.state}'" if self.state else ""
        return f"<ICCDocument(code='{self.code}', year={self.year}{state_info})>"


class ICCSection(Base):
    """ICC Code section model."""
    __tablename__ = "icc_sections"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("icc_documents.id"), nullable=False)
    section_number = Column(String(50), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    chapter = Column(Integer, index=True)
    url = Column(Text, nullable=False)
    description = Column(Text)

    # Relationships
    document = relationship("ICCDocument", back_populates="sections")
    mappings = relationship("CSIICCMapping", back_populates="icc_section")
    amendments = relationship("StateAmendment", back_populates="icc_section")

    def __repr__(self):
        return f"<ICCSection(section_number='{self.section_number}', title='{self.title}')>"


class CSIICCMapping(Base):
    """Mapping between CSI codes and ICC sections."""
    __tablename__ = "csi_icc_mappings"
    __table_args__ = (
        UniqueConstraint('csi_code_id', 'icc_section_id', name='uix_csi_icc'),
    )

    id = Column(Integer, primary_key=True, index=True)
    csi_code_id = Column(Integer, ForeignKey("csi_codes.id"), nullable=False)
    icc_section_id = Column(Integer, ForeignKey("icc_sections.id"), nullable=False)
    relevance = Column(String(20))  # "primary", "secondary", "reference"
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    csi_code = relationship("CSICode", back_populates="mappings")
    icc_section = relationship("ICCSection", back_populates="mappings")

    def __repr__(self):
        return f"<CSIICCMapping(csi_code_id={self.csi_code_id}, icc_section_id={self.icc_section_id})>"


class StateAmendment(Base):
    """State-specific amendments to ICC sections."""
    __tablename__ = "state_amendments"

    id = Column(Integer, primary_key=True, index=True)
    icc_section_id = Column(Integer, ForeignKey("icc_sections.id"), nullable=False)
    state = Column(String(50), nullable=False, index=True)
    amendment_text = Column(Text)
    effective_date = Column(Date)

    # Relationship
    icc_section = relationship("ICCSection", back_populates="amendments")

    def __repr__(self):
        return f"<StateAmendment(state='{self.state}', section_id={self.icc_section_id})>"
