# from sqlalchemy import Column, String, Integer, Text, Date, DateTime
# from sqlalchemy.ext.declarative import declarative_base
# from datetime import datetime

# Base = declarative_base()

# class Paper(Base):
#     __tablename__ = "papers"

#     # Core columns
#     id = Column(String, primary_key=True)
#     title = Column(Text, nullable=False)
#     abstract = Column(Text)
#     authors = Column(String)  # Store as JSON string for now
#     published_date = Column(Date)  # Add this field
#     citation_count = Column(Integer, default=0)
#     venue = Column(String)
#     source = Column(String)
#     pdf_url = Column(String)
    
#     # Timestamps
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

#     def __repr__(self):
#         return f"<Paper(id='{self.id}', title='{self.title[:50]}...')>"


from sqlalchemy import Column, String, Integer, Text, Date, DateTime, ForeignKey, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Paper(Base):
    __tablename__ = "papers"

    # Core columns
    id = Column(String, primary_key=True)
    title = Column(Text, nullable=False)
    abstract = Column(Text)
    authors = Column(String)  # JSON string
    published_date = Column(Date)
    citation_count = Column(Integer, default=0)
    venue = Column(String)
    source = Column(String)
    pdf_url = Column(String)
    
    # Vector embeddings
    title_embedding = Column(JSONB)
    abstract_embedding = Column(JSONB)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    citations = relationship("PaperRelationship", 
                           foreign_keys="PaperRelationship.citing_paper_id",
                           back_populates="citing_paper")
    
    references = relationship("PaperRelationship",
                            foreign_keys="PaperRelationship.cited_paper_id", 
                            back_populates="cited_paper")

    def __repr__(self):
        return f"<Paper(id='{self.id}', title='{self.title[:50]}...')>"

class PaperRelationship(Base):
    __tablename__ = "paper_relationships"
    
    id = Column(Integer, primary_key=True)
    citing_paper_id = Column(String, ForeignKey('papers.id'))
    cited_paper_id = Column(String, ForeignKey('papers.id'))
    relationship_type = Column(String)  # 'cites', 'similar', 'same_venue'
    similarity_score = Column(Float)  # For semantic similarity
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    citing_paper = relationship("Paper", foreign_keys=[citing_paper_id], back_populates="citations")
    cited_paper = relationship("Paper", foreign_keys=[cited_paper_id], back_populates="references")