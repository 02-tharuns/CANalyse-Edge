import uvicorn
from canalyse.config import settings

if __name__ == "__main__":
    uvicorn.run("canalyse.api:app", host=settings.host, port=settings.port)

