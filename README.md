# SONiC-GUI-Backend

Backend API service for SONiC switch management GUI.

## Description

REST API that bridges the frontend GUI with SONiC switches via RESTCONF. Handles authentication and provides endpoints for switch configuration and monitoring.

## Tech Stack

- FastAPI (Python)
- JWT authentication
- RESTCONF client for SONiC communication
- AsyncSSH – For CLI feature that connects directly to SONiC switch
- GitHub Actions – CI/CD linting workflow

## Current Features

- User authentication
- Vlan CRUD Operations
- Port Operational Status Retrieval
- Cli feature

## Getting Started

### Prerequisites
- **Python 3.11+**
- **Docker**

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/alaaashraf19/SONiC-GUI-Backend.git
   cd SONiC-GUI-Backend

2. **Setup Virtual Enviroment**
   ```bash
   python -m venv venv
   venv\Scripts\activate #For Windows
   source venv/bin/activate  # Linux/Mac
   
3. **Enviroment Variables**
   ```bash
   cp .env.example .env
   ```
- Update the .env file with your values
   
   
5. **Install Dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt

6. **Run the Application**
   ```bash
   uvicorn app.main:app --reload

