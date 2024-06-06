from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import os
import docker

app = FastAPI()


class Resources(BaseModel):
    cpu: str
    gpu: str
    ram: str
    storage: str


class TaskRequest(BaseModel):
    task_type: str
    code: str
    resources: Resources


docker_client = docker.from_env()


def parse_storage_size(size_str):
    size_str = size_str.upper()
    if size_str.endswith('MB'):
        return int(size_str[:-2]) * 1024 * 1024
    elif size_str.endswith('GB'):
        return int(size_str[:-2]) * 1024 * 1024 * 1024
    else:
        raise ValueError("Unsupported storage size format. Use MB or GB.")


@app.post("/execute-task")
async def execute_task(task: TaskRequest):
    if task.task_type != "execute_code":
        raise HTTPException(status_code=400, detail="Invalid task type")

    # Validate resources
    try:
        cpu = int(task.resources.cpu)
        gpu = int(task.resources.gpu)
        ram = task.resources.ram
        storage = parse_storage_size(task.resources.storage)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Resource parsing error: {e}")

    # Create the code file in the current directory
    code_file_path = "script.py"
    with open(code_file_path, "w") as code_file:
        code_file.write(task.code)

    # Docker resource constraints
    mem_limit = ram
    cpu_quota = cpu * 100000

    # GPU support using NVIDIA runtime
    device_requests = None
    if gpu > 0:
        device_requests = [
            docker.types.DeviceRequest(count=gpu, capabilities=[['gpu']])
        ]

    # Create and run Docker container
    try:
        container = docker_client.containers.run(
            image="python:3.9-slim",
            command=f"python /app/script.py",
            volumes={os.path.abspath('.'): {"bind": "/app", "mode": "rw"}},
            tmpfs={'/usr/src/app': f'size={storage}'},  # Simulate storage constraint using tmpfs
            mem_limit=mem_limit,
            cpu_quota=cpu_quota,
            device_requests=device_requests,
            detach=True,
            runtime="nvidia" if gpu > 0 else None
        )

        # Wait for the container to finish execution
        container.wait()

        # Retrieve logs
        logs = container.logs().decode("utf-8")

        # Remove the container
        container.remove()

        # Clean up the code file
        os.remove(code_file_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Container execution error: {e}")

    return {"message": "Task executed", "logs": logs, "resources": task.resources}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
