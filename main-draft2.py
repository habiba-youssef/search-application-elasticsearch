import uvicorn
import os
from fastapi import FastAPI, HTTPException
from elasticsearch import Elasticsearch

from sentence_transformers import SentenceTransformer

# for NLP search
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

ELASTICSEARCH_URL = os.environ["ELASTICSEARCH_URL"]
ELASTIC_API_KEY = os.environ["ELASTIC_API_KEY"]

# Set up client
client = Elasticsearch(
    hosts=ELASTICSEARCH_URL,
    api_key=ELASTIC_API_KEY,
)

app = FastAPI()

# Root Page - Starting Info
@app.get("/",
         summary="Smart Knowledge Search Application",
         description = "Features Available:\n\n"
                       "- Search from pre-designed index/database\n\n"
                       "- Input data into pre-designed index/database\n\n"
                       "- Create new index/database\n\n"
                       "- Push data to any index/database\n\n")

def root():
    return ("Smart Knowledge Search Application"
            "Features Available:\n\n"
            "- Search from pre-designed index/database\n\n"
            "- Input data into pre-designed index/database\n\n"
            "- Create new index/database\n\n"
            "- Push data to any Index/database\n\n")

# Search pre-designed index (employees)
@app.get("/search-employees")
# ADD: hybrid search method = keyword search + vector search!!!!!!!!!!!!!!
def search_employees(query: str, gender = "Male/Female"):
    filters = {}
    if gender.capitalize() == "Male":
        filters["term"] = {"gender": "Male"}
    elif gender.capitalize() == "Female":
        filters["term"] = {"gender": "Female"}
    elif gender == "Male/Female":
        filters["match_all"] = {}
    else:
        return "Not a valid Filter Input. Try Again."

    response = client.search(
        index='employees',
        query={
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": query,
                            "fields": [
                                "name",
                                "nationality",
                                "degree^2",
                                "job_description^3",
                                "department"
                            ]
                        }
                    }
                ],
                "filter": filters
            }
        },
        knn={
            "field": "embedding",
            "query_vector": model.encode(query).tolist(),
            "k": 4,
            "num_candidates": 100,
            "filter": filters
        },
        # Search result ranking with highlighted matches.
        highlight={
            "fields": {
                "name": {},
                "nationality" : {},
                "degree" : {},
                "job_description" : {}
            }
        }
    )

    results = []

    for hit in response["hits"]["hits"]:
        results.append({
            "employee": hit["_source"],
            "highlight": hit.get("highlight", {})
        })

    if not results:
        return "No results found"
    else:
        return {"query": query, "results": results}


# Input data into pre-designed index (employees)
@app.post("/add-employee",
          summary= "Add New Employee Data",
          description= "Adds an employee document into the Elasticsearch employees index.\n\n"
                       "Important info:\n\n"
                       "- DOB FORMAT: YYYY-MM-DD"
                       "- Gender: Male or Female")
def add_employee(employee_id : int, # to avoid replicas
                 name : str,
                 dob : str ,
                 gender : str,
                 nationality : str,
                 degree : str,
                 job_description : str,
                 ):

    employee = {
        "emp_id": employee_id,
        "name": name.capitalize(),
        "dob": dob,
        "gender": gender.capitalize(),
        "nationality": nationality.capitalize(),
        "degree": degree.capitalize(),
        "job_description": job_description,
    }
    client.index(index='employees', id = employee["emp_id"], document=employee)
    return "Employee added"


# Elasticsearch index creation
@app.post("/create-index",
          summary= "Create New Index/Database",
          description= 'Format is the following:\n\n\n\n'
                       '{\n\n'
            '"property1": {"type": "text/integer/float/keyword/date/boolean"},\n\n'
            '"property2": {"type": "text/integer/float/keyword/date/boolean"},\n\n'
            '"property3": {"type": "text/integer/float/keyword/date/boolean"},\n\n'
            '"property4": {"type": "text/integer/float/keyword/date/boolean"},\n\n'
            '"property5": {"type": "text/integer/float/keyword/date/boolean"},\n\n'
            '"property6": {"type": "text/integer/float/keyword/date/boolean"},\n\n'
            '"property7": {"type": "text/integer/float/keyword/date/boolean"},\n\n'
            '}\n\n\n\n'
                       'etc.')
def create_index(index_name:str, properties:dict):
    mapping = {
        "mappings" : {
            "properties": properties
            # {
            #     "food": {"type": "text"},
            #     "calories": {"type": "float"},
            # }
        }
    }

    client.indices.create(index=index_name, body=mapping)

# Add document to index
@app.post("/add-to-index",
          summary= "",
          description= 'example:\n\n'
                       '{\n\n'
                       '"name": "Ahmed",\n\n'
                       '"nationality": "Kuwait",\n\n'
                       '}')
def add_document(index_name:str, data:dict):
    # check if index exists
    if not client.indices.exists(index=index_name):
        raise HTTPException(status_code=404, detail=f"Index '{index_name}' does not exist.")

    # check if data format is dict
    elif not isinstance(data, dict) or not data:
        raise HTTPException(status_code=400, detail="Data formatting incorrect")

    try:
        # add document
        client.index(index=index_name, document=data)
        return "data added successfully"

    except Exception:
        raise HTTPException(status_code=500)

# Add document(s) to any index
from setup import Setup
# Bulk docs ingesting
@app.post("/bulk-add-to-index",
          summary= "Bulk Data Ingestion Pipeline",
          description= "Important info:\n\n"
                       "- path must be url AND csv, e.g. 'https://raw.githubusercontent.com/habiba-youssef/databases/refs/heads/main/EmployeesData.csv'\n\n"
                       "- Mapping e.g.\n\n\n\n"
                       "{\n\n"
                       '"mappings": {\n\n'
                       '    "properties": {\n\n'
                       '        "property1": {"type": "text/integer/float/keyword/date/boolean"},\n\n'
                       '        "property1": {"type": "text/integer/float/keyword/date/boolean"},\n\n'
                       '    }\n\n'
                       ' }\n\n'
                       '}\n\n'
          )
def bulk_add_document(mapping:dict, path:str, index_name:str):
    NewDocs = Setup(mapping=mapping, path=path)
    NewDocs.setup(index_name=index_name)