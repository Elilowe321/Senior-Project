import uvicorn
from fastapi import FastAPI
from api_stuff.routers.cfb_model_router import router as cfb_model_router
from api_stuff.routers.auth_router import router as auth_router
from api_stuff.routers.cfb_games_router import router as game_router

app = FastAPI()

app.include_router(game_router, prefix="/games", tags=["games"])

app.include_router(cfb_model_router, prefix="/cfb", tags=["cfb"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])


if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)
