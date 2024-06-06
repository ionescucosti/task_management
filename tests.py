from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_execute_task_1():
    response = client.post(
        "/execute-task/",
        json={
                "task_type": "execute_code",
                "code": "for i in range(5): print(f'Count {i}')",
                "resources": {
                    "cpu": "1",
                    "gpu": "0",
                    "ram": "256MB",
                    "storage": "500MB"
                }
            },
    )
    assert response.status_code == 200
    assert response.json() == {
                                "message": "Task executed",
                                "logs": "Count 0\nCount 1\nCount 2\nCount 3\nCount 4\n",
                                "resources": {
                                    "cpu": "1",
                                    "gpu": "0",
                                    "ram": "256MB",
                                    "storage": "500MB"
                                }
                            }

def test_execute_task_2():
    response = client.post(
        "/execute-task/",
        json={
                "task_type": "execute_code",
                "code": "print('Hello, World!')",
                "resources": {
                    "cpu": "2",
                    "gpu": "0",
                    "ram": "512MB",
                    "storage": "1GB"
                }
            },
    )
    assert response.status_code == 200
    assert response.json() == {
                                "message": "Task executed",
                                "logs": "Hello, World!\n",
                                "resources": {
                                    "cpu": "2",
                                    "gpu": "0",
                                    "ram": "512MB",
                                    "storage": "1GB"
                                }
                            }
