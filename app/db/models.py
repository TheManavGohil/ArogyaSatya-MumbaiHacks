from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import datetime

# Association table for Claims <-> RawContent (Many-to-Many)
claim_content_association = Table(
    "claim_content_association",
    Base.metadata,
    Column("claim_id", Integer, ForeignKey("canonical_claims.id")),
    Column("content_id", Integer, ForeignKey("raw_content.id")),
)

class RawContent(Base):
    """
    Stores raw ingested content (articles, tweets, transcripts).
    Short retention for full text, but metadata kept longer.
    """
    __tablename__ = "raw_content"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String, index=True) # e.g., "twitter", "bbc", "youtube"
    external_id = Column(String, index=True) # ID from the source platform
    url = Column(String, unique=True, index=True)
    content_type = Column(String) # "text", "image", "video"
    
    title = Column(String, nullable=True)
    text_content = Column(Text, nullable=True) # The raw text or transcript
    media_url = Column(String, nullable=True) # URL for image/video
    
    published_at = Column(DateTime(timezone=True))
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    claims = relationship("CanonicalClaim", secondary=claim_content_association, back_populates="sources")

class CanonicalClaim(Base):
    """
    Represents a unique, normalized claim.
    "5G causes COVID" and "COVID spread by 5G" map to one CanonicalClaim.
    """
    __tablename__ = "canonical_claims"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, unique=True, index=True) # The normalized claim text
    embedding_id = Column(String, nullable=True) # ID in vector DB
    
    # Classification
    status = Column(String, default="unverified") # unverified, true, false, misleading
    confidence_score = Column(Float, default=0.0)
    explanation = Column(Text)
    
    first_seen_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sources = relationship("RawContent", secondary=claim_content_association, back_populates="claims")
    evidence = relationship("ClaimEvidence", back_populates="claim")

class ClaimEvidence(Base):
    """
    Evidence items retrieved to verify a claim.
    """
    __tablename__ = "claim_evidence"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("canonical_claims.id"))
    
    source_url = Column(String)
    source_reliability = Column(String) # "high", "medium", "low"
    text_snippet = Column(Text)
    
    supports_claim = Column(Boolean, nullable=True) # True=Supports, False=Refutes, None=Neutral
    
    retrieved_at = Column(DateTime(timezone=True), server_default=func.now())
    
    claim = relationship("CanonicalClaim", back_populates="evidence")
