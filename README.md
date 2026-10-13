# AI Sales Workforce Agent

An AI-powered sales automation platform that combines Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), AI agent tool calling, FastAPI, PostgreSQL, n8n, and React to automate customer conversations and sales workflows.

The system can answer product-related questions using a knowledge base, retrieve relevant information through RAG, check demo availability, capture lead information, and persist leads in PostgreSQL.

---

## Project Overview

The AI Sales Workforce Agent is a conversational AI sales assistant designed to demonstrate how modern AI systems can interact with business knowledge, tools, databases, and workflow automation.

Unlike a traditional chatbot that only generates text, this system combines an LLM with RAG and backend tools to perform actions based on customer requests.

The project demonstrates an end-to-end AI application architecture consisting of:

- LLM-powered conversational AI
- Retrieval-Augmented Generation
- Vector similarity search
- AI agent tool calling
- Lead capture
- Demo availability checking
- PostgreSQL persistence
- FastAPI backend
- n8n workflow automation
- React frontend

---

## Key Features

### LLM-Powered Sales Agent

The system uses a Gemini-powered AI agent to understand customer requests and generate relevant responses.

The agent is designed to use available tools when an action is required instead of relying only on text generation.

### Retrieval-Augmented Generation

The project uses RAG to provide the AI agent with relevant information from a sales knowledge base.

The knowledge base contains information related to:

- Company information
- Products
- Pricing
- Sales capabilities

The RAG pipeline follows this process:

![RAG Pipeline](docs/architecture/rag-pipeline.png)



### AI Agent Tool Calling

The AI agent can call backend tools when required.

Current tools include:

- `check_demo_availability`
- `capture_lead`

This demonstrates an agent architecture where the LLM can determine when external functionality is required and request a tool call.

### Demo Availability Checking

Customers can request a product demonstration by providing a date and time.

The AI agent can call the calendar tool to check whether the requested time slot is available before providing a response.

### Lead Capture

The system can capture customer information and store it as a lead.

The lead data includes:

- Name
- Email
- Company
- Interest
- Status
- Created timestamp

### PostgreSQL Database

PostgreSQL is used to persist captured lead information.

### FastAPI Backend

FastAPI provides the backend API layer between the React frontend and the AI sales agent.

Main API endpoints include:

```text
GET  /
GET  /health
POST /chat
```

### n8n Workflow Automation

n8n is used for workflow orchestration around the AI sales system.

Example workflow:

![Example n8n Workflow](docs/architecture/example-workflow-n8n.png)



### React Frontend

A React-based frontend provides the customer-facing conversational interface with product, pricing, demo, and sales interactions.

---

## System Architecture

![System Architecture](docs/architecture/system-architecture.png)

---

## RAG Architecture

### Ingestion Pipeline

![Ingestion Pipeline](docs/architecture/ingestion-pipeline.png)

### Retrieval Pipeline

![Retrieval Pipeline](docs/architecture/retrieval-pipeline.png)

The system uses semantic similarity search to retrieve relevant knowledge before generating an answer.

---

## Agent Tool Calling Architecture

The AI agent has access to backend functions that can be executed when required.

### Calendar Tool

```text
check_demo_availability(
    date,
    time
)
```

The tool checks whether the requested demonstration slot is available.

### Lead Capture Tool

```text
capture_lead(
    name,
    email,
    company,
    interest
)
```

The tool saves lead information into PostgreSQL.

General agent workflow:

![General Agent Workflow](docs/architecture/general-agent-workflow.png)

---

## Technology Stack

### Backend

- Python
- FastAPI
- Uvicorn
- Google Gemini API
- python-dotenv

### AI and Generative AI

- Large Language Models
- Retrieval-Augmented Generation
- Gemini Embeddings
- FAISS
- Semantic Search
- AI Agent Tool Calling

### Database

- PostgreSQL
- Psycopg

### Frontend

- React
- Vite
- JavaScript
- CSS

### Automation

- n8n

### Development Tools

- Git
- GitHub
- Visual Studio Code
- PowerShell

---

## Project Structure

```text
ai_sales_agent/
|
+-- backend/
|   |
|   +-- app/
|       |
|       +-- agents/
|       |   |
|       |   +-- sales_agent.py
|       |
|       +-- api/
|       |
|       +-- database/
|       |
|       +-- rag/
|       |   |
|       |   +-- ingest.py
|       |   +-- retriever.py
|       |
|       +-- tools/
|       |   |
|       |   +-- calendar_tools.py
|       |   +-- lead_tools.py
|       |
|       +-- main.py
|       |
|       +-- requirements.txt
|
+-- data/
|   |
|   +-- knowledge/
|   |   |
|   |   +-- company_info.txt
|   |   +-- products.txt
|   |   +-- pricing.txt
|   |
|   +-- rag/
|
+-- frontend/
|   |
|   +-- src/
|   |   |
|   |   +-- App.jsx
|   |   +-- App.css
|   |   +-- main.jsx
|   |
|   +-- public/
|   +-- package.json
|   +-- vite.config.js
|
+-- n8n/
|
+-- tests/
|
+-- .env.example
+-- .gitignore
+-- README.md
```

