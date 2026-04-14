# Voter Data Management System - API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication
Currently, the API does not require authentication (development mode).

## Response Format
All responses are in JSON format:

### Success Response
```json
{
    "status": "success",
    "data": {},
    "message": "Operation completed successfully"
}
```

### Error Response
```json
{
    "status": "error",
    "message": "Error description"
}
```

---

## Endpoints

### 1. Booths

#### Get All Booths
```
GET /api/booths
```

**Description**: Retrieve all booths in the system

**Query Parameters**: None

**Response**:
```json
{
    "status": "success",
    "booths": [
        {
            "id": 1,
            "booth_number": "001",
            "booth_name": "Booth 001"
        }
    ],
    "total_booths": 1
}
```

**Status Codes**:
- 200 OK - Success
- 500 Internal Server Error

---

### 2. Voters

#### Get Voters by Booth
```
GET /api/booth/<booth_id>/voters
```

**Description**: Get all voters in a specific booth

**Path Parameters**:
- `booth_id` (integer, required) - The booth ID

**Response**:
```json
{
    "status": "success",
    "voters": [
        {
            "id": 1,
            "voter_id": "KA01A0001234",
            "voter_name": "John Smith",
            "booth_number": "001",
            "status": "not_visited",
            "custom_notes": null
        }
    ],
    "booth_stats": {
        "total": 150,
        "visited": 45
    }
}
```

**Status Codes**:
- 200 OK - Success
- 500 Internal Server Error

---

#### Search Voters
```
GET /api/search
```

**Description**: Search voters by name or voter ID

**Query Parameters**:
- `q` (string, required) - Search term (minimum 2 characters)
- `booth_id` (integer, optional) - Filter by booth

**Examples**:
```
GET /api/search?q=john
GET /api/search?q=KA01A0001234&booth_id=1
```

**Response**:
```json
{
    "status": "success",
    "voters": [
        {
            "id": 1,
            "voter_id": "KA01A0001234",
            "voter_name": "John Smith",
            "booth_number": "001",
            "status": "not_visited",
            "custom_notes": null
        }
    ],
    "count": 1
}
```

**Status Codes**:
- 200 OK - Success
- 400 Bad Request - Search term too short or missing
- 500 Internal Server Error

---

#### Update Voter
```
PUT /api/voter/<voter_id>
```

**Description**: Update voter status and/or notes

**Path Parameters**:
- `voter_id` (integer, required) - The voter ID

**Request Body**:
```json
{
    "status": "visited",
    "custom_notes": "Voter was at home, confirmed information"
}
```

**Possible Status Values**:
- `not_visited` - Default status
- `visited` - Voter has been visited
- `not_available` - Voter not at location
- `no_entry` - Restricted access
- `verified` - Information verified

**Response**:
```json
{
    "status": "success",
    "message": "Voter updated successfully"
}
```

**Status Codes**:
- 200 OK - Success
- 400 Bad Request - No fields provided
- 500 Internal Server Error

**Request Body Variations**:
```json
// Update only status
{
    "status": "visited"
}

// Update only notes
{
    "custom_notes": "Some notes here"
}

// Update both
{
    "status": "visited",
    "custom_notes": "Notes text"
}
```

---

### 3. File Upload

#### Upload PDF
```
POST /api/upload-pdf
```

**Description**: Upload and parse a voter list PDF

**Content-Type**: `multipart/form-data`

**Form Parameters**:
- `pdf_file` (file, required) - The PDF file

**Example with cURL**:
```bash
curl -X POST http://localhost:5000/api/upload-pdf \
  -F "pdf_file=@voters_list.pdf"
```

**Response**:
```json
{
    "status": "success",
    "message": "Successfully added 1500 voters",
    "added_voters": 1500,
    "skipped_voters": 25,
    "total_booths": 12
}
```

**Error Response**:
```json
{
    "status": "error",
    "message": "Could not extract voter data from PDF. Please ensure it contains..."
}
```

