from fastapi import HTTPException
from models import Company, Task, TaskTemplate, AssignData
import firebase
from datetime import datetime
import uuid

async def get_companies():
    try:
        companies = await firebase.get_companies()
        return companies
    except Exception as e:
        print(f"Error in get_companies: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

async def create_company(company_data: Company):
    company_id = str(uuid.uuid4())
    company_data.id = company_id
    company_data.created_at = datetime.utcnow()
    company_data.updated_at = datetime.utcnow()
    
    try:
        success = await firebase.create_company(company_data)
        if success:
            return {"message": "Data created successfully", "id": company_id}
        else:
            raise HTTPException(status_code=500, detail="Internal server error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

async def update_company(company_id: str, company_data: Company):
    # Check if company exists first
    try:
        existing_company = await firebase.get_company_by_id(company_id)
        if not existing_company:
            return {"message": "That data not exist"}
        
        # Company exists, proceed with update
        company_data.id = company_id
        company_data.updated_at = datetime.utcnow()
        
        success = await firebase.update_company(company_id, company_data)
        if success:
            return {"message": "Data updated successfully", "id": company_id}
        else:
            raise HTTPException(status_code=500, detail="Internal server error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

async def delete_company(company_id: str):
    # Check if company exists first
    try:
        existing_company = await firebase.get_company_by_id(company_id)
        if not existing_company:
            return {"message": "That data not exist"}
        
        # Company exists, proceed with delete
        success = await firebase.delete_company(company_id)
        if success:
            return {"message": "Company deleted successfully", "id": company_id}
        else:
            raise HTTPException(status_code=500, detail="Internal server error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_company_by_id(company_id: str):
    try:
        company = await firebase.get_company_by_id(company_id)
        if company:
            return company
        else:
            return {"message": "That data not exist"}
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_tasks():
    try:
        tasks = await firebase.get_tasks()
        return tasks
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

async def create_task(task_data: Task):
    task_id = str(uuid.uuid4())
    task_data.id = task_id
    task_data.created_at = datetime.utcnow()
    task_data.updated_at = datetime.utcnow()
    
    try:
        success = await firebase.create_task(task_data)
        if success:
            return {"message": "Data created successfully", "id": task_id}
        else:
            raise HTTPException(status_code=500, detail="Internal server error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

async def update_task(task_id: str, task_data: Task):
    # Check if task exists first
    try:
        existing_task = await firebase.get_task_by_id(task_id)
        if not existing_task:
            return {"message": "That data not exist"}
        
        # Task exists, proceed with update
        task_data.id = task_id
        task_data.updated_at = datetime.utcnow()
        
        success = await firebase.update_task(task_id, task_data)
        if success:
            return {"message": "Data updated successfully", "id": task_id}
        else:
            raise HTTPException(status_code=500, detail="Internal server error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

async def delete_task(task_id: str):
    print(f"DELETE /delete_task/{task_id} called")
    
    # Check if task exists first
    try:
        existing_task = await firebase.get_task_by_id(task_id)
        if existing_task:
            print(f"✅ Task found: {existing_task.title}")
            company_id = existing_task.companyId
        else:
            print(f"❌ Task not found with ID: {task_id}")
            return {"message": "That data not exist"}
        
        # Task exists, proceed with delete
        print(f"🗑️ Proceeding to delete task: {task_id}")
        success = await firebase.delete_task(task_id, company_id)
        if success:
            print("✅ Task deleted successfully from Firebase")
            return {"message": "Task deleted successfully", "id": task_id}
        else:
            print("❌ Failed to delete task from Firebase")
            raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        print(f"🔥 Error in delete_task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_task_by_id(task_id: str):
    try:
        task = await firebase.get_task_by_id(task_id)
        if task:
            return task
        else:
            return {"message": "That data not exist"}
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_templates():
    try:
        templates = await firebase.get_templates()
        return templates
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

async def create_template(template_data: TaskTemplate):
    created_tasks = []
    
    # Create a task for each company
    for company_id in template_data.companyIds:
        task_id = str(uuid.uuid4())
        
        # Create task object
        task = Task(
            id=task_id,
            companyId=company_id,
            title=template_data.title,
            description=template_data.description,
            completed=template_data.completed,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Save task to Firebase
        try:
            success = await firebase.create_task(task)
            if success:
                created_tasks.append({
                    "task_id": task_id,
                    "company_id": company_id,
                    "status": "created"
                })
            else:
                created_tasks.append({
                    "task_id": task_id,
                    "company_id": company_id,
                    "status": "failed"
                })
        except Exception:
            created_tasks.append({
                "task_id": task_id,
                "company_id": company_id,
                "status": "error"
            })
    
    return {
        "message": "Tasks created and assigned to companies",
        "created_tasks": created_tasks,
        "total_companies": len(template_data.companyIds),
        "successful_assignments": len([t for t in created_tasks if t["status"] == "created"])
    }

async def delete_template(template_id: str):
    return {"message": "Template deleted successfully", "id": template_id}

async def assign_template(template_id: str, assign_data: AssignData):
    return {
        "message": "Template assigned successfully",
        "templateId": template_id,
        "companyIds": assign_data.companyIds,
        "startDate": assign_data.startDate,
        "dueDate": assign_data.dueDate,
        "assigned_at": datetime.utcnow().isoformat()
    }