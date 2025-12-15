import httpx
import json
import os
from typing import List, Optional
from models import Company, Task, TaskTemplate
import jwt
import time
from datetime import datetime

async def get_access_token() -> str:
    client_email = os.getenv("FIREBASE_CLIENT_EMAIL")
    private_key = os.getenv("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n')
    
    print(f"Client email: {client_email}")
    print(f"Private key length: {len(private_key)}")
    
    if not client_email or not private_key:
        raise Exception("Missing Firebase credentials in environment variables")
    
    now = int(time.time())
    
    payload = {
        "iss": client_email,
        "scope": "https://www.googleapis.com/auth/datastore",
        "aud": "https://oauth2.googleapis.com/token",
        "exp": now + 3600,
        "iat": now,
    }
    
    token = jwt.encode(payload, private_key, algorithm="RS256")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": token,
            }
        )
        
        token_data = response.json()
        return token_data["access_token"]

async def get_companies() -> List[Company]:
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    user_id = "S982Zx4o90FuchAp2idT"  # Replace with actual user ID
    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/cm-users-dev/{user_id}/companies"
    
    print(f"Getting companies from: {url}")
    
    try:
        token = await get_access_token()
        print(f"Got access token: {token[:20]}...")
    except Exception as e:
        print(f"Error getting access token: {e}")
        raise
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text[:500]}")
        
        if response.status_code in [403, 401]:
            print("Authentication failed - returning empty list")
            return []
        
        if response.status_code != 200:
            print(f"Unexpected status code: {response.status_code}")
            return []
        
        data = response.json()
        companies = []
        
        if "documents" in data:
            for doc in data["documents"]:
                company = parse_firestore_company(doc)
                if company:
                    companies.append(company)
        
        return companies

async def get_tasks() -> List[Task]:
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    user_id = "S982Zx4o90FuchAp2idT"  # Replace with actual user ID
    
    # Get all companies first, then get tasks from each company
    companies_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/cm-users-dev/{user_id}/companies"
    
    token = await get_access_token()
    all_tasks = []
    
    async with httpx.AsyncClient() as client:
        # Get all companies
        companies_response = await client.get(
            companies_url,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if companies_response.status_code in [403, 401]:
            return []
        
        companies_data = companies_response.json()
        
        if "documents" in companies_data:
            for company_doc in companies_data["documents"]:
                company_id = company_doc["name"].split("/")[-1]
                
                # Get tasks for this company
                tasks_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/cm-users-dev/{user_id}/companies/{company_id}/Task"
                
                tasks_response = await client.get(
                    tasks_url,
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if tasks_response.status_code == 200:
                    tasks_data = tasks_response.json()
                    if "documents" in tasks_data:
                        for task_doc in tasks_data["documents"]:
                            task = parse_firestore_task(task_doc)
                            if task:
                                all_tasks.append(task)
    
    return all_tasks
    
    token = await get_access_token()
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code in [403, 401]:
            return []
        
        data = response.json()
        tasks = []
        
        if "documents" in data:
            for doc in data["documents"]:
                task = parse_firestore_task(doc)
                if task:
                    tasks.append(task)
        
        return tasks

async def get_templates() -> List[TaskTemplate]:
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/task_templates"
    
    token = await get_access_token()
    
    async with httpx.AsyncClient() as client:
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

async def create_company(company: Company) -> bool:
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    user_id = "S982Zx4o90FuchAp2idT"  # Replace with actual user ID
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
    
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=firestore_doc
        )
        
        return response.status_code < 400

async def get_company_by_id(company_id: str) -> Optional[Company]:
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    user_id = "S982Zx4o90FuchAp2idT"  # Replace with actual user ID
    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/cm-users-dev/{user_id}/companies/{company_id}"
    
    token = await get_access_token()
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code in [404, 403, 401]:
            return None
        
        doc = response.json()
        return parse_firestore_company(doc)

async def update_company(company_id: str, company: Company) -> bool:
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    user_id = "S982Zx4o90FuchAp2idT"  # Replace with actual user ID
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
    
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=firestore_doc
        )
        
        return response.status_code < 400

async def delete_company(company_id: str) -> bool:
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    user_id = "S982Zx4o90FuchAp2idT"  # Replace with actual user ID
    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/cm-users-dev/{user_id}/companies/{company_id}"
    
    token = await get_access_token()
    
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            url,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        return response.status_code < 400

async def create_task(task: Task) -> bool:
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    user_id = "S982Zx4o90FuchAp2idT"  # Replace with actual user ID
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
    
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=firestore_doc
        )
        
        return response.status_code < 400

async def get_task_by_id(task_id: str) -> Optional[Task]:
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    user_id = "S982Zx4o90FuchAp2idT"  # Replace with actual user ID
    
    # Need to search through all companies to find the task
    companies_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/cm-users-dev/{user_id}/companies"
    
    token = await get_access_token()
    
    async with httpx.AsyncClient() as client:
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
    
    token = await get_access_token()
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code in [404, 403, 401]:
            return None
        
        doc = response.json()
        return parse_firestore_task(doc)

async def update_task(task_id: str, task: Task) -> bool:
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    user_id = "S982Zx4o90FuchAp2idT"  # Replace with actual user ID
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
    
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=firestore_doc
        )
        
        return response.status_code < 400

async def delete_task(task_id: str, company_id: str) -> bool:
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    user_id = "S982Zx4o90FuchAp2idT"  # Replace with actual user ID
    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/cm-users-dev/{user_id}/companies/{company_id}/Task/{task_id}"
    
    token = await get_access_token()
    
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            url,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        return response.status_code < 400