
# Smart Knowledge Search Application

An AI-powered search application built using **Python, FastAPI, and Elasticsearch** to store, manage, and retrieve structured information through natural-language queries.

The application demonstrates **hybrid search**, combining traditional keyword matching with semantic vector search to improve search relevance.

The primary use case is an **employee directory**, allowing users to search employee profiles based on qualifications, department, nationality, and job descriptions.

## Features

- **Hybrid Search:** Combines Elasticsearch full-text search with kNN vector similarity search.
- **Semantic Search:** Uses Sentence Transformers to generate embeddings and identify contextually relevant results.
- **Keyword Search:** Searches employee records using Elasticsearch's `multi_match` queries.
- **Search Filters:** Filter employee results by gender and department.
- **Result Ranking & Highlighting:** Returns relevance-ranked results with highlighted keyword matches.
- **Index Management:** Create custom Elasticsearch indexes with configurable field mappings.
- **Data Ingestion:** Add individual documents or bulk-import data from CSV files.
- **REST APIs:** FastAPI endpoints for searching, inserting, and managing data.
- **Web Interface:** Basic HTML landing page linking to interactive API documentation.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend development |
| FastAPI | REST API development |
| Elasticsearch | Indexing, storage, and hybrid search |
| Sentence Transformers | Generating semantic embeddings |
| all-MiniLM-L6-v2 | Embedding model (384 dimensions) |
| Pydantic | Data validation |
| CSV | Dataset ingestion |
| Jinja2, HTML, CSS | Basic frontend |

## How It Works

1. **Data Ingestion:** Employee records are added individually or imported from CSV files.
2. **Embedding Generation:** Text is converted into numerical vectors using Sentence Transformers.
3. **Indexing:** Employee data and embeddings are stored in Elasticsearch.
4. **Query Processing:** User queries are processed using both keyword matching and vector similarity.
5. **Results:** Elasticsearch retrieves relevance-ranked employee records with optional filters and keyword highlighting.

### Example Search

**Query:**
```text
Machine learning engineer from Egypt
```

The application searches employee qualifications, nationalities, departments, and job descriptions to identify relevant profiles.

## Project Structure

```text
smart-knowledge-search/
│
├── main.py                 # FastAPI application and API endpoints
├── config.py               # Elasticsearch configuration and data models
├── setup.py                # CSV ingestion and indexing pipeline
│
├── templates/
│   └── index.html          # Application landing page
│
├── EmployeesData(1).csv    # Sample employee dataset
└── README.md               # Project documentation
```

Earlier development versions (`draft1.py` and `draft2.py`) are optional and are not required to run the latest application.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Display application landing page |
| GET | `/search-employees` | Search employees using hybrid search and optional filters |
| POST | `/add-employee` | Add employee data and generate embeddings |
| POST | `/create-index` | Create a new Elasticsearch index |
| POST | `/add-to-index` | Add a document to an existing index |
| POST | `/bulk-add-to-index` | Import multiple documents from an online CSV file |

### Example API Request

```http
GET /search-employees?query=software%20engineer&department=IT
```

The search endpoint supports:
- Natural-language queries
- Optional gender and department filters
- Keyword and vector similarity search
- Relevance-ranked results with keyword highlighting

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/smart-knowledge-search.git
cd smart-knowledge-search
```

### 2. Install Dependencies

```bash
pip install fastapi uvicorn elasticsearch sentence-transformers pydantic jinja2 python-dotenv
```

### 3. Configure Elasticsearch

Set up an Elasticsearch deployment and obtain an API key with the required permissions.

Update `config.py` to load credentials from environment variables rather than hardcoding them.

Create a local `.env` file:

```env
ELASTICSEARCH_URL=your_elasticsearch_endpoint
ELASTIC_API_KEY=your_api_key
```

Load these values in `config.py` using `python-dotenv`.

**Security:** Never commit API keys or `.env` files to GitHub. Any previously exposed keys should be rotated.

### 4. Prepare the Elasticsearch Index

Before adding or searching employee records, create an `employees` index.

The index mapping should include:
- Employee fields such as `name`, `nationality`, `degree`, and `department`
- An indexed `dense_vector` field named `embedding` with 384 dimensions
- `keyword` mappings for fields used in exact-match filters

### 5. Run the Application

```bash
uvicorn main:app --reload
```

Open the following URLs:

- **Landing Page:** http://127.0.0.1:8000/
- **Interactive API:** http://127.0.0.1:8000/docs
- **API Documentation:** http://127.0.0.1:8000/redoc

The Swagger UI interface allows users to test the API endpoints directly.

## Sample Dataset

The repository includes a CSV dataset containing **20 employee profiles**, with information such as:

- Employee ID
- Name
- Date of birth
- Gender
- Nationality
- Degree
- Department
- Job description

The sample data can be used to demonstrate employee indexing and searching.

**Note:** The current bulk ingestion endpoint accepts publicly accessible CSV URLs rather than local file uploads. CSV column order must match the supplied mapping.

## Current Limitations & Future Improvements

- **Frontend:** The existing HTML page serves as a landing page. Dedicated interfaces for employee search and data submission have not yet been developed.
- **Search Scope:** Hybrid search is currently implemented for the employee index rather than all dynamically created indexes.
- **File Attachments:** CV and PDF upload, extraction, and indexing are not yet supported.
- **Data Ingestion:** CSV ingestion relies on matching field order, and the generic document insertion endpoint does not automatically generate embeddings.
- **Production Readiness:** Automated testing, authentication, pagination, enhanced error handling, and deployment configuration remain future improvements.

## Project Summary

This project demonstrates the integration of **Python, FastAPI, Elasticsearch, and machine learning embeddings** to build an intelligent search and retrieval system.

It combines traditional search techniques with semantic similarity to provide more flexible and relevant results while supporting API-based data management and ingestion.
