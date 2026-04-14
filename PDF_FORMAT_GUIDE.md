# PDF Format Guide for Voter Data Management System

This document explains the PDF formats supported for voter list uploads.

## Overview

The system supports PDFs with voter information in either **table format** or **text format**. The system will attempt to parse the PDF and extract:
1. **Voter Name** - Full name of the voter
2. **Voter ID (EPIC)** - Electoral Photo Identity Card number
3. **Booth Number** - Polling booth assignment

---

## Format 1: Table Format (RECOMMENDED)

### Description
The most reliable format consists of a table with clear columns.

### Table Structure

The table should have at least 3 columns containing:

| Column | Content | Format |
|--------|---------|--------|
| Column 1 | Booth Number | Numeric (e.g., "001", "42") |
| Column 2 | Voter ID (EPIC) | `KKDDSSSSSS` (e.g., "KA01A0001234") |
| Column 3 | Voter Name | Text (e.g., "John Smith") |

### Column Order
The parser looks for content in any column order. The system identifies each column by its content type:
- **Numeric-only** = Booth Number
- **Alphanumeric KKDDSSSSSS format** = Voter ID
- **Alphabetic text** = Voter Name

### Example Table

```
┌─────────────────────────────────────────────────────────────┐
│ Booth | EPIC ID       | Voter Name         | Gender | Age  │
├─────────────────────────────────────────────────────────────┤
│ 001   | KA01A0001234  | JOHN SMITH         | M      | 42   │
│ 001   | KA01A0001235  | JANE ELIZABETH     | F      | 38   │
│ 002   | KA01A0002001  | ROBERT JOHNSON     | M      | 55   │
│ 002   | KA01A0002002  | MARIA GARCIA       | F      | 45   │
│ 003   | KA01A0003100  | WILLIAM BROWN      | M      | 67   │
└─────────────────────────────────────────────────────────────┘
```

### Column Variations

The system recognizes these column header variations:
- Booth Number: "Booth", "Booth#", "Booth Number", "Polling Booth"
- Voter ID: "ID", "EPIC", "EPIC ID", "Voter ID", "Election ID"
- Voter Name: "Name", "Voter Name", "Full Name", "Full Name of Voter"

**Additional columns are ignored**, so you can include extra information.

### Benefits
✅ Most accurate extraction
✅ Fast parsing
✅ Tolerates extra columns
✅ Works with different column orders

---

## Format 2: Text Format

### Description
If tables aren't available, the system can parse structured text.

### Text Pattern

Each voter should be represented similarly to one of these patterns:

**Pattern A** (Booth label followed by voters):
```
Booth: 001
Voter: KA01A0001234, Name: John Smith
Voter: KA01A0001235, Name: Jane Elizabeth

Booth: 002
Voter: KA01A0002001, Name: Robert Johnson
```

**Pattern B** (Comma-separated):
```
001, KA01A0001234, John Smith
001, KA01A0001235, Jane Elizabeth
002, KA01A0002001, Robert Johnson
```

**Pattern C** (Space-separated):
```
001 KA01A0001234 John Smith
001 KA01A0001235 Jane Elizabeth
002 KA01A0002001 Robert Johnson
```

**Pattern D** (Dash-separated):
```
001 - KA01A0001234 - John Smith
001 - KA01A0001235 - Jane Elizabeth
002 - KA01A0002001 - Robert Johnson
```

### Benefits
✓ Works with simple PDFs
✓ No table structure needed
✓ Can extract from scanned documents (with OCR)

### Limitations
- Less accurate than table format
- Sensitive to line breaks
- May not handle all variations

---

## Voter ID (EPIC) Format Specification

### EPIC Format
```
KKDDSSSSSS
```

Where:
- **KK** = State Code (2 uppercase letters)
- **DD** = District Code (2 digits: 01-99)
- **S** = Additional identifier (1 letter or digit)
- **SSSSS** = Serial number (remaining alphanumeric characters)

### Valid State Codes
```
AP - Andhra Pradesh      | GJ - Gujarat         | MH - Maharashtra
AR - Arunachal Pradesh   | HR - Haryana         | ML - Meghalaya
AS - Assam               | HP - Himachal Pradesh| MN - Manipur
BR - Bihar               | JK - Jammu & Kashmir | MZ - Mizoram
CG - Chhattisgarh        | JH - Jharkhand       | NL - Nagaland
CH - Chandigarh          | KA - Karnataka       | OD - Odisha
DD - Dadra & Nagar Haveli | KL - Kerala         | PB - Punjab
DL - Delhi               | LA - Ladakh          | RJ - Rajasthan
DN - Daman & Diu         | LD - Lakshadweep     | SK - Sikkim
GA - Goa                 | MP - Madhya Pradesh  | TN - Tamil Nadu
                         |                      | TR - Tripura
                         |                      | UP - Uttar Pradesh
                         |                      | UT - Uttarakhand
                         |                      | WB - West Bengal
```

### Examples
```
KA01A0001234 - Karnataka, District 01
TN02B0050678 - Tamil Nadu, District 02
UP15C0125999 - Uttar Pradesh, District 15
```

