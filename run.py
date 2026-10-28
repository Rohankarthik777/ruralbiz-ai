import uvicorn
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"Starting RuralBiz AI Server on http://{host}:{port} (Local: http://127.0.0.1:{port}) ...")
    uvicorn.run("app.main:app", host=host, port=port, reload=False)
