from elasticsearch import helpers
import csv
from urllib.request import urlopen
import io

from config import client, model


# data_url = "https://raw.githubusercontent.com/habiba-youssef/databases/refs/heads/main/EmployeesData.csv"
data_url = 'https://raw.githubusercontent.com/habiba-youssef/databases/refs/heads/main/foodcalories.csv'
# INDEX = 'employees'
INDEX = 'calorie_tracking'
# DATASET_PATH = 'EmployeesData.csv'

# DEFAULT_MAPPING = {
#     "mappings": {
#         "properties": {
#             "emp_id": {"type": "integer"},
#             "name": {"type": "text"},
#             "dob": {"type": "date"},
#             "gender": {"type": "keyword"},
#             "nationality": {"type": "text"},
#             "degree" : {"type": "text"},
#             "department": {"type": "keyword"},
#             "job_description": {"type": "text"},
#             'embedding': {      # for hybrid search
#                 'type': 'dense_vector',
#                 'dims': 384,
#                 'index': True,
#                 'similarity': "cosine"
#             }
#             }
#         }
#     }

DEFAULT_MAPPING = {
    "mappings": {
        "properties": {
            "calories": {"type": "integer"},
            "food": {"type": "text"},
            "g_protein": {"type": "integer"},
            }
            }
        }

class Setup:
    def __init__(self, mapping:dict, path:str):
        self.path = path
        self.mapping = mapping

    # error handling 1 - file path entered incorrectly
    def validate_file_path(self):
        if not self.path.endswith(".csv"):
            raise ValueError("File must be a CSV file.")

    # error handling 2 - checks if mapping and csv file lengths match
    def validate_csv_mapping(self, csv_headers, property_list):
        if len(csv_headers) != len(property_list):
            raise ValueError(f"CSV columns ({len(csv_headers)}) do not match mapping fields ({len(property_list)})")

    # error handling 3 - checks if index already exisst
    def validate_index(self, clients, index_name):
        if clients.indices.exists(index=index_name):
            without_embed = clients.indices.get_mapping(index=index_name)[f'{index_name}']['mappings'][
                                'properties'].keys() - {'embedding'}

            for field in without_embed:
                if not self.mapping['mappings']['properties'][field] == \
                    clients.indices.get_mapping(index=index_name)[f'{index_name}']['mappings']['properties'][field]:
                    raise ValueError(f"Index '{index_name}' already exists and mapping doesn't match.")
        else:
            clients.indices.create(index=index_name, body=self.mapping)

    def generate_actions(self):
        # This function is passed into the bulk() helper to create many documents in sequence.
        self.validate_file_path()
        response = urlopen(self.path)
        csv_data = io.StringIO(response.read().decode('utf-8'))

        reader = csv.DictReader(csv_data)
        docs = []  # to iterate for bulk
        # property_list = list(self.mapping["mappings"]["properties"].keys())
        property_list = [
            field for field in self.mapping["mappings"]["properties"].keys()
            if field != "embedding"
        ]
        y = 0
        csv_heading_length = list(reader.fieldnames) # error handling 2
        for row in reader:
            doc = {}  # new dictionary each iteration
            text_to_embed = ""
            i = 0
            for csv_heading in row:
                # to compare against using embeddings
                text_to_embed += f"{row[csv_heading]} "
                embedding = model.encode(text_to_embed).tolist()

                self.validate_csv_mapping(csv_heading_length, property_list)
                doc[property_list[i]] = row[csv_heading]
                i += 1

            # y += 1
            # doc["_id"] = y
            doc["embedding"] = embedding

            docs.append(doc)

        return docs

    # Set up client
    def add_docs(self, index_name:str):
        try:
            self.validate_index(client, index_name)
            # Indexing documents in bulk
            helpers.bulk(client=client, index=index_name, actions=self.generate_actions())

        except Exception as error:
            print(f"Error: {error}")
            raise error

# Testing sample data
# sample_data_trial = Setup(mapping=DEFAULT_MAPPING,path=data_url)
# sample_data_trial.add_docs(index_name=INDEX)