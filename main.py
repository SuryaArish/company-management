from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from models import Company, Task, TaskTemplate, AssignData
import handlers

load_dotenv()

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Company API Routes
@app.get("/getall_companies/{user_id}")
async def get_companies(user_id: str):
    return await handlers.get_companies(user_id)

@app.get("/get_company/{user_id}/{company_id}")
async def get_company_by_id(user_id: str, company_id: str):
    return await handlers.get_company_by_id(user_id, company_id)

@app.post("/create_company/{user_id}")
async def create_company(user_id: str, company_data: Company):
    return await handlers.create_company(user_id, company_data)

@app.put("/update_company/{user_id}/{company_id}")
async def update_company(user_id: str, company_id: str, company_data: Company):
    return await handlers.update_company(user_id, company_id, company_data)

@app.delete("/delete_company/{user_id}/{company_id}")
async def delete_company(user_id: str, company_id: str):
    return await handlers.delete_company(user_id, company_id)

# Task API Routes
@app.get("/getall_tasks/{user_id}")
async def get_tasks(user_id: str):
    return await handlers.get_tasks(user_id)

@app.get("/get_task/{user_id}/{task_id}")
async def get_task_by_id(user_id: str, task_id: str):
    return await handlers.get_task_by_id(user_id, task_id)

@app.post("/create_task/{user_id}")
async def create_task(user_id: str, task_data: Task):
    return await handlers.create_task(user_id, task_data)

@app.put("/update_task/{user_id}/{task_id}")
async def update_task(user_id: str, task_id: str, task_data: Task):
    return await handlers.update_task(user_id, task_id, task_data)

@app.delete("/delete_task/{user_id}/{task_id}")
async def delete_task(user_id: str, task_id: str):
    return await handlers.delete_task(user_id, task_id)

# Template API Routes
@app.get("/getall_templates/{user_id}")
async def get_templates(user_id: str):
    return await handlers.get_templates(user_id)

@app.post("/create_template/{user_id}")
async def create_template(user_id: str, template_data: TaskTemplate):
    return await handlers.create_template(user_id, template_data)

@app.delete("/delete_template/{user_id}/{template_id}")
async def delete_template(user_id: str, template_id: str):
    return await handlers.delete_template(user_id, template_id)

@app.post("/assign_template/{user_id}/{template_id}")
async def assign_template(user_id: str, template_id: str, assign_data: AssignData):
    return await handlers.assign_template(user_id, template_id, assign_data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

# ride it
# yad
