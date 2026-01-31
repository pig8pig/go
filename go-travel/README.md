# go. - Extreme Minimalist Travel Planner

Philosophy: **Occam's Razor** - Extreme minimalism. Single input. No login. No settings. Brutalist black-and-white aesthetic.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v18.17 or higher) - [Download](https://nodejs.org/)
- **npm** (comes with Node.js)
- **Python** (v3.8 or higher) - [Download](https://www.python.org/downloads/)
- **Git** - [Download](https://git-scm.com/)

## Project Structure

```
go-travel/
├── frontend/          # Next.js 14+ (App Router)
│   ├── app/          # Next.js App Router pages
│   ├── components/   # React components
│   └── package.json
├── backend/          # Python FastAPI
│   ├── main.py      # FastAPI application
│   └── requirements.txt
├── .gitignore
├── go.code-workspace
└── README.md
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd go-travel
```

### 2. Frontend Setup

Navigate to the frontend directory and install dependencies:

```bash
cd frontend
npm install
```

**Installed packages:**
- `next` (v14.1.0+) - React framework
- `react` & `react-dom` (v18.2.0+)
- `typescript` - Type safety
- `tailwindcss` - Utility-first CSS
- `framer-motion` - Animations
- `lucide-react` - Icon library

### 3. Backend Setup

Navigate to the backend directory:

```bash
cd ../backend
```

Create and activate a virtual environment:

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

**Installed packages:**
- `fastapi` - Modern web framework
- `uvicorn` - ASGI server
- `python-dotenv` - Environment variables
- `requests` - HTTP library
- `openai` - OpenAI API client
- `pydantic` - Data validation

Create environment file:

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your API keys
# OPENAI_API_KEY=your_key_here
```

## Running the Application

### Start the Frontend

```bash
cd frontend
npm run dev
```

Frontend runs at: **http://localhost:3000**

### Start the Backend

In a separate terminal:

```bash
cd backend

# Activate venv first (if not already activated)
# Windows: .\venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

python main.py
```

Backend API runs at: **http://localhost:8000**

API Documentation: **http://localhost:8000/docs**

## Tech Stack

### Frontend
- **Next.js 14+** - React framework with App Router
- **TypeScript** - Strict type checking
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** - Animation library
- **Lucide React** - Icon set

### Backend
- **FastAPI** - Python web framework
- **Uvicorn** - ASGI server
- **OpenAI API** - AI integration
- **Pydantic** - Data validation

## Development

### Frontend Development
```bash
npm run dev      # Start dev server
npm run build    # Build for production
npm run start    # Start production server
npm run lint     # Run ESLint
```

### Backend Development
```bash
python main.py                    # Start server
uvicorn main:app --reload         # Start with auto-reload
uvicorn main:app --reload --port 8000  # Custom port
```

## Troubleshooting

**Frontend errors after cloning:**
- Run `npm install` in the frontend directory
- Restart VS Code or run "TypeScript: Restart TS Server" from command palette

**Backend import errors:**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`
- Check Python interpreter in VS Code matches venv path

**Port already in use:**
- Frontend: Change port with `npm run dev -- -p 3001`
- Backend: Change port in `main.py` or use `uvicorn main:app --port 8001`

## Philosophy

One input. One result. Zero friction. Pure functionality.

**go.**