---

## Installation and Setup

### Prerequisites

- Python 3.10+
- Node.js
- PostgreSQL
- Git
- n8n
- Google Gemini API key

### Backend Setup

#### 1. Clone the Repository

```bash
git clone <your-github-repository-url>
cd ai_sales_agent
```

#### 2. Create a Virtual Environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

#### 3. Install Python Dependencies

```powershell
pip install -r backend/requirements.txt
```

#### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=your_postgresql_connection_string
```

Do not commit `.env` to GitHub. The repository contains `.env.example` as a safe template.

#### 5. Configure PostgreSQL

Create the project database and configure the connection string in `.env`.

Example:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/ai_sales_agent
```

---

## Running the Backend

Navigate to the backend directory:

```powershell
cd backend
```

Activate the virtual environment if necessary:

```powershell
..\.venv\Scripts\Activate.ps1
```

Start FastAPI:

```powershell
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

Health endpoint:

```text
http://127.0.0.1:8000/health
```

---

## Running the Frontend

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

## Running n8n

The project uses n8n for workflow automation.

The workflow connects:

```text
Webhook
    |
    v
HTTP Request
    |
    v
AI Sales Backend
    |
    v
PostgreSQL
    |
    v
Respond to Webhook
```

The local n8n runtime and database files are intentionally excluded from the Git repository.

---

## Example Interactions

### Product Information

```text
User:
What products do you offer?

Agent:
Retrieves relevant information from the knowledge base
and generates a grounded response.
```

### Demo Availability

```text
User:
Can I book a demo tomorrow at 3 PM?

Agent:
Checks the requested date and time using the
demo availability tool and returns the result.
```

### Lead Capture

```text
User:
My name is John. My email is john@example.com.
I work at ABC Corp and I'm interested in AI automation.

Agent:
Captures the lead information and stores it in PostgreSQL.
```

---

## API Example

### Chat Request

```http
POST /chat
Content-Type: application/json
```

Request:

```json
{
  "message": "What products do you offer?"
}
```

Example response:

```json
{
  "response": "Our AI Sales Workforce Platform helps businesses automate repetitive sales and customer-engagement tasks using AI agents.",
  "lead_captured": null
}
```

The exact response can vary depending on the retrieved knowledge and agent behavior.

---

## Security

The project follows basic security practices for local development.

- API keys are stored in environment variables.
- `.env` is excluded from Git.
- Virtual environments are excluded from Git.
- Node modules are excluded from Git.
- Local n8n runtime data is excluded from Git.
- Generated local data is excluded where appropriate.
- Secrets and credentials are not stored in the repository.

Never commit API keys, database passwords, or other credentials to GitHub.

---

## Project Highlights

This project demonstrates practical experience with:

- Building LLM-powered applications
- Designing Retrieval-Augmented Generation pipelines
- Implementing vector similarity search
- Building AI agent workflows
- Implementing function and tool calling
- Integrating AI with backend services
- Developing REST APIs using FastAPI
- Persisting application data using PostgreSQL
- Building a React-based AI interface
- Integrating workflow automation using n8n
- Connecting multiple components into an end-to-end AI application

---

## Future Improvements

Potential production-level improvements include:

- Real calendar API integration
- Email automation
- CRM integration
- Authentication and authorization
- Conversation history
- Production vector database
- Automated testing
- Application monitoring
- Logging and observability
- Rate-limit handling
- Docker containerization
- Cloud deployment
- Human escalation and handoff
- Sales analytics dashboard

---

## Learning Outcomes

Through this project, the following areas were explored:

1. LLM application development
2. Retrieval-Augmented Generation
3. Embedding generation
4. Vector similarity search
5. AI agent tool calling
6. Backend API development
7. Database integration
8. Workflow automation
9. Frontend and backend integration
10. End-to-end AI application architecture

---

## Author

**Praveen Kumar D**

B.Sc. Information Technology

AI / Machine Learning / Generative AI

GitHub: https://github.com/Pravin232004

LinkedIn: https://linkedin.com/in/pravin-kd-a29993408

---

## License

This project is intended for educational, portfolio, and demonstration purposes.
