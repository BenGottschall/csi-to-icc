"""
Pydantic schemas for API request/response validation.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, date


# CSI Code Schemas
class CSICodeBase(BaseModel):
    """Base schema for CSI code."""
    code: str = Field(..., description="CSI MasterFormat code (e.g., '03 30 00')")
    division: int = Field(..., description="CSI division number")
    title: str = Field(..., description="CSI code title")
    description: Optional[str] = Field(None, description="Detailed description")


class CSICodeCreate(CSICodeBase):
    """Schema for creating a new CSI code."""
    pass


class CSICode(CSICodeBase):
    """Schema for CSI code response."""
    id: int

    class Config:
        from_attributes = True


# ICC Document Schemas
class ICCDocumentBase(BaseModel):
    """Base schema for ICC document."""
    code: str = Field(..., description="ICC document code (e.g., 'IBC', 'IRC')")
    year: int = Field(..., description="Document year (e.g., 2021, 2024)")
    title: str = Field(..., description="Document title")
    state: Optional[str] = Field(None, description="State abbreviation (e.g., 'CO', 'NY') or NULL for model codes")
    base_url: str = Field(..., description="Base URL to ICC document")


class ICCDocumentCreate(ICCDocumentBase):
    """Schema for creating a new ICC document."""
    pass


class ICCDocument(ICCDocumentBase):
    """Schema for ICC document response."""
    id: int

    class Config:
        from_attributes = True


# ICC Section Schemas
class ICCSectionBase(BaseModel):
    """Base schema for ICC section."""
    section_number: str = Field(..., description="Section number (e.g., '1905.2')")
    title: str = Field(..., description="Section title")
    chapter: Optional[int] = Field(None, description="Chapter number")
    url: str = Field(..., description="Direct URL to section")
    description: Optional[str] = Field(None, description="Section description")


class ICCSectionCreate(ICCSectionBase):
    """Schema for creating a new ICC section."""
    document_id: int = Field(..., description="ID of the parent ICC document")


class ICCSection(ICCSectionBase):
    """Schema for ICC section response."""
    id: int
    document_id: int
    document: Optional[ICCDocument] = None

    class Config:
        from_attributes = True

    @field_validator('description', mode='before')
    @classmethod
    def truncate_description(cls, v: Optional[str]) -> Optional[str]:
        """Truncate description for copyright compliance."""
        if v is None:
            return None
        max_words = 12
        words = v.split()
        if len(words) <= max_words:
            return v
        return ' '.join(words[:max_words]) + '...'


# Mapping Schemas
class CSIICCMappingBase(BaseModel):
    """Base schema for CSI to ICC mapping."""
    relevance: Optional[str] = Field(None, description="Relevance level: 'primary', 'secondary', 'reference'")
    notes: Optional[str] = Field(None, description="Additional notes about the mapping")


class CSIICCMappingCreate(CSIICCMappingBase):
    """Schema for creating a new mapping."""
    csi_code_id: int
    icc_section_id: int


class CSIICCMapping(CSIICCMappingBase):
    """Schema for mapping response."""
    id: int
    csi_code_id: int
    icc_section_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# State Amendment Schemas
class StateAmendmentBase(BaseModel):
    """Base schema for state amendment."""
    state: str = Field(..., description="State abbreviation")
    amendment_text: Optional[str] = Field(None, description="Amendment text")
    effective_date: Optional[date] = Field(None, description="Date amendment became effective")


class StateAmendmentCreate(StateAmendmentBase):
    """Schema for creating a new state amendment."""
    icc_section_id: int


class StateAmendment(StateAmendmentBase):
    """Schema for state amendment response."""
    id: int
    icc_section_id: int

    class Config:
        from_attributes = True


# Combined Response Schemas
class ICCSectionWithDocument(ICCSection):
    """ICC Section with full document info."""
    document: ICCDocument


class CSICodeWithMappings(CSICode):
    """CSI Code with associated ICC sections."""
    icc_sections: List[ICCSectionWithDocument] = []


# Search Request Schema
class SearchRequest(BaseModel):
    """Schema for search request."""
    csi_code: str = Field(..., description="CSI code to search for")
    state: Optional[str] = Field(None, description="Filter by state")
    year: Optional[int] = Field(None, description="Filter by year")
    icc_document: Optional[str] = Field(None, description="Filter by ICC document type (e.g., 'IBC')")


# Search Response Schema
class SearchResult(BaseModel):
    """Schema for search results."""
    csi_code: CSICode
    icc_sections: List[ICCSectionWithDocument]
    total_results: int
    source: Optional[str] = Field(None, description="Source of results: 'manual_mappings', 'keyword_matching', or 'no_mappings'")
