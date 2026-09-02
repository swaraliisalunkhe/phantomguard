# PhantomGuard

PhantomGuard is an advanced AI-driven payment fraud detection system that utilizes a multi-model architecture (XGBoost, TCN, GraphSAGE, and a Meta-Classifier) and LLM-based threat generation.

## Setup

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   pip install -r requirements.txt
   ```

2. Copy the `.env.example` file to `.env` and fill in your Gemini API Key:
   ```bash
   cp .env.example .env
   ```

## Running Locally

Start the backend API using Uvicorn:
```bash
uvicorn main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

## Deployment

The project is configured for deployment on Render. It includes a `render.yaml` Blueprint file. Connect your GitHub repository to Render and use the Blueprint deployment method.
