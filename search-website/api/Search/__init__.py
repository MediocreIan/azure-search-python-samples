import logging
import azure.functions as func
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from shared_code import azure_config
import json
import ssl

ssl.SSLContext.verify_mode = ssl.VerifyMode.CERT_OPTIONAL
environment_vars = azure_config()
# Set Azure Search endpoint and key
# endpoint = f'https://{environment_vars["search_service_name"]}.search.windows.net'
endpoint = "https://abcds-search-dev.search.windows.net"
# key = environment_vars["search_api_key"]
key = "FEF4CC675BAD6B362E22228412E28C1A"

# Your index name
index_name = 'adlsgen2-index'

# Create Azure SDK client
search_client = SearchClient(endpoint, index_name, AzureKeyCredential(key))

# returns obj like {authors: 'array', language_code:'string'}
def read_facets(facetsString):
    facets = facetsString.split(",")
    output = {}
    for x in facets:
        if(x.find('*') != -1):
            newVal = x.replace('*','')
            output[newVal]='array'
        else: 
            output[x]='string'
            
    return output


# creates filters in odata syntax
def create_filter_expression(filter_list, facets):
    i = 0
    filter_expressions = []
    return_string = ""
    separator = ' and '
    print(facets)
    while (i < len(filter_list)) :
        field = filter_list[i]["field"]
        value = filter_list[i]["value"]
        
        if (facets[field] == 'array'): 
            print('array')
            filter_expressions.append(f'{field}/any(t: search.in(t, \'{value}\', \',\'))')
        else :
            print('value')
            filter_expressions.append(f'{field} eq \'{value}\'')
        
        i += 1
    
    
    return_string = separator.join(filter_expressions)

    return return_string

def new_shape(docs):
    print(docs)
    old_api_shape = list(docs)
    print(old_api_shape)
    # print(docs.next())
    # count=0
    # client_side_expected_shape = []
    
    # for item in old_api_shape:
        
    #     new_document = {}
    #     print(item)
    #     # new_document["score"]=item["@search.score"]

    
    # return list(client_side_expected_shape)

def main(req: func.HttpRequest) -> func.HttpResponse:

    # variables sent in body
    req_body = req.get_json()
    q = req_body.get('q')
    print(req_body)
    top = req_body.get('top') or 8
    skip = req_body.get('skip') or 0
    filters = req_body.get('filters') or []

    # facets = environment_vars["search_facets"]
    facets="display_customer_name"
    print("FACETS")
    print(facets)
    facetKeys = read_facets(facets)
    print(facetKeys)
    
    filter=""
    if(len(filters)): 
        filter = create_filter_expression(filters, facetKeys)

    if q:
        print(q)
        logging.info(f"/Search q = {q}")
        print("LINE129")
        print(q)
        search_results = search_client.search(search_text=q)
        print(search_results)
        returned_docs = new_shape(search_results)
        # returned_count = search_results.get_count()
        # returned_facets = search_results.get_facets()
        
        # # format the React app expects
        # full_response = {}
        
        # full_response["count"]=search_results.get_count()
        # full_response["facets"]=search_results.get_facets()
        # full_response["results"]=returned_docs
        
        
        # return func.HttpResponse(body=json.dumps(full_response), mimetype="application/json",status_code=200)
        return func.HttpResponse(
             "query found.",
             status_code=200
        )
    else:
        print("no query param found")
        return func.HttpResponse(
             "No query param found.",
             status_code=200
        )

