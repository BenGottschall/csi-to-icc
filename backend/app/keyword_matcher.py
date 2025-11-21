"""
Keyword-based CSI to ICC Code Matching

This module provides keyword-based similarity matching between CSI MasterFormat codes
and ICC code sections. Uses TF-IDF vectorization and cosine similarity for ranking.

This serves as the baseline matching system and can be enhanced with LLM-based
approaches later. See MAPPING_STRATEGIES.md for details.
"""

from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from .models import CSICode, ICCSection, ICCDocument


class KeywordMatcher:
    """
    Keyword-based matcher for finding relevant ICC sections for CSI codes.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            ngram_range=(1, 3),  # Capture 1-3 word phrases
            max_features=5000
        )
        self.icc_sections = []
        self.icc_vectors = None

    def initialize(self, db: Session, icc_document_code: str = None):
        """
        Load ICC sections and build TF-IDF vectors.

        Args:
            db: Database session
            icc_document_code: Optional filter (e.g., "IPC" for plumbing only)
        """
        # Load ICC sections
        query = db.query(ICCSection).join(ICCDocument)

        if icc_document_code:
            query = query.filter(ICCDocument.code == icc_document_code)

        self.icc_sections = query.all()

        if not self.icc_sections:
            raise ValueError("No ICC sections found in database")

        # Build text corpus from ICC sections
        icc_texts = [
            self._create_searchable_text(section)
            for section in self.icc_sections
        ]

        # Create TF-IDF vectors
        self.icc_vectors = self.vectorizer.fit_transform(icc_texts)

        print(f"✓ Initialized keyword matcher with {len(self.icc_sections)} ICC sections")

    def _create_searchable_text(self, section: ICCSection) -> str:
        """
        Create searchable text from ICC section by combining title and description.
        """
        parts = []

        # Section number and title are most important
        if section.section_number:
            parts.append(section.section_number)
        if section.title:
            parts.append(section.title)
            parts.append(section.title)  # Repeat for higher weight

        # Description provides context
        if section.description:
            parts.append(section.description)

        # Chapter for categorization
        if section.chapter:
            parts.append(f"chapter {section.chapter}")

        return " ".join(parts)

    def find_matches(
        self,
        csi_code: CSICode,
        top_n: int = 10,
        min_score: float = 0.1
    ) -> List[Dict]:
        """
        Find top matching ICC sections for a CSI code.

        Args:
            csi_code: CSI code object to find matches for
            top_n: Number of top results to return
            min_score: Minimum similarity score (0-1)

        Returns:
            List of dicts with 'section', 'score', and 'matched_keywords'
        """
        if self.icc_vectors is None:
            raise RuntimeError("Matcher not initialized. Call initialize() first.")

        # Create search query from CSI code
        query_text = self._create_csi_query(csi_code)

        # Vectorize query
        query_vector = self.vectorizer.transform([query_text])

        # Calculate cosine similarity
        similarities = cosine_similarity(query_vector, self.icc_vectors)[0]

        # Get top N indices
        top_indices = np.argsort(similarities)[::-1][:top_n]

        # Build results
        results = []
        for idx in top_indices:
            score = similarities[idx]

            # Skip low-scoring matches
            if score < min_score:
                continue

            section = self.icc_sections[idx]

            # Find matched keywords for explanation
            matched_keywords = self._find_matched_keywords(
                query_text,
                self._create_searchable_text(section)
            )

            results.append({
                'section': section,
                'score': float(score),
                'matched_keywords': matched_keywords,
                'confidence': self._score_to_confidence(score)
            })

        return results

    def _create_csi_query(self, csi_code: CSICode) -> str:
        """
        Create search query from CSI code.
        """
        parts = []

        # Code itself
        if csi_code.code:
            parts.append(csi_code.code)

        # Title is most important - repeat for weight
        if csi_code.title:
            parts.append(csi_code.title)
            parts.append(csi_code.title)
            parts.append(csi_code.title)

        # Description
        if csi_code.description:
            parts.append(csi_code.description)

        return " ".join(parts)

    def _find_matched_keywords(self, query: str, text: str) -> List[str]:
        """
        Find overlapping keywords between query and text.
        """
        # Simple keyword extraction (can be enhanced)
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())

        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        query_words -= stop_words
        text_words -= stop_words

        # Find overlap
        matched = query_words & text_words

        # Sort by length (longer words are more meaningful)
        return sorted(matched, key=len, reverse=True)[:5]

    def _score_to_confidence(self, score: float) -> str:
        """
        Convert similarity score to confidence level.
        """
        if score >= 0.5:
            return "high"
        elif score >= 0.3:
            return "medium"
        elif score >= 0.15:
            return "low"
        else:
            return "very_low"


def create_keyword_mappings(
    db: Session,
    csi_code: CSICode,
    matches: List[Dict],
    relevance_map: Dict[str, str] = None
) -> int:
    """
    Create CSI-ICC mappings from keyword match results.

    Args:
        db: Database session
        csi_code: CSI code to create mappings for
        matches: List of match dicts from KeywordMatcher
        relevance_map: Optional dict mapping confidence to relevance level

    Returns:
        Number of mappings created
    """
    from .models import CSIICCMapping
    from datetime import datetime

    if relevance_map is None:
        relevance_map = {
            'high': 'primary',
            'medium': 'secondary',
            'low': 'reference',
            'very_low': 'reference'
        }

    created = 0

    for match in matches:
        section = match['section']
        confidence = match['confidence']
        score = match['score']
        keywords = match['matched_keywords']

        # Determine relevance based on confidence
        relevance = relevance_map.get(confidence, 'reference')

        # Check if mapping already exists
        existing = db.query(CSIICCMapping).filter(
            CSIICCMapping.csi_code_id == csi_code.id,
            CSIICCMapping.icc_section_id == section.id
        ).first()

        if existing:
            continue  # Skip duplicates

        # Create mapping
        mapping = CSIICCMapping(
            csi_code_id=csi_code.id,
            icc_section_id=section.id,
            relevance=relevance,
            notes=f"Auto-generated via keyword matching (score: {score:.3f}, keywords: {', '.join(keywords[:3])})",
            created_at=datetime.utcnow()
        )

        db.add(mapping)
        created += 1

    if created > 0:
        db.commit()

    return created
