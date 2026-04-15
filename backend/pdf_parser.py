import pdfplumber
import re
from typing import List, Dict, Tuple

EPIC_PATTERNS = (
    re.compile(r'\b[A-Z]{3}\d{7}\b'),
    re.compile(r'\b[A-Z]{2}\d{2}[A-Z0-9]{7}\b'),
)
ENTRY_START_PATTERN = re.compile(r'^\d{1,4}$')
PART_NUMBER_PATTERN = re.compile(r'(?i)\b(?:part|booth|polling(?:\s+station)?)\s*no\.?\s*[:\-]?\s*(\d+)\b')
CARD_ENTRY_PATTERN = re.compile(
    r'(?is)(?:^|\n)\s*(\d{1,4})\s+'
    r'([A-Z]{3}\d{7}|[A-Z]{2}\d{2}[A-Z0-9]{7})\s+'
    r'Name\s*:\s*([^:\n]+?)\s+'
    r'(?:Father\s+Name|Husband\s+Name|Mother\s+Name|Wife\s+Name|House\s+Number|Age)\b'
)

class VoterPDFParser:
    """Parser for voter list PDFs"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.voters = []
        self.booths = set()
        self.seen_voter_ids = set()
    
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
        current_booth = self._extract_part_number(text)

        # First try the actual electoral-roll card format.
        if self._parse_card_entries(text, current_booth):
            return

        current_serial = None
        current_voter_id = None
        current_name = None

        for raw_line in lines:
            line = raw_line.strip()
            normalized = self._normalize_line(line)
            line = line.strip()
            if not line:
                continue
            
            # Look for booth information (common patterns)
            if 'booth' in line.lower() or 'polling' in line.lower():
                # Try to extract booth number
                booth_match = re.search(r'(?:[Bb]ooth|[Pp]olling(?:\s+[Ss]tation)?)\s*(?:[Nn]o\.?|[:\-])?\s*(\d+)', line)
                if booth_match:
                    current_booth = booth_match.group(1)

            part_match = PART_NUMBER_PATTERN.search(line)
            if part_match:
                current_booth = part_match.group(1)

            if ENTRY_START_PATTERN.match(normalized):
                self._append_if_complete(current_name, current_voter_id, current_booth)
                current_serial = normalized
                current_voter_id = None
                current_name = None
                continue

            epic_match = self._extract_epic(normalized)
            if epic_match:
                current_voter_id = epic_match.group(0)

                # A compact single-line entry sometimes contains ID and Name.
                inline_name = self._extract_name_from_text_line(normalized, current_voter_id)
                if inline_name and inline_name != normalized:
                    current_name = inline_name

                self._append_if_complete(current_name, current_voter_id, current_booth)
                continue

            extracted_name = self._extract_name_from_label(normalized)
            if extracted_name:
                current_name = extracted_name
                self._append_if_complete(current_name, current_voter_id, current_booth)
                continue

            # Some PDFs output serial + voter ID on the same text line.
            serial_and_id_match = re.match(
                r'^(\d{1,4})\s+([A-Z]{3}\d{7}|[A-Z]{2}\d{2}[A-Z0-9]{7})\b',
                normalized
            )
            if serial_and_id_match:
                self._append_if_complete(current_name, current_voter_id, current_booth)
                current_serial = serial_and_id_match.group(1)
                current_voter_id = serial_and_id_match.group(2)
                current_name = self._extract_name_from_label(normalized)
                self._append_if_complete(current_name, current_voter_id, current_booth)
    
    def _extract_voter_from_row(self, row: list) -> Dict or None:
        """Extract voter information from a table row"""
        try:
            voter_info = {}
            clean_row = [str(cell).strip() if cell else '' for cell in row]
            identified_cells = []

            # Pass 1: Identify unique patterns (EPIC, Booth)
            for i, cell in enumerate(clean_row):
                if not cell:
                    continue
                
                epic_match = self._extract_epic(cell)
                if epic_match and 'voter_id' not in voter_info:
                    voter_info['voter_id'] = epic_match.group(0)
                    identified_cells.append(cell)
                    continue

                if re.match(r'^\d+$', cell) and 'booth_number' not in voter_info:
                    voter_info['booth_number'] = cell
                    identified_cells.append(cell)
                    continue

            # Pass 2: Identify name (longest alphabetic string)
            name_candidate = ''
            for cell in clean_row:
                if cell not in identified_cells and re.search(r'[A-Za-z]{3,}', cell) and not self._looks_like_label(cell):
                    if len(cell) > len(name_candidate):
                        name_candidate = cell
            if name_candidate:
                voter_info['voter_name'] = name_candidate
                identified_cells.append(name_candidate)

            # Pass 3: The remaining cell is likely the house number
            for cell in clean_row:
                if cell and cell not in identified_cells and not self._looks_like_label(cell):
                    if 'house_number' not in voter_info:
                        voter_info['house_number'] = cell
                        break

            if self._is_valid_voter(voter_info):
                if self._is_duplicate_voter(voter_info['voter_id']):
                    return None
                self.seen_voter_ids.add(voter_info['voter_id'])
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

    def _parse_card_entries(self, text: str, booth_number: str | None) -> bool:
        """Parse electoral-roll card layouts like serial + voter ID + Name."""
        matches = list(CARD_ENTRY_PATTERN.finditer(text))
        if not matches or not booth_number:
            return False

        found = False
        for match in matches:
            voter_info = {
                'voter_name': self._clean_name(match.group(3)),
                'voter_id': match.group(2),
                'booth_number': booth_number,
            }
            if self._is_valid_voter(voter_info) and not self._is_duplicate_voter(voter_info['voter_id']):
                self.voters.append(voter_info)
                self.booths.add(booth_number)
                self.seen_voter_ids.add(voter_info['voter_id'])
                found = True
        return found

    def _append_if_complete(self, voter_name: str | None, voter_id: str | None, booth_number: str | None, house_number: str | None = None):
        """Append a voter only when the three required fields are present."""
        if not (voter_name and voter_id and booth_number):
            return

        voter_info = {
            'voter_name': self._clean_name(voter_name),
            'voter_id': voter_id,
            'booth_number': booth_number,
            'house_number': house_number,
        }
        if self._is_valid_voter(voter_info) and not self._is_duplicate_voter(voter_id):
            self.voters.append(voter_info)
            self.booths.add(booth_number)
            self.seen_voter_ids.add(voter_id)

    def _extract_part_number(self, text: str) -> str | None:
        """Use Part No. as the booth identifier for electoral-roll PDFs."""
        match = PART_NUMBER_PATTERN.search(text or '')
        return match.group(1) if match else None

    def _extract_name_from_label(self, value: str) -> str | None:
        """Extract the voter name from lines like 'Name : Rajkumar'."""
        match = re.search(r'(?i)\bName\s*:\s*([^\n]+)', value or '')
        if not match:
            return None

        name = match.group(1)
        name = re.split(
            r'(?i)\b(Father\s+Name|Husband\s+Name|Mother\s+Name|Wife\s+Name|House\s+Number|Age|Gender)\b',
            name,
            maxsplit=1
        )[0]
        return self._clean_name(name)

    def _normalize_line(self, value: str) -> str:
        """Normalize extracted PDF text for more reliable matching."""
        return re.sub(r'\s+', ' ', (value or '').strip())

    def _clean_name(self, value: str) -> str:
        """Remove labels and trailing metadata from extracted names."""
        cleaned = value or ''
        cleaned = re.sub(r'(?i)\bName\s*:\s*', '', cleaned)
        cleaned = re.sub(r'(?i)\b(ELECTOR PHOTO IDENTITY CARD|AVAILABLE)\b', ' ', cleaned)
        cleaned = re.sub(r'[^A-Za-z.\s]', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    def _is_duplicate_voter(self, voter_id: str) -> bool:
        return voter_id in self.seen_voter_ids

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
        cleaned = re.sub(r'(?i)\b(father\s*name|husband\s*name|mother\s*name|wife\s*name|gender|age|part\s*no)\b.*', ' ', cleaned)
        cleaned = re.sub(r'[:;,.\-_/]+', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return self._clean_name(cleaned)

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
