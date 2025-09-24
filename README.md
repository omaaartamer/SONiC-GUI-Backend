# SONiC-GUI-Backend

Backend API service for SONiC switch management GUI.

## Description

REST API that bridges the frontend GUI with SONiC switches via RESTCONF. Handles authentication and provides endpoints for switch configuration and monitoring.

## Tech Stack

- FastAPI (Python)
- JWT authentication
- RESTCONF client for SONiC communication
- AsyncSSH – For CLI feature that connects directly to SONiC switch
- Redis – For caching (Ports, VLANs) and rate limiting
- TinyDB – Lightweight JSON-based storage for user data
- HuggingFace Embeddings + ChromaDB – For semantic search of SONiC documentation
- Gemini 2.5 Flash LLM – To power the chatbot feature
- GitHub Actions – CI/CD linting workflow

## Current Features

- User authentication
- Vlan CRUD Operations
- Port Operational Status Retrieval
- Cli feature
- Redis cache for Vlans and Port Operations
- Rate Limiting
- Chatbot Feature
    - ChromaDB stores usies HuggingFace embeddings for SONiC Documentation
    - User query is sent to the backend
    - Prompt Template instructs Gemini 2.5 Flash LLM on how to process the query
    - Agent retrieves relevant context and invokes appropriate tools then adds result to the context
    - Parsed answer is returned to user
  
## Getting Started

### Prerequisites
- **Python 3.11+**
- **Docker**

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/omaaartamer/SONiC-GUI-Backend.git
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
   
4. **Install Dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt

5. **Run the Application**
   ```bash
   uvicorn app.main:app --reload
   
6. **Install and run Redis (default port `6379`):**
   ```bash
   redis-server
   ```
