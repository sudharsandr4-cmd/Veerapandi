import pdfplumber
import re
from typing import List, Dict, Tuple

EPIC_PATTERNS = (
    re.compile(r'\b[A-Z]{3}\d{7}\b'),
    re.compile(r'\b[A-Z]{2}\d{2}[A-Z0-9]{7}\b'),
)

class VoterPDFParser:
    """Parser for voter list PDFs"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.voters = []
        self.booths = set()
    
    def parse(self) -> Tuple[List[Dict], set]:
        """
        Parse PDF and extract voter information
        Returns: (list of voters, set of booths)
        """
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page in pdf.pages:
                    try:
                        self._parse_page(page)
                    except Exception as page_error:
                        print(f"Skipping page {page.page_number}: {page_error}")
            return self.voters, self.booths
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return [], set()
    
    def _parse_page(self, page):
        """Parse individual page from PDF"""
        # Text extraction is much cheaper than table extraction and works for
        # most voter-roll PDFs. We only fall back to table extraction when text
        # extraction produced nothing on the current page.
        text = page.extract_text() or ''
        voters_before = len(self.voters)

        if text:
            self._parse_text(text)

        if len(self.voters) > voters_before:
            return

        tables = page.extract_tables() or []
        for table in tables:
            self._parse_table(table)
    
    def _parse_table(self, table):
        """Parse table structure from PDF"""
        if not table:
            return
        
        for row in table:
            if row and len(row) >= 3:
                # Try to extract voter info from row
                voter_info = self._extract_voter_from_row(row)
                if voter_info:
                    self.voters.append(voter_info)
                    self.booths.add(voter_info['booth_number'])
    
    def _parse_text(self, text: str):
        """Parse text content - pattern matching fallback"""
        lines = text.split('\n')
        
        current_booth = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for booth information (common patterns)
            if 'booth' in line.lower() or 'polling' in line.lower():
                # Try to extract booth number
                booth_match = re.search(r'(?:[Bb]ooth|[Pp]olling(?:\s+[Ss]tation)?)\s*(?:[Nn]o\.?|[:\-])?\s*(\d+)', line)
                if booth_match:
                    current_booth = booth_match.group(1)
            
            epic_match = self._extract_epic(line)
            
            if epic_match and current_booth:
                voter_id = epic_match.group(0)
                
                voter_name = self._extract_name_from_text_line(line, voter_id)

                voter_info = {
                    'voter_name': voter_name,
                    'voter_id': voter_id,
                    'booth_number': current_booth
                }

                if self._is_valid_voter(voter_info):
                    self.voters.append(voter_info)
                    self.booths.add(current_booth)
    
    def _extract_voter_from_row(self, row) -> Dict or None:
        """Extract voter information from a table row"""
        try:
            voter_info = {}
            
            # Clean row data
            clean_row = [str(cell).strip() if cell else '' for cell in row]
            
            # Look for patterns in row cells
            # Usually structure is: Booth | Voter ID | Name | Other columns
            
            # Initialize with all possible positions
            for i, cell in enumerate(clean_row):
                if not cell:
                    continue
                
                # Check if cell looks like a booth number (usually numeric)
                if re.match(r'^\d+$', cell):
                    if 'booth_number' not in voter_info:
                        voter_info['booth_number'] = cell
                
                # Check if cell looks like a voter ID (EPIC format)
                epic_match = self._extract_epic(cell)
                if epic_match:
                    voter_info['voter_id'] = epic_match.group(0)
                
                # Check if cell contains alphabetic characters (likely name)
                if re.search(r'[A-Za-z]{3,}', cell) and not self._looks_like_label(cell):
                    if 'voter_name' not in voter_info or len(cell) > len(voter_info.get('voter_name', '')):
                        voter_info['voter_name'] = cell
            
            # Return if we have the minimum required info
            if self._is_valid_voter(voter_info):
                return voter_info
            
            return None
        except Exception as e:
            print(f"Error extracting row: {e}")
            return None
    
    def _is_valid_voter(self, voter_info: Dict) -> bool:
        """Validate if voter information is complete"""
        required_fields = ['voter_name', 'voter_id', 'booth_number']
        
        # Check if all required fields exist
        for field in required_fields:
            if field not in voter_info or not voter_info[field]:
                return False
        
        # Validate voter ID format (EPIC number)
        voter_id = voter_info['voter_id']
        if not self._extract_epic(voter_id):
            return False
        
        # Validate name (at least 2 characters)
        if len(voter_info['voter_name']) < 2:
            return False
        
        # Validate booth number (should be numeric)
        if not voter_info['booth_number'].isdigit():
            return False
        
        return True

    def _extract_epic(self, value: str):
        """Return the first EPIC-style voter ID match from a string."""
        normalized = (value or '').strip().upper()
        for pattern in EPIC_PATTERNS:
            match = pattern.search(normalized)
            if match:
                return match
        return None

    def _extract_name_from_text_line(self, line: str, voter_id: str) -> str:
        """Best-effort name extraction for text-based PDFs."""
        cleaned = line.replace(voter_id, ' ')
        cleaned = re.sub(r'(?i)\b(voter\s*id|epic|name|serial\s*no|house\s*no)\b', ' ', cleaned)
        cleaned = re.sub(r'[:;,.\-_/]+', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    def _looks_like_label(self, value: str) -> bool:
        """Ignore common header or metadata cells when choosing the voter name."""
        normalized = value.strip().lower()
        return normalized in {
            'booth',
            'booth number',
            'booth no',
            'voter id',
            'epic',
            'epic number',
            'name',
            'serial no',
            'part no',
        }

def extract_voters_from_pdf(pdf_path: str) -> Tuple[List[Dict], set]:
    """
    Main function to extract voter data from PDF
    
    Args:
        pdf_path: Path to the voter list PDF
    
    Returns:
        Tuple of (voters list, booths set)
    """
    parser = VoterPDFParser(pdf_path)
    return parser.parse()
