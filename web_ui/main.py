from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from analytics_service import get_analytics_generator
import json
import asyncio

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/analyze")
async def analyze(username: str):
    async def event_generator():
        # Running the synchronous generator in a separate thread to not block the event loop
        # For simplicity, we just iterate here. In a heavy load app, use run_in_executor.
        for item in get_analytics_generator(username):
            yield json.dumps(item) + "\n"
            # Small delay to ensure the frontend can keep up and show progress
            await asyncio.sleep(0.01)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
