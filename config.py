import os
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

ELASTICSEARCH_URL = os.environ["ELASTICSEARCH_URL"]
ELASTIC_API_KEY = os.environ["ELASTIC_API_KEY"]

# Set up client
client = Elasticsearch(
    hosts=ELASTICSEARCH_URL,
    api_key=ELASTIC_API_KEY,
)

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Base Model - input models
from pydantic import BaseModel,Field

class Employee(BaseModel):
    emp_id: int
    name: str = Field(min_length=2, max_length=50)
    dob: str = Field(example="YYYY-MM-DD")
    gender: str = Field(pattern="^(?i)(male|female)$")
    nationality: str
    degree: str
    department : str
    job_description: str

class NewIndex(BaseModel):
    index_name: str
    properties: dict = Field(
        example={
            "property1": {"type": "text/integer/float/keyword/date/boolean"},
            "property2": {"type": "text/integer/float/keyword/date/boolean"},
            "property1": {"type": "text/integer/float/keyword/date/boolean"},
        }
    )

class NewDocument(BaseModel):
    index_name: str
    document: dict = Field(
        example={
            "Field1": "content1",
            "Field2": "content2",
            "Field3": "content3",
        }
    )

class BulkAddDocuments(BaseModel):
    index_name: str
    path : str = Field(example= "https://raw.githubusercontent.com/.../data.csv")
    mapping: dict = Field(
        example={
        "mappings": {
            "properties": {
                "property1": {"type": "text/integer/float/keyword/date/boolean"},
                "property2": {"type": "text/integer/float/keyword/date/boolean"},
                "property3": {"type": "text/integer/float/keyword/date/boolean"},
            }
            }
            }
    )