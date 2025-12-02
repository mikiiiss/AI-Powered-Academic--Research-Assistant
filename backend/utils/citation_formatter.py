# backend/utils/citation_formatter.py
"""
Citation formatting utility for multiple citation styles
Supports APA, MLA, IEEE, Harvard, Chicago
"""
from typing import Dict, Optional, List
from datetime import datetime

class CitationFormatter:
    """Format citations in various academic styles"""
    
    SUPPORTED_STYLES = ['APA', 'MLA', 'IEEE', 'HARVARD', 'CHICAGO', 'INLINE']
    
    @staticmethod
    def format_citation(
        paper: Dict,
        style: str = 'APA'
    ) -> str:
        """Format a single paper citation
        
        Args:
            paper: Paper dict with title, authors, year, venue
            style: Citation style (APA, MLA, IEEE, etc.)
            
        Returns:
            Formatted citation string
        """
        style = style.upper()
        
        if style == 'APA':
            return CitationFormatter._format_apa(paper)
        elif style == 'MLA':
            return CitationFormatter._format_mla(paper)
        elif style == 'IEEE':
            return CitationFormatter._format_ieee(paper)
        elif style == 'HARVARD':
            return CitationFormatter._format_harvard(paper)
        elif style == 'CHICAGO':
            return CitationFormatter._format_chicago(paper)
        elif style == 'INLINE':
            return CitationFormatter._format_inline(paper)
        else:
            return CitationFormatter._format_apa(paper)  # Default to APA
    
    @staticmethod
    def _format_apa(paper: Dict) -> str:
        """APA style: Author, A. A. (Year). Title. Journal, volume(issue), pages."""
        authors = CitationFormatter._format_authors(paper.get('authors', 'Unknown'), style='APA')
        year = CitationFormatter._extract_year(paper)
        title = paper.get('title', 'Untitled')
        venue = paper.get('venue', 'Unpublished')
        
        return f"{authors} ({year}). {title}. {venue}."
    
    @staticmethod
    def _format_mla(paper: Dict) -> str:
        """MLA style: Author. "Title." Journal, Year."""
        authors = CitationFormatter._format_authors(paper.get('authors', 'Unknown'), style='MLA')
        year = CitationFormatter._extract_year(paper)
        title = paper.get('title', 'Untitled')
        venue = paper.get('venue', 'Unpublished')
        
        return f'{authors}. "{title}." {venue}, {year}.'
    
    @staticmethod
    def _format_ieee(paper: Dict) -> str:
        """IEEE style: [1] A. Author, "Title," Journal, Year."""
        authors = CitationFormatter._format_authors(paper.get('authors', 'Unknown'), style='IEEE')
        year = CitationFormatter._extract_year(paper)
        title = paper.get('title', 'Untitled')
        venue = paper.get('venue', 'Unpublished')
        
        return f'{authors}, "{title}," {venue}, {year}.'
    
    @staticmethod
    def _format_harvard(paper: Dict) -> str:
        """Harvard style: Author, A. (Year) Title. Journal."""
        authors = CitationFormatter._format_authors(paper.get('authors', 'Unknown'), style='HARVARD')
        year = CitationFormatter._extract_year(paper)
        title = paper.get('title', 'Untitled')
        venue = paper.get('venue', 'Unpublished')
        
        return f"{authors} ({year}) {title}. {venue}."
    
    @staticmethod
    def _format_chicago(paper: Dict) -> str:
        """Chicago style: Author. Title. Journal Year."""
        authors = CitationFormatter._format_authors(paper.get('authors', 'Unknown'), style='CHICAGO')
        year = CitationFormatter._extract_year(paper)
        title = paper.get('title', 'Untitled')
        venue = paper.get('venue', 'Unpublished')
        
        return f"{authors}. {title}. {venue} {year}."
    
    @staticmethod
    def _format_inline(paper: Dict) -> str:
        """Inline style: [Author et al., Year]"""
        authors = paper.get('authors', 'Unknown')
        year = CitationFormatter._extract_year(paper)
        
        # Get first author's last name
        if isinstance(authors, list) and len(authors) > 0:
            first_author = authors[0].split()[-1]  # Get last name
            if len(authors) > 1:
                return f"[{first_author} et al., {year}]"
            else:
                return f"[{first_author}, {year}]"
        elif isinstance(authors, str):
            # Parse string of authors
            author_list = authors.split(',')[0].strip()
            first_author = author_list.split()[-1] if author_list else 'Unknown'
            return f"[{first_author} et al., {year}]"
        else:
            return f"[Unknown, {year}]"
    
    @staticmethod
    def _format_authors(authors, style: str = 'APA') -> str:
        """Format author names according to style"""
        if isinstance(authors, list):
            if len(authors) == 0:
                return "Unknown"
            elif len(authors) == 1:
                return authors[0]
            elif len(authors) == 2:
                return f"{authors[0]} & {authors[1]}"
            else:
                return f"{authors[0]} et al."
        elif isinstance(authors, str):
            # Parse string of authors
            author_list = [a.strip() for a in authors.split(',') if a.strip()]
            if len(author_list) == 0:
                return "Unknown"
            elif len(author_list) == 1:
                return author_list[0]
            elif len(author_list) == 2:
                return f"{author_list[0]} & {author_list[1]}"
            else:
                return f"{author_list[0]} et al."
        else:
            return "Unknown"
    
    @staticmethod
    def _extract_year(paper: Dict) -> str:
        """Extract publication year from paper"""
        # Try published_date first
        if 'published_date' in paper and paper['published_date']:
            pub_date = paper['published_date']
            if hasattr(pub_date, 'year'):
                return str(pub_date.year)
            elif isinstance(pub_date, str):
                try:
                    return pub_date.split('-')[0]  # YYYY-MM-DD format
                except:
                    pass
        
        # Try year field
        if 'year' in paper and paper['year']:
            return str(paper['year'])
        
        return 'n.d.'  # No date
    
    @staticmethod
    def generate_bibliography(
        papers: List[Dict],
        style: str = 'APA'
    ) -> str:
        """Generate complete bibliography
        
        Args:
            papers: List of paper dicts
            style: Citation style
            
        Returns:
            Formatted bibliography string
        """
        citations = []
        for i, paper in enumerate(papers, 1):
            if style.upper() == 'IEEE':
                citation = f"[{i}] {CitationFormatter.format_citation(paper, style)}"
            else:
                citation = CitationFormatter.format_citation(paper, style)
            citations.append(citation)
        
        return "\n\n".join(citations)
