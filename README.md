How to run the project:

Open Terminal
Clone project: git clone https://github.com/ionescucosti/task_management.git
Move to project folder: RUN cd task_management
Create virtual envorinment: RUN python -m venv .venv
Activate .venv: RUN source .venv/bin/activate
Install requirements: pip install -r requirements.txt
Start Docker instance
Start main app: RUN uvicorn main:app --reload
Run tests in anonther terminal: RUN pytest