**Status Codes**:
- 200 OK - Success
- 400 Bad Request - No file, wrong format, or extraction failed
- 413 Payload Too Large - File exceeds 50MB
- 500 Internal Server Error

**PDF Requirements**:
- Format: PDF file
- Max size: 50MB
- Must contain voter information with:
  - Voter Name
  - Voter ID (EPIC format: KKDDSSSSSS)
  - Booth Number (numeric)

---

### 4. Statistics

#### Get System Statistics
```
GET /api/stats
```

**Description**: Get overall statistics

**Query Parameters**: None

**Response**:
```json
{
    "status": "success",
    "total_voters": 1525,
    "visited_voters": 123,
    "total_booths": 12
}
```

**Status Codes**:
- 200 OK - Success
- 500 Internal Server Error

---

### 5. Data Management

#### Clear All Data
```
POST /api/clear-data
```

**Description**: Clear all voters and booths from database (DANGER - no undo!)

**Query Parameters**: None

**Request Body**: None

**Response**:
```json
{
    "status": "success",
    "message": "All data cleared successfully"
}
```

**Status Codes**:
- 200 OK - Success
- 500 Internal Server Error

⚠️ **WARNING**: This operation cannot be undone. All data will be permanently deleted.

---

## Error Codes

| Code | Meaning | Common Cause |
|------|---------|--------------|
| 400 | Bad Request | Missing required parameter, invalid format |
| 404 | Not Found | Endpoint doesn't exist |
| 413 | Payload Too Large | File exceeds 50MB |
| 500 | Internal Server Error | Server-side error |

---

## Rate Limiting

Currently, no rate limiting is implemented (development mode).

For production, implement rate limiting to prevent abuse.

---

## CORS Configuration

The API allows CORS requests from all origins (development mode).

**CORS Headers**:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

---

## Examples

### Example 1: Upload PDF and Search
```bash
# 1. Upload PDF
curl -X POST http://localhost:5000/api/upload-pdf \
  -F "pdf_file=@voters.pdf"

# 2. Get all booths
curl http://localhost:5000/api/booths

# 3. Search voter
curl "http://localhost:5000/api/search?q=john&booth_id=1"
```

### Example 2: Update Voter Status
```bash
curl -X PUT http://localhost:5000/api/voter/1 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "visited",
    "custom_notes": "Verified on 2026-04-14"
  }'
```

### Example 3: Get Statistics
```bash
curl http://localhost:5000/api/stats
```

---

## Pagination Notes

The API does not implement pagination. All results are returned at once.

For large datasets (>10,000 voters), consider implementing pagination in future versions.

---

## Data Types

### Voter Object
```json
{
    "id": 1,
    "voter_id": "KA01A0001234",        // EPIC ID
    "voter_name": "John Smith",         // Full name
    "booth_number": "001",              // Booth number
    "status": "visited",                // Current status
    "custom_notes": "Some notes"        // Optional notes
}
```

### Booth Object
```json
{
    "id": 1,
    "booth_number": "001",              // Booth number
    "booth_name": "Booth 001"           // Booth name
}
```

---

## Testing the API

### Using Postman
1. Import endpoints from this documentation
2. Set base URL: `http://localhost:5000/api`
3. Test each endpoint with sample data

### Using cURL
See examples section above

### Using JavaScript Fetch
```javascript
// Search voters
fetch('http://localhost:5000/api/search?q=john')
    .then(response => response.json())
    .then(data => console.log(data));

// Update voter
fetch('http://localhost:5000/api/voter/1', {
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({status: 'visited'})
})
    .then(response => response.json())
    .then(data => console.log(data));
```

---

## Future API Enhancements

- Authentication & authorization
- Rate limiting
- Pagination
- Advanced filtering
- Export/import functionality
- Bulk operations
- API versioning (v1, v2, etc.)
- Request logging
- API key management

---

**API Documentation Version**: 1.0
**Last Updated**: April 2026
**API Version**: 1.0