### Invalid Examples
```
123456789 - No state code
KAAA123456 - Invalid format
KA1A123456 - Missing district digits
KA01123456 - Missing letter/digit identifier
```

---

## Creating Test PDFs

### Using Microsoft Word
1. Create a table with columns: Booth, EPIC ID, Voter Name
2. Fill with sample data
3. Save as PDF (File → Save As → PDF)

### Using LibreOffice Calc
1. Create spreadsheet with columns
2. Fill data
3. Export as PDF (File → Export as PDF)

### Using Google Sheets
1. Create sheet with columns
2. Go to File → Download → PDF Document
3. Download as PDF

### Example Data to Use
```
Booth: 001
EPIC ID: KA01A0001001
Name: Rajesh Kumar

Booth: 001
EPIC ID: KA01A0001002
Name: Priya Singh

Booth: 002
EPIC ID: KA01A0002001
Name: Amit Patel

Booth: 002
EPIC ID: KA01A0002002
Name: Deepa Sharma
```

---

## File Requirements

### File Type
- ✅ PDF format (.pdf)
- ❌ JPEG, PNG, Word, Excel (not supported)

### File Size
- ✅ Maximum 50MB
- ❌ Files larger than 50MB (will be rejected)

### Content
- ✅ Clear, readable text
- ✅ Structured layout (table or formatted text)
- ✅ Valid voter IDs in EPIC format
- ❌ Scanned images without OCR (will not parse correctly)
- ❌ Encrypted or password-protected PDFs

### Quality
- ✅ High quality (readable text)
- ✅ Good contrast (black text on white background)
- Helpful: Properly formatted tables or organized text

---

## Parsing Accuracy

### High Accuracy Scenarios
- Clear table format with distinct columns
- EPIC IDs in standard format
- Voter names clearly separated
- Booth numbers properly identified

### Lower Accuracy Scenarios
- Mixed formats in same PDF
- Voter IDs with non-standard formatting
- Small font sizes or poor quality scans
- Complex table structures with merged cells

---

## Troubleshooting PDF Parsing

### Problem: "No voters extracted"
**Solutions**:
- Verify PDF has readable text (not scanned image)
- Check booth numbers are numeric (e.g., "001" not "Booth One")
- Verify EPIC IDs match the format: KKDDSSSSSS
- Try saving as a different PDF version

### Problem: "Some voters not extracted"
**Solutions**:
- Check for inconsistent voter ID format
- Verify booth numbers in that section
- Remove special characters from names if present
- Ensure voter IDs don't have extra spaces

### Problem: "Incorrect data extracted"
**Solutions**:
- Verify column order (Booth, EPIC ID, Name)
- Check for extra spaces in data
- Remove headers if they match voter data pattern
- Use table format instead of text format

---

## Best Practices

### Do's ✅
1. ✅ Use table format when possible
2. ✅ Keep booth numbers as simple numbers (001, 042)
3. ✅ Use proper EPIC format (KA01A0001234)
4. ✅ Put voter names in a dedicated column
5. ✅ Keep PDF file size reasonable (<20MB for best results)
6. ✅ Use consistent formatting throughout the document

### Don'ts ❌
1. ❌ Don't mix formats within the same PDF
2. ❌ Don't use "Booth One" instead of "01"
3. ❌ Don't include EPIC ID in name column
4. ❌ Don't use special unicode characters
5. ❌ Don't use images instead of text
6. ❌ Don't encrypt the PDF

---

## Sample Files

### Sample 1: Simple Table
```
Booth | Voter ID      | Name
------|---------------|------------------
001   | KA01A0001001  | Rajesh Kumar
001   | KA01A0001002  | Priya Singh
001   | KA01A0001003  | Amit Kumar
```

### Sample 2: Extended Table with Extra Columns
```
Booth | Serial | Voter ID      | Full Name      | Gender | Age
------|--------|---------------|----------------|--------|----
001   | 1      | KA01A0001001  | Rajesh Kumar   | M      | 45
001   | 2      | KA01A0001002  | Priya Singh    | F      | 42
001   | 3      | KA01A0001003  | Amit Kumar     | M      | 38
002   | 1      | KA01A0002001  | Deepa Sharma   | F      | 50
```

### Sample 3: Text Format
```
Booth: 001
List of Voters:
- KA01A0001001: Rajesh Kumar
- KA01A0001002: Priya Singh
- KA01A0001003: Amit Kumar

Booth: 002
- KA01A0002001: Deepa Sharma
- KA01A0002002: Rajiv Patel
```

---

## Advanced Features

### Union Lists
If you have multiple booth lists, you can:
1. Upload them one at a time, or
2. Combine into a single PDF before uploading

### Historical Data
- Previous voter data is preserved
- Only new voter IDs are added (duplicates skipped)
- Updated information requires manual update via UI

---

## Support

If your PDF format is not being recognized:
1. Check the format requirements above
2. Try converting to a simpler format
3. Create a sample PDF using the provided examples
4. Refer to SETUP.md for more guidance

---

**PDF Format Guide Version**: 1.0
**Last Updated**: April 2026
**Supported since**: Version 1.0
