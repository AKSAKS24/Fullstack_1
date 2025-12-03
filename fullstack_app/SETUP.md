# Setup Instructions

Follow these steps to run the full‑stack AI agents application locally.  The backend is built with FastAPI and Celery while the frontend uses React + Vite.  A Redis instance is required for background task queuing.

## Prerequisites

* **Python 3.9+**
* **Node.js 18+** with npm
* **Redis** running locally on `localhost:6379`

## Backend Setup

1. Navigate to the backend directory:

   ```bash
   cd fullstack_app/backend
   ```

2. (Optional) Create a virtual environment and activate it:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install backend dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and provide your OpenAI API key if you plan to use OpenAI models:

   ```bash
   echo "OPENAI_API_KEY=sk-..." > .env
   ```

5. Start the FastAPI server (it listens on port **8000** by default):

   ```bash
   uvicorn src.main:app --reload
   ```

6. In a separate terminal (with the virtual environment activated), start the Celery worker.  Ensure Redis is running:

   ```bash
   celery -A celery_app.celery_app worker --loglevel=info
   ```

## Frontend Setup

1. Navigate to the frontend directory:

   ```bash
   cd fullstack_app/frontend
   ```

2. Install frontend dependencies:

   ```bash
   npm install
   ```

3. Start the development server:

   ```bash
   npm run dev
   ```

4. Open your browser at `http://localhost:5173` to use the application.  The frontend proxies API requests to `http://localhost:8000`.

## Connecting Both Parts

* Ensure the backend is running on port 8000 and the Celery worker is connected to the same Redis instance.
* The frontend, via Vite, proxies API calls to the backend based on the paths configured in `vite.config.js`.

## Environment Variables

The backend reads configuration from environment variables.  Important variables include:

| Variable | Description |
|---------|-------------|
| `OPENAI_API_KEY` | API key for OpenAI models |
| `CELERY_BROKER_URL` | URL of the Redis broker (default: `redis://localhost:6379/0`) |
| `CELERY_RESULT_BACKEND` | URL for result backend (default: same as broker) |

You may define these variables in a `.env` file at the project root.  The application uses `python-dotenv` to load them automatically.

## Testing

* After both backend and frontend are running, open the UI and send a message.  You should see responses generated from the selected model.
* To test the TSD agent:
  1. Select **tsd** from the agent dropdown.
  2. Upload a PDF, DOCX or other supported file.
  3. Enter additional instructions if needed and send the request.  The agent will process each section and return a DOCX file link.
* To test the ABAP agent:
  1. Select **abap** from the agent dropdown.
  2. Type natural language instructions such as "Write an ABAP program to read a CSV file and display its contents".
  3. The agent returns ABAP code.  Add words like "explanation" in your prompt to receive an explanation as well.

## Linting & Formatting

* Backend code follows PEP8 and is type‑annotated where possible.  Use `flake8` and `black` for linting and formatting.
* Frontend code uses ESLint (you can configure your own rules) and Prettier for formatting.