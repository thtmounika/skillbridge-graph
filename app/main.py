from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import db, queries

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="SkillBridge Graph", version="1.0.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


def run(query, **params):
    with db.session() as s:
        return [record.data() for record in s.run(query, **params)]


@app.get("/")
def index():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/api/health")
def health():
    try:
        db.verify_connection()
        return {"ok": True, "database": "connected"}
    except Exception as exc:
        return {"ok": False, "database": "unavailable", "message": str(exc)}


@app.get("/api/roles")
def roles():
    try:
        return run(queries.ROLES)
    except Exception as exc:
        raise HTTPException(503, f"Database unavailable: {exc}")


@app.get("/api/roles/{role_id}")
def role_detail(role_id: str):
    try:
        rows = run(queries.ROLE_DETAIL, role_id=role_id)
        if not rows:
            raise HTTPException(404, "Role not found")
        return rows[0]
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(503, f"Database unavailable: {exc}")


@app.get("/api/profile/{person_id}")
def profile(person_id: str):
    try:
        rows = run(queries.PROFILE, person_id=person_id)
        if not rows:
            raise HTTPException(404, "Profile not found")
        return rows[0]
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(503, f"Database unavailable: {exc}")


@app.get("/api/profile/{person_id}/gaps/{role_id}")
def skill_gap(person_id: str, role_id: str):
    try:
        return run(queries.SKILL_GAP, person_id=person_id, role_id=role_id)
    except Exception as exc:
        raise HTTPException(503, f"Database unavailable: {exc}")


@app.get("/api/profile/{person_id}/recommendations")
def recommendations(person_id: str):
    try:
        return run(queries.RECOMMEND_ROLES, person_id=person_id)
    except Exception as exc:
        raise HTTPException(503, f"Database unavailable: {exc}")


@app.get("/api/profile/{person_id}/learning-path/{role_id}")
def learning_path(person_id: str, role_id: str):
    try:
        return run(queries.LEARNING_PATH, person_id=person_id, role_id=role_id)
    except Exception as exc:
        raise HTTPException(503, f"Database unavailable: {exc}")


@app.get("/api/profile/{person_id}/graph")
def graph(person_id: str):
    try:
        return run(queries.GRAPH, person_id=person_id)
    except Exception as exc:
        raise HTTPException(503, f"Database unavailable: {exc}")


@app.on_event("shutdown")
def shutdown():
    db.close()
