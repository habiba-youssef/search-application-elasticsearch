import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import config

# Root page frontend
templates = Jinja2Templates(directory="templates")

app = FastAPI()
# Root Page - Starting Info
@app.get("/", response_class=HTMLResponse,
         summary="Smart Knowledge Search Application",
         description = "Features Available:\n\n"
                       "- Search from pre-designed index/database\n\n"
                       "- Input data into pre-designed index/database\n\n"
                       "- Create new index/database\n\n"
                       "- Push data to any index/database\n\n")

def root(request: Request):
    return templates.TemplateResponse(
        request = request,
        name ="index.html",
        context = {"request": request}
    )

# Input data into pre-designed index (employees)
@app.post("/add-employee", summary= "Add New Employee Data",)

def add_employee(employee: config.Employee):
    employee_data = {
        "emp_id": employee.emp_id,
        "name": employee.name.capitalize(),
        "dob": employee.dob,
        "gender": employee.gender.capitalize(),
        "nationality": employee.nationality.capitalize(),
        "degree": employee.degree,
        "department": employee.department,
        "job_description": employee.job_description,
        "embedding" : config.model.encode(f'{employee.name}, {employee.dob}, {employee.gender}, {employee.nationality}, {employee.degree}, {employee.department}, {employee.job_description}').tolist()
    }
    config.client.index(index='employees', id = employee.emp_id, document=employee_data)
    return "Sucessfully added new employee data"

# Search pre-designed index (employees)
@app.get("/search-employees")
def search_employees(query: str, gender:str = None, department: str = None):
    filters = []

    # filter by department
    if department:
        filters.append({"term": {"department": department}})
    # filter by gender
    if gender:
        gender = gender.capitalize()
        if gender not in ["Male", "Female"]:
            return "Not a valid filter input. Try Again (Male/Female)."
        else:
            filters.append({"term": {"gender": gender}})

    response = config.client.search(
        index='employees',
        query={
            "bool": {
                "must": [
                    {
                        # keyword-based search method
                        "multi_match": {
                            "query": query,
                            "fields": [
                                "name",
                                "gender",
                                "nationality",
                                "degree^2",
                                "department",
                                "job_description^3",
                            ]
                        }
                    }
                ],
                "filter": filters
            }
        },
        # hybrid search method
        knn={
            "field": "embedding",
            "query_vector": config.model.encode(query).tolist(),
            "k": 4,
            "num_candidates": 100,
            "filter": filters
        },
        # highlights keywords found in document from query
        highlight={
            "fields": {
                "name": {},
                "nationality" : {},
                "degree" : {},
                "department" : {},
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
        return {"results": results}

# Elasticsearch index creation
@app.post("/create-index", summary= "Create New Index/Database")
def create_index(new_index: config.NewIndex):
    mapping = {
        "mappings": {
            "properties": new_index.properties
        }
    }
    config.client.indices.create(index=new_index.index_name, body=mapping)
    return "Index created sucessfully"

# Add document to any index
@app.post("/add-to-index", summary= "Add document to any Index/Database")

def add_document(new_doc: config.NewDocument):
    # check if index exists
    if not config.client.indices.exists(index=new_doc.index_name):
        raise HTTPException(status_code=404, detail=f"Index '{new_doc.index_name}' does not exist.")

    try:
        # add document
        config.client.index(index=new_doc.index_name, document=new_doc.document)
        return "data added successfully"

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

# Bulk add document(s) to any index
from setup import Setup
# Bulk docs ingesting
@app.post("/bulk-add-to-index", summary= "Bulk Data Ingestion Pipeline",
          description="make sure to match the CSV order to the mapping's order!")
def bulk_add_document(new_docs : config.BulkAddDocuments):
    try:
        NewDocs = Setup(mapping=new_docs.mapping, path=new_docs.path)
        NewDocs.add_docs(index_name=new_docs.index_name)
        return "data added successfully"
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
