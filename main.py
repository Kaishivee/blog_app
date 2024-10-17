from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from routers import posts_crud, register
from fastapi.staticfiles import StaticFiles

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="templates"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request) -> RedirectResponse:
    return RedirectResponse(url="/user/login")


@app.get("/my_blog", response_class=HTMLResponse)
async def blog(request: Request):
    return templates.TemplateResponse("page_blog.html", {'request': request})


app.include_router(posts_crud.router)
app.include_router(register.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)