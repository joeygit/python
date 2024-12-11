from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import requests
import time
import json
from datetime import datetime, timedelta
app = FastAPI()

# TSheets API credentials
TSHEETS_TOKEN = "TOKEN"
TSHEETS_BASE_URL = "https://rest.tsheets.com/api/v1"

#print("tsheets url:", url)
# Set up headers with authentication token
headers = {
    "Authorization": f"Bearer {TSHEETS_TOKEN}",
    "Content-Type": "application/json"
}
@app.get("/")
def root():
  return {"message": "Hello World"}

def get_parent_job_code(name: str):
    try:
        # Construct the API request URL with query parameter
        url = f"{TSHEETS_BASE_URL}/jobcodes?name={name}"
        # Make request to TSheets API
        response = requests.get(url, headers=headers)
        print("tsheets response:", response.json())
        response.raise_for_status()  # Raise exception for HTTP errors
        # Parse response JSON  
        if not response.json()["results"]["jobcodes"]:
            # if no jobcodes found, return NOT_FOUND
            return "NOT_FOUND"
        else:
            job_code_id = next(iter(response.json()["results"]["jobcodes"].keys()))
            return job_code_id

    except requests.exceptions.RequestException as e:
        # Handle request exceptions
        errorResp = {
            "response" : response,
            "error"    : e
        }
        return errorResp
        #raise HTTPException(status_code=500, detail=f"Error accessing TSheets API: {e}")

    except KeyError as e:
        # Handle missing data in response
        errorResp = {
            "response" : response,
            "error"    : e
        }
        return errorResp
        #raise HTTPException(status_code=500, detail="Unexpected response format from TSheets API")

def get_child_job_code(jobnum: str, jobname: str):
    ticket_name = jobname + " - " + jobnum
    print("ticketname", ticket_name)
    try:
        # Construct the API request URL with query parameter
        url = f"{TSHEETS_BASE_URL}/jobcodes?name={ticket_name}"
        # Make request to TSheets API
        response = requests.get(url, headers=headers)
        print("tsheets response:", response.json())
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Access the jobcodes dictionary
        jobcodes = response.json()['results']['jobcodes']
        print("jobcode: ", jobcodes)
        # Iterate through each jobcode
        for key, value in jobcodes.items():
            # Access the id value for each jobcode
            id_value = value['id']
            print("ID:", id_value)
            return id_value
        # Parse response JSON  
        #if not response.json()["results"]["jobcodes"]:
            # if no jobcodes found, return NOT_FOUND
          #  return "NOT_FOUND"
       # else:
          #  job_code_id = next(iter(response.json()["results"]["jobcodes"].keys()))
           # return job_code_id

    except requests.exceptions.RequestException as e:
        # Handle request exceptions
        errorResp = {
            "response" : response,
            "error"    : e
        }
        return errorResp
        #raise HTTPException(status_code=500, detail=f"Error accessing TSheets API: {e}")

    except KeyError as e:
        # Handle missing data in response
        errorResp = {
            "response" : response,
            "error"    : e
        }
        return errorResp
        #raise HTTPException(status_code=500, detail="Unexpected response format from TSheets API")

