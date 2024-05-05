from fastapi import FastAPI

# appを定義
app = FastAPI(title="App")
feature_app = FastAPI(title="App(/feature)")
admin_app = FastAPI(title="App(/admin)")


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


# BaseとなるAppに他のappをmountする
app.mount("/feature", feature_app)
app.mount("/admin", admin_app)


APP_PATH_LIST = ["", "/feature", "/admin"]


# Swagger間のリンクを作成
def _make_app_docs_link_html(app_path: str, app_path_list: list[str]) -> str:
    """swaggerの上部に表示する各Appへのリンクを生成する"""
    descriptions = [
        f"<a href='{path}/docs'>{path}/docs</a>" if path != app_path else f"{path}/docs"
        for path in app_path_list
    ]
    descriptions.insert(0, "Apps link")
    return "<br>".join(descriptions)


app.description = _make_app_docs_link_html("", APP_PATH_LIST)
feature_app.description = _make_app_docs_link_html("/feature", APP_PATH_LIST)
admin_app.description = _make_app_docs_link_html("/admin", APP_PATH_LIST)
