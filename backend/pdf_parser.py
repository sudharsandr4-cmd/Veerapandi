import pdfplumber
import re
from typing import List, Dict, Tuple

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
                    self._parse_page(page)
            return self.voters, self.booths
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return [], set()
    
    def _parse_page(self, page):
        """Parse individual page from PDF"""
        # First, try to extract tables
        tables = page.extract_tables()
        
        if tables:
            for table in tables:
                self._parse_table(table)
        else:
            # Fallback to text extraction if no tables found
            text = page.extract_text()
            if text:
                self._parse_text(text)
    
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
                booth_match = re.search(r'[Bb]ooth\s*[:\-]?\s*(\d+)', line)
                if booth_match:
                    current_booth = booth_match.group(1)
            
            # Look for voter ID (EPIC number - typically alphanumeric)
            # Pattern: starts with state code (2 letters) + district + numbers
            epic_match = re.search(r'([A-Z]{2})\d{2}[A-Z0-9]{7}', line)
            
            if epic_match and current_booth:
                voter_id = epic_match.group(0)
                
                # Extract voter name (usually comes before or after EPIC)
                name_match = re.search(r'([A-Za-z\s]+)', line)
                if name_match:
                    voter_name = name_match.group(1).strip()
                    
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
                if re.match(r'^[A-Z]{2}\d{2}[A-Z0-9]{7}', cell):
                    voter_info['voter_id'] = cell
                
                # Check if cell contains alphabetic characters (likely name)
                if re.search(r'[A-Za-z]{3,}', cell):
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
        if not re.match(r'^[A-Z]{2}\d{2}[A-Z0-9]{7}$', voter_id):
            return False
        
        # Validate name (at least 2 characters)
        if len(voter_info['voter_name']) < 2:
            return False
        
        # Validate booth number (should be numeric)
        if not voter_info['booth_number'].isdigit():
            return False
        
        return True

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
