from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import base64
import httpx
import os
import uvicorn

app = FastAPI()

# Middleware CORS per permettere l'accesso da Stremio
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Funzione per recuperare il titolo del film
async def get_movie_title(imdb_id: str) -> str:
    url = f"https://v3-cinemeta.strem.io/meta/movie/{imdb_id}.json"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            data = response.json()
            name = data["meta"]["name"]
            
            # Formattazione slug
            slug = name.lower().strip()
            slug = slug.replace(" ", "-").replace(":", "").replace("'", "").replace(".", "").replace("!", "").replace("?", "")
            return slug
    except:
        return ""

@app.get("/")
async def read_index():
    # Verifica la presenza di index.html
    if os.path.exists("index.html"):
        with open("index.html", "r") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Guardaplay Browser Opener è attivo</h1>")

@app.get("/{config}/manifest.json")
async def get_manifest(config: str):
    return {
        "id": "community.browser.opener",
        "version": "1.0.4",
        "name": "Diego🔥Browser",
        "resources": ["stream"],
        "types": ["movie", "series"],
        "idPrefixes": ["tt"]
    }

@app.get("/{config}/stream/{type}/{imdb_id}.json")
async def get_stream(config: str, type: str, imdb_id: str):
    try:
        base_url = base64.b64decode(config).decode('utf-8').rstrip('/')
    except:
        return {"streams": []}
    
    slug = await get_movie_title(imdb_id)
    target_url = f"{base_url}/film/{slug}/"
    
    return {
        "streams": [
            {
                "name": "Guardaplay",
                "title": "Avvia film nel browser",
                "externalUrl": target_url,
                "behaviorHints": {
                    "notWebReady": True
                }
            }
        ]
    }

# Blocco fondamentale per avviare il server su Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
    
