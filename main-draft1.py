import uvicorn
import os
from fastapi import FastAPI
from elasticsearch import Elasticsearch

ELASTICSEARCH_URL = os.environ["ELASTICSEARCH_URL"]
ELASTIC_API_KEY = os.environ["ELASTIC_API_KEY"]
INDEX = 'employees'

# Set up client
client = Elasticsearch(
    hosts=ELASTICSEARCH_URL,
    api_key=ELASTIC_API_KEY,
)

# # Manually adding employee
# employee = {
#     "emp_id": "001", # to avoid replicas
#     "name": "Habiba",
#     "dob": "2004-06-12",
#     "gender": "Female",
#     "nationality": "Egypt",
#     "degree": "Mechatronics & Robotics Engineer",
#     "job_description": "Software Developer",
# }
#
# client.index(index=INDEX, id = employee["emp_id"], document=employee)
#
# print("Employee added")

# # Manually searching index
# response = client.search(
#     index=INDEX,
#     query={
#         "multi_match": {
#             "query": "AI Engineer from Egypt",
#             "fields": ["name", "nationality", "degree^2", "job_description^3"]
#     }
# }
# )
#
# for hit in response["hits"]["hits"]:
#     print(f'{hit["_source"]}\n')

app = FastAPI()
@app.get("/")
def root():
    return {"message": "Hello World"}


@app.post("/new-index",
          summary= "Create a new index",)
def create_new_index(index_name: str):
    mapping={
     "mappings": {
         "properties": {
             "emp_id": {"type": "keyword"},
             "name": {"type": "text"},
             "dob": {"type": "date"},
             "gender": {"type": "keyword"},
             "nationality": {"type": "text"},
             "degree": {"type": "text"},
             "job_description": {"type": "text"},
             "cv": {"type": "text"},
         }
     }
    }
    client.indices.create(index=index_name, body=mapping)


@app.post("/push-data",
          summary= "Add new employee",
          description= "Adds an employee document into the Elasticsearch employees index.\n\n"
                       "DOB FORMAT: YYYY-MM-DD")
def add_employee(employee_id : int,
                 name : str,
                 dob : str ,
                 gender : str,
                 nationality : str,
                 degree : str,
                 job_description : str,
                 index_name = "employees"
                 ):

    employee = {
        "emp_id": employee_id,
        "name": name,
        "dob": dob,
        "gender": gender,
        "nationality": nationality,
        "degree": degree,
        "job_description": job_description,
    }
    client.index(index=index_name, id = employee["emp_id"], document=employee)
    return {"message": "Employee added"}

@app.get("/search")
def search_employees(query: str):
    response = client.search(
        index=INDEX,
        query={
            "multi_match": {
                "query": query,
                "fields" : ["name", "dob", "gender", "nationality", "degree^2", "job_description^3"],
            }
        }
    )

    results = []

    for hit in response["hits"]["hits"]:
        results.append(hit["_source"])

    if results == []:
        return {"message": "No results found"}
    else:
        return {"query": query, "results": results}