def create_parent_job(parent_job_name: str):
    try:
        # Construct the request payload
        payload = {
            "data": 
                {
                    "jobcode": {
                        "name": parent_job_name,
                        "parent_id": 0,  # Assuming this is a parent job
                        "assigned_to_all": "yes"
                    }
                }
            
        }
        print("Parent Payload: ", payload)
        # Make a POST request to create a new parent job
        headers = {
            "Authorization": f"Bearer {TSHEETS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(f"{TSHEETS_BASE_URL}/jobcodes", json=payload, headers=headers)
        #print("Parent response: ", response.reason, response.content, response)
        # Check if the request was successful
        if response.status_code == 200:
            # Parent job created successfully
            return {"message": "Parent job created successfully"}
        else:
            # If request was unsuccessful, raise HTTPException
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        # Handle request exceptions
        errorResp = {
            "response" : response,
            "error"    : e
        }
        return errorResp
        #raise HTTPException(status_code=500, detail=f"Error accessing TSheets API: {e}")

    except KeyError as e:
        # Handle missing data in response
        errorResp = {
            "response" : response,
            "error"    : e
        }
        return errorResp
    
def create_jobcode(parent_jobcode: int, job_name: str, ticketnum: int):
    try:
        # Construct the request payload
        trun_jobName = job_name[:50]
        ticket_name = trun_jobName + " - " + ticketnum
        payload = {
            "data": {
                "jobcode": {
                    "parent_id": parent_jobcode,
                    "name":      ticket_name,
                    "billable":  "yes",
                    "assigned_to_all": "yes"
                }
            }
        }
        print("job Payload: ", payload)
        # Make a POST request to create a new jobcode
        
        response = requests.post(f"{TSHEETS_BASE_URL}/jobcodes", json=payload, headers=headers)
        print("child response: ", response.reason, response.content, response)
        # Check if the request was successful
        if response.status_code == 200:
            # Jobcode created successfully
            return {"message": "Jobcode created successfully"}
        else:
            # If request was unsuccessful, raise HTTPException
            response.raise_for_status()

    except requests.exceptions.RequestException as e:
        # Handle request exceptions
        errorResp = {
            "response" : response,
            "error"    : e
        }
        return errorResp
        #raise HTTPException(status_code=500, detail=f"Error accessing TSheets API: {e}")

    except KeyError as e:
        # Handle missing data in response
        errorResp = {
            "response" : response,
            "error"    : e
        }
        return errorResp

#@app.get("/webhook/get_old_Jobs")
def get_old_jobcodes():   
    # Calculate the date 2 years ago
    two_years_ago = datetime.now() - timedelta(days=365*5)
    two_years_ago_str = two_years_ago.strftime('%Y-%m-%dT%H:%M:%S%z')
    # Send a GET request to retrieve all jobcodes
    response = requests.get(f"{TSHEETS_BASE_URL}/jobcodes", headers=headers)
    print(response)
    # Check if the request was successful
    if response.status_code == 200:
        jobcodes = response.json().get('results', {}).get('jobcodes', {})
        old_jobcodes = []
        # Filter jobcodes based on last modified date
        for jobcode_id, jobcode_info in jobcodes.items():
            last_modified = jobcode_info.get('last_modified')
            if last_modified and last_modified < two_years_ago_str:
                old_jobcodes.append(jobcode_info)
        return old_jobcodes
    else:
        print("Failed to retrieve jobcodes:", response.text)
        return []

def archive_job_code(jobnum: str, jobname: str):
    try:
        jobcode_id = get_child_job_code(jobnum, jobname)
        # Construct the API request URL with query parameter
        print("jobcode in archive: ", jobcode_id)
        payload = { "data":  [
                 {
                    "id":  jobcode_id,
                     "active":  "false"
                 }
             ]
        }
        url = f"{TSHEETS_BASE_URL}/jobcodes"
        # Make request to TSheets API
        print("payload in archive: ", payload)
        print("URL: ", url)
        response = requests.put(url, headers=headers, json=payload)
        print("archive response: ", response.reason)
        print("archive response: ", response.raw)
    except requests.exceptions.RequestException as e:
        # Handle request exceptions
        errorResp = {
            "response" : response,
            "error"    : e
        }
        return errorResp
        #raise HTTPException(status_code=500, detail=f"Error accessing TSheets API: {e}")

    except KeyError as e:
        # Handle missing data in response
        errorResp = {
            "response" : response,
            "error"    : e
        }
        return errorResp
        #raise HTTPException(status_code=500, detail="Unexpected response format from TSheets API")    


@app.get("/webhook/archive_old_Jobs")
async def deactivate_jobcodes():
    oldJobs = await get_old_jobcodes()
    print("oldjobs: ", oldJobs)
    # Iterate over the list of jobcodes and send PATCH requests to deactivate them
    for jobcode_id in oldJobs:
        payload = {
            "data": {
                "id": jobcode_id,
                "active": False
            }
        }
        print(payload)
        # Send PATCH request to update the jobcode
        #response = requests.patch(f"{TSHEETS_BASE_URL}/jobcodes", headers=headers, json=payload)

        # Check if the request was successful
        '''
        if response.status_code == 200:
            print(f"Jobcode {jobcode_id} deactivated successfully.")
        else:
            print(f"Failed to deactivate jobcode {jobcode_id}. Status code: {response.status_code}")
'''


class TicketPayload(BaseModel):
    tickettitle: str
    ticketorg: str  # Assuming organization name can be optional
    ticketnum: str  # Assuming ticket ID is a string

@app.post("/webhook/newticket")
async def receive_webhook(payload: TicketPayload):
    # Process the incoming payload
    tickettitle = payload.tickettitle
    ticketorg = payload.ticketorg
    ticketnum = payload.ticketnum
    # Example: Print the received data
    print("Received ticket:", tickettitle)
    print("Received ticket:", ticketorg)
    print("Received ticket:", ticketnum)
   # print("Received organization name:", organization_name)
   # print("Received ticket ID:", ticket_number)
    
    # get tsheets parent code
    parentcode = get_parent_job_code(ticketorg)

    if parentcode == 'NOT_FOUND':
        #parent does not exist, create parent first
        print("calling create_parent_job with org: ", ticketorg)
        create_parent_job(ticketorg)
        time.sleep(3)
        newParentcode = get_parent_job_code(ticketorg)
        create_jobcode(newParentcode, tickettitle, ticketnum)
    else:
        # parent already exists, continue adding ticket
        create_jobcode(parentcode, tickettitle, ticketnum)
    #print("ParentCode:", parentcode)
    #return {"ticketorg": ticketorg}


# Endpoint to query parent job code by name
#@app.get("/parent-job-code/")

@app.post("/webhook/closeticket")
def closeJob(payload: TicketPayload):
    # Process the incoming payload
    tickettitle = payload.tickettitle
    ticketorg = payload.ticketorg
    ticketnum = payload.ticketnum
    # Example: Print the received data
    print("Received ticket:", tickettitle)
    print("Received ticket:", ticketorg)
    print("Received ticket:", ticketnum)
   # print("Received organization name:", organization_name)
   # print("Received ticket ID:", ticket_number)
    ticket_name = tickettitle + " - " + ticketnum
    # get tsheets parent code
    #closejobcode = get_child_job_code(ticket_name)    
    archive_job_code(ticketnum, tickettitle)
