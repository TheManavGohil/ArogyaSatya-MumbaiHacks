# TrueLen API Documentation

Base URL: `http://localhost:8000`

## Overview
TrueLen is a healthcare misinformation detection system. This API provides endpoints for triggering content scans, retrieving articles, analyzing claims, and viewing trending narratives.

## Endpoints

### 1. Health Check
**GET** `/api/health`

Checks if the API is running.

**Response:**
```json
{
  "status": "ok"
}
```

### 2. Trigger Scan
**POST** `/api/trigger-scan`

Manually triggers the scraper manager to fetch new content from configured sources (BBC, CNN, Twitter, etc.).

**Response:**
```json
{
  "status": "Scan completed"
}
```

### 3. List Articles
**GET** `/api/articles`

Retrieves a list of the latest 20 scraped articles/content items.

**Response:**
```json
[
  {
    "id": 1,
    "title": "Article Title",
    "source": "BBC Health",
    "url": "https://...",
    "published_at": "2023-10-27T10:00:00",
    ...
  },
  ...
]
```

### 4. Analyze Content (by ID)
**POST** `/api/analyze/{content_id}`

Triggers the full AI Agent Graph analysis for a specific article already in the database.
*   **Video Processing**: If the content is a video URL.
*   **Safety Check**: Pre-screens for harmful advice.
*   **Claim Extraction**: Identifies medical assertions.
*   **Evidence Retrieval**: Searches PubMed, Web, and Drug databases.
*   **Verification**: Verifies claims against evidence.
*   **Explanation**: Generates a final report.

**Parameters:**
*   `content_id` (path): The ID of the article to analyze.

**Response:**
```json
{
  "status": "Analysis completed",
  "report": "Markdown formatted executive summary...",
  "verification_results": [
    {
      "claim": "Extracted claim text",
      "status": "False",
      "explanation": "Reasoning...",
      "evidence": [
        {
          "source": "PubMed",
          "title": "Study Title",
          "url": "https://pubmed...",
          "snippet": "Abstract..."
        }
      ]
    }
  ]
}
```

### 5. Analyze Text (Manual)
**POST** `/api/analyze-text`

Analyzes raw text or a URL provided directly in the request body.

**Request Body:**
```json
{
  "text": "Drinking bleach cures COVID-19."
}
```

**Response:**
Same structure as `/api/analyze/{content_id}`.

### 6. Get Trends
**GET** `/api/trends`

Retrieves trending healthcare misinformation narratives based on clustered claims.

**Response:**
```json
[
  {
    "topic": "Vaccine Infertility",
    "count": 15,
    "example_claim": "Vaccines cause sterility in women."
  },
  ...
]
```

### 7. Root
**GET** `/`

Returns a welcome message.

**Response:**
```json
{
  "message": "Healthcare Misinformation Detector API is running"
}
```
