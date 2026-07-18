from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import base64
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Funzione per recuperare il titolo del film e formattarlo esattamente come il sito
async def get_movie_title(imdb_id: str) -> str:
    url = f"https://v3-cinemeta.strem.io/meta/movie/{imdb_id}.json"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=5.0)
            data = response.json()
            name = data["meta"]["name"]
            
            # Formattazione: minuscolo, spazi in trattini, rimozione caratteri speciali comuni
            slug = name.lower().strip()
            slug = slug.replace(" ", "-").replace(":", "").replace("'", "").replace(".", "").replace("!", "").replace("?", "")
            return slug
    except:
        return ""

@app.get("/")
async def read_index():
    # Assicurati di avere un file index.html nella stessa cartella
    try:
        with open("index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except:
        return HTMLResponse(content="<h1>Configuratore Browser Opener attivo</h1>")

@app.get("/{config}/manifest.json")
async def get_manifest(config: str):
    return {
        "id": "community.browser.opener",
        "version": "1.0.4",
        "name": "Guardaplay Browser Opener",
        "resources": ["stream"],
        "types": ["movie", "series"],
        "idPrefixes": ["tt"]
    }

@app.get("/{config}/stream/{type}/{imdb_id}.json")
async def get_stream(config: str, type: str, imdb_id: str):
    try:
        # Decodifica l'URL del sito base (es: https://guardaplay.store)
        base_url = base64.b64decode(config).decode('utf-8').rstrip('/')
    except:
        return {"streams": []}
    
    slug = await get_movie_title(imdb_id)
    
    # Costruzione URL esatta basata sul tuo esempio: /film/titolo/
    target_url = f"{base_url}/film/{slug}/"
    
    return {
        "streams": [
            {
                "name": "Guardaplay Browser",
                "title": "Avvia film nel browser",
                "externalUrl": target_url,
                "behaviorHints": {
                    "notWebReady": True
                }
            }
        ]
    }