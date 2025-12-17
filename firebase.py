import httpx
import json
import os
from typing import List, Optional
from models import Company, Task, TaskTemplate
import jwt
import time
from datetime import datetime
import asyncio

# Global variables for caching
_cached_token = None
_token_expiry = 0
_http_client = None

async def get_http_client():
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(timeout=30.0)
    return _http_client

async def get_access_token() -> str:
    global _cached_token, _token_expiry
    
    now = int(time.time())
    if _cached_token and now < _token_expiry - 300:  # Refresh 5 minutes before expiry
        return _cached_token
    
    client_email = os.getenv("FIREBASE_CLIENT_EMAIL")
    private_key = os.getenv("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n')
    
    if not client_email or not private_key:
        raise Exception("Missing Firebase credentials in environment variables")
    
    payload = {
        "iss": client_email,
        "scope": "https://www.googleapis.com/auth/datastore",
        "aud": "https://oauth2.googleapis.com/token",
        "exp": now + 3600,
        "iat": now,
    }
    
    token = jwt.encode(payload, private_key, algorithm="RS256")
    
    client = await get_http_client()
    response = await client.post(
        "https://oauth2.googleapis.com/token",
        data={
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": token,
        }
    )
    
    token_data = response.json()
    _cached_token = token_data["access_token"]
    _token_expiry = now + 3600
    return _cached_token

async def get_companies(user_id: str) -> List[Company]:
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/cm-users-dev/{user_id}/companies"
    
    token = await get_access_token()
    client = await get_http_client()
    
    response = await client.get(
        url,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code in [403, 401, 404]:
        return []
    
    if response.status_code != 200:
        return []
    
    data = response.json()
    companies = []
    
    if "documents" in data:
        for doc in data["documents"]:
            company = parse_firestore_company(doc)
            if company:
                companies.append(company)
    
    return companies



async def get_tasks(user_id: str) -> List[Task]:
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    
    companies_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/cm-users-dev/{user_id}/companies"
    
    token = await get_access_token()
    client = await get_http_client()
    
    companies_response = await client.get(
        companies_url,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if companies_response.status_code in [403, 401, 404]:
        return []
    
    companies_data = companies_response.json()
    
    if "documents" not in companies_data:
        return []
    
    # Create concurrent requests for all company tasks
    async def get_company_tasks(company_doc):
        company_id = company_doc["name"].split("/")[-1]
        tasks_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/cm-users-dev/{user_id}/companies/{company_id}/Task"
        
        tasks_response = await client.get(
            tasks_url,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if tasks_response.status_code == 200:
            tasks_data = tasks_response.json()
            if "documents" in tasks_data:
                return [parse_firestore_task(task_doc) for task_doc in tasks_data["documents"] if parse_firestore_task(task_doc)]
        return []
    
    # Execute all requests concurrently
    task_lists = await asyncio.gather(*[get_company_tasks(company_doc) for company_doc in companies_data["documents"]], return_exceptions=True)
    
    # Flatten the results
    all_tasks = []
    for task_list in task_lists:
        if isinstance(task_list, list):
            all_tasks.extend(task_list)
    
    return all_tasks

async def get_templates(user_id: str) -> List[TaskTemplate]:
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/task_templates"
    
    token = await get_access_token()
    client = await get_http_client()
    
    response = await client.get(
        url,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code in [403, 401]:
        return []
    
    data = response.json()
    templates = []
    
    if "documents" in data:
        for doc in data["documents"]:
            template = parse_firestore_template(doc)
            if template:
                templates.append(template)
    
    return templates

def parse_firestore_company(doc: dict) -> Optional[Company]:
    try:
        fields = doc["fields"]
        doc_id = doc["name"].split("/")[-1]
        
        return Company(
            id=doc_id,
            name=get_string_value(fields, "name"),
            EIN=get_string_value(fields, "EIN"),
            startDate=get_string_value(fields, "startDate"),
            stateIncorporated=get_string_value(fields, "stateIncorporated"),
            contactPersonName=get_string_value(fields, "contactPersonName"),
            contactPersonPhNumber=get_string_value(fields, "contactPersonPhNumber"),
            address1=get_string_value(fields, "address1"),
            address2=get_string_value(fields, "address2"),
            city=get_string_value(fields, "city"),
            state=get_string_value(fields, "state"),
            zip=get_string_value(fields, "zip")
        )
    except:
        return None

def parse_firestore_task(doc: dict) -> Optional[Task]:
    try:
        fields = doc["fields"]
        doc_id = doc["name"].split("/")[-1]
        
        return Task(
            id=doc_id,
            companyId=get_string_value(fields, "company_id"),
            title=get_string_value(fields, "title"),
            description=get_optional_string_value(fields, "description"),
            completed=get_bool_value(fields, "completed")
        )
    except:
        return None

def parse_firestore_template(doc: dict) -> Optional[TaskTemplate]:
    # Templates are not stored in Firebase, they are just used to create tasks
    return None

def get_string_value(fields: dict, field_name: str) -> str:
    return fields.get(field_name, {}).get("stringValue", "")

def get_optional_string_value(fields: dict, field_name: str) -> Optional[str]:
    value = fields.get(field_name, {}).get("stringValue")
    return value if value else None

def get_bool_value(fields: dict, field_name: str) -> bool:
    return fields.get(field_name, {}).get("booleanValue", False)

async def create_company(user_id: str, company: Company) -> bool:
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    doc_id = company.id
    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/cm-users-dev/{user_id}/companies/{doc_id}"
    
    token = await get_access_token()
    
    firestore_doc = {
        "fields": {
            "name": {"stringValue": company.name},
            "EIN": {"stringValue": company.EIN},
            "startDate": {"stringValue": company.startDate},
            "stateIncorporated": {"stringValue": company.stateIncorporated},
            "contactPersonName": {"stringValue": company.contactPersonName},
            "contactPersonPhNumber": {"stringValue": company.contactPersonPhNumber},
            "address1": {"stringValue": company.address1},
            "address2": {"stringValue": company.address2},
            "city": {"stringValue": company.city},
            "state": {"stringValue": company.state},
            "zip": {"stringValue": company.zip}
        }
    }
    
    client = await get_http_client()
    response = await client.patch(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=firestore_doc
    )
    
    return response.status_code < 400

async def get_company_by_id(user_id: str, company_id: str) -> Optional[Company]:
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/cm-users-dev/{user_id}/companies/{company_id}"
    
    token = await get_access_token()
    client = await get_http_client()
    
    response = await client.get(
        url,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code in [404, 403, 401]:
        return None
    
    doc = response.json()
    return parse_firestore_company(doc)

async def update_company(user_id: str, company_id: str, company: Company) -> bool:
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/cm-users-dev/{user_id}/companies/{company_id}"
    
    token = await get_access_token()
    
    firestore_doc = {
        "fields": {
            "name": {"stringValue": company.name},
            "EIN": {"stringValue": company.EIN},
            "startDate": {"stringValue": company.startDate},
            "stateIncorporated": {"stringValue": company.stateIncorporated},
            "contactPersonName": {"stringValue": company.contactPersonName},
            "contactPersonPhNumber": {"stringValue": company.contactPersonPhNumber},
            "address1": {"stringValue": company.address1},
            "address2": {"stringValue": company.address2},
            "city": {"stringValue": company.city},
            "state": {"stringValue": company.state},
            "zip": {"stringValue": company.zip}
        }
    }
    
    client = await get_http_client()
    response = await client.patch(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=firestore_doc
    )
    
    return response.status_code < 400

async def delete_company(user_id: str, company_id: str) -> bool:
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/cm-users-dev/{user_id}/companies/{company_id}"
    
    token = await get_access_token()
    client = await get_http_client()
    
    response = await client.delete(
        url,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    return response.status_code < 400

async def create_task(user_id: str, task: Task) -> bool:
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    doc_id = task.id
    company_id = task.companyId
    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/cm-users-dev/{user_id}/companies/{company_id}/Task/{doc_id}"
    
    token = await get_access_token()
    
    firestore_doc = {
        "fields": {
            "company_id": {"stringValue": task.companyId},
            "title": {"stringValue": task.title},
            "description": {"stringValue": task.description or ""},
            "completed": {"booleanValue": task.completed}
        }
    }
    
    client = await get_http_client()
    response = await client.patch(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=firestore_doc
    )
    
    return response.status_code < 400

async def get_task_by_id(user_id: str, task_id: str) -> Optional[Task]:
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    
    # Need to search through all companies to find the task
    companies_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/cm-users-dev/{user_id}/companies"
    
    token = await get_access_token()
    client = await get_http_client()
    
    companies_response = await client.get(
        companies_url,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if companies_response.status_code in [403, 401, 404]:
        return None
    
    companies_data = companies_response.json()
    
    if "documents" in companies_data:
        for company_doc in companies_data["documents"]:
            company_id = company_doc["name"].split("/")[-1]
            
            task_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/cm-users-dev/{user_id}/companies/{company_id}/Task/{task_id}"
            
            task_response = await client.get(
                task_url,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if task_response.status_code == 200:
                doc = task_response.json()
                return parse_firestore_task(doc)
    
    return None

async def update_task(user_id: str, task_id: str, task: Task) -> bool:
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    company_id = task.companyId
    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/cm-users-dev/{user_id}/companies/{company_id}/Task/{task_id}"
    
    token = await get_access_token()
    
    firestore_doc = {
        "fields": {
            "company_id": {"stringValue": task.companyId},
            "title": {"stringValue": task.title},
            "description": {"stringValue": task.description or ""},
            "completed": {"booleanValue": task.completed}
        }
    }
    
    client = await get_http_client()
    response = await client.patch(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=firestore_doc
    )
    
    return response.status_code < 400

async def delete_task(user_id: str, task_id: str, company_id: str) -> bool:
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/cm-users-dev/{user_id}/companies/{company_id}/Task/{task_id}"
    
    token = await get_access_token()
    client = await get_http_client()
    
    response = await client.delete(
        url,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    return response.status_code < 400