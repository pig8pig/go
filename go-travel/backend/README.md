# go. Backend

FastAPI backend for the go. travel planner.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
```

2. Activate virtual environment:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file from `.env.example`:
```bash
cp .env.example .env
```

5. Run the server:
```bash
python main.py
# or
uvicorn main:app --reload
```

Server runs at: http://localhost:8000

## API Endpoints

- `GET /` - Status check
- `POST /generate` - Generate travel itinerary
- `GET /health` - Health check

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
