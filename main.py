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
@app.get("/getall_companies")                                   # GET http://localhost:8080/getall_companies - Get All Companies
async def get_companies():
    return await handlers.get_companies()

@app.get("/get_company/{company_id}")                          # GET http://localhost:8080/get_company/{id} - Get Company By ID
async def get_company_by_id(company_id: str):
    return await handlers.get_company_by_id(company_id)

@app.post("/create_company")                                   # POST http://localhost:8080/create_company - Create New Company
async def create_company(company_data: Company):
    return await handlers.create_company(company_data)

@app.put("/update_company/{company_id}")                       # PUT http://localhost:8080/update_company/{id} - Update Company By ID
async def update_company(company_id: str, company_data: Company):
    return await handlers.update_company(company_id, company_data)

@app.delete("/delete_company/{company_id}")                    # DELETE http://localhost:8080/delete_company/{id} - Delete Company By ID
async def delete_company(company_id: str):
    return await handlers.delete_company(company_id)

# Task API Routes
@app.get("/getall_tasks")                                      # GET http://localhost:8080/getall_tasks - Get All Tasks
async def get_tasks():
    return await handlers.get_tasks()

@app.get("/get_task/{task_id}")                               # GET http://localhost:8080/get_task/{id} - Get Task By ID
async def get_task_by_id(task_id: str):
    return await handlers.get_task_by_id(task_id)

@app.post("/create_task")                                     # POST http://localhost:8080/create_task - Create New Task
async def create_task(task_data: Task):
    return await handlers.create_task(task_data)

@app.put("/update_task/{task_id}")                            # PUT http://localhost:8080/update_task/{id} - Update Task By ID
async def update_task(task_id: str, task_data: Task):
    return await handlers.update_task(task_id, task_data)

@app.delete("/delete_task/{task_id}")                         # DELETE http://localhost:8080/delete_task/{id} - Delete Task By ID
async def delete_task(task_id: str):
    return await handlers.delete_task(task_id)

# Template API Routes
@app.get("/getall_templates")                                 # GET http://localhost:8080/getall_templates - Get All Templates
async def get_templates():
    return await handlers.get_templates()

@app.post("/create_template")                                 # POST http://localhost:8080/create_template - Create New Template
async def create_template(template_data: TaskTemplate):
    return await handlers.create_template(template_data)

@app.delete("/delete_template/{template_id}")                 # DELETE http://localhost:8080/delete_template/{id} - Delete Template By ID
async def delete_template(template_id: str):
    return await handlers.delete_template(template_id)

@app.post("/assign_template/{template_id}")                   # POST http://localhost:8080/assign_template/{id} - Assign Template To Companies
async def assign_template(template_id: str, assign_data: AssignData):
    return await handlers.assign_template(template_id, assign_data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

