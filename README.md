# Rule Engine with AST

A full-stack application built with FastAPI, SQLite and Reactjs for creating a rule engine. This application allows you to add and combine rules based on different fields and values, and evaluate data based on those rules.



## Docker Image

The Docker image for this app can be found [here](https://hub.docker.com/r/darthyoda1/rule-engine).

To run the app, ensure you have the following installed on your local machine:

- [Docker](https://www.docker.com/get-started)

Steps to run the image:


Pull the docker image:

`docker pull darthyoda1/rule-engine`

Before running the image, make sure ports 3000 and 8000 are free. Run the image:

`docker run -p 8000:8000 -p 3000:3000 darthyoda1/rule-engine`

This will start the frontend on port 3000 and the backend on port 8000.

Now you can view the rules and interact with the app by visiting `localhost:3000`.


## Prerequisites

To work on the source code and add and test your own features, you need these packages:

- package manager (npm or yarn and pip)
- nodejs (>=18.0.0)
- python (>= 3.10)

## Getting Started

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/rule-engine.git
cd rule-engine
```

### Step 2: Install required packages

```bash
cd backend

pip install -r requirements.txt

cd frontend

npm install
```

This will install the required packages for both the frontend and the backend.

Now you can run the app locally and make changes to the code.