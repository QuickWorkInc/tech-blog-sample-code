from app_manager import FastAPIAppManager
from fastapi import FastAPI

# appを定義
app = FastAPI(title="App")
feature_app = FastAPI()
admin_app = FastAPI()
app_manager = FastAPIAppManager(root_app=app)


# Path関数を定義
@app.get("/")
def base_app_root():
    return {"message": "Hello World", "app": "base"}


@feature_app.get("/")
def feature_app_root():
    return {"message": "Hello World", "app": "feature"}


@admin_app.get("/")
def admin_app_root():
    return {"message": "Hello World", "app": "admin"}


# FastAPIAppManagerにappを追加することで、Linkの自動生成を行う
app_manager.add_app(path="/feature", app=feature_app)
app_manager.add_app(path="/admin", app=admin_app)
app_manager.setup_apps_docs_link()
