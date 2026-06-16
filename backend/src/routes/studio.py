"""Layout Studio API — build/browse a use-case-indexed library of candidate
ModuleConfig layouts, and promote chosen ones into the generation seed pool."""
import json

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src import db, semantic_cache
from src.schema import ModuleConfig
from src.services import studio

router = APIRouter(prefix="/studio")


class StudioUseCase(BaseModel):
    key: str
    title: str
    icon: str | None = None
    accent: str | None = None
    apps: list[str] = []
    count: int = 0


class StudioLayout(BaseModel):
    id: str | None = None
    use_case: str
    label: str
    inspired_by: str | None = None
    config: ModuleConfig
    created_at: str | None = None


class PromoteResponse(BaseModel):
    ok: bool
    seed_prompt: str
    library: dict


def _row_to_layout(r) -> StudioLayout:
    return StudioLayout(
        id=r["id"], use_case=r["use_case"], label=r["label"], inspired_by=r["inspired_by"],
        config=ModuleConfig.model_validate_json(r["config_json"]), created_at=r["created_at"],
    )


@router.get("/use-cases", response_model=list[StudioUseCase])
def list_use_cases() -> list[StudioUseCase]:
    counts = db.layout_counts()
    return [
        StudioUseCase(key=u["key"], title=u["title"], icon=u.get("icon"),
                      accent=u.get("accent"), apps=u.get("apps", []),
                      count=counts.get(u["key"], 0))
        for u in studio.use_cases()
    ]


@router.post("/use-cases/{key}/generate", response_model=list[StudioLayout])
def generate(key: str, n: int = Query(default=4, ge=1, le=8)) -> list[StudioLayout]:
    """Mine N candidate layouts for a use case (modelled after leading apps) and
    store them in the library."""
    if studio.get_use_case(key) is None:
        raise HTTPException(status_code=404, detail=f"Unknown use case: {key}")
    layouts = studio.generate_layouts(key, n)
    stored: list[StudioLayout] = []
    for ly in layouts:
        lid = db.layout_add(key, ly["label"], ly.get("inspired_by"), json.dumps(ly["config"]))
        stored.append(StudioLayout(id=lid, use_case=key, label=ly["label"],
                                   inspired_by=ly.get("inspired_by"),
                                   config=ModuleConfig.model_validate(ly["config"])))
    return stored


@router.get("/layouts", response_model=list[StudioLayout])
def list_layouts(use_case: str | None = Query(default=None)) -> list[StudioLayout]:
    return [_row_to_layout(r) for r in db.layout_list(use_case)]


@router.delete("/layouts/{layout_id}", status_code=204)
def delete_layout(layout_id: str) -> None:
    if not db.layout_delete(layout_id):
        raise HTTPException(status_code=404, detail="Layout not found")


@router.post("/layouts/{layout_id}/promote", response_model=PromoteResponse)
def promote_layout(layout_id: str) -> PromoteResponse:
    """Add a layout to the main app's generation seed pool, so future generations
    for this use case draw on it (the 'upload template ideas' connection)."""
    row = db.layout_get(layout_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Layout not found")
    uc = studio.get_use_case(row["use_case"])
    seed_prompt = (uc.get("seed_prompts") or [row["label"]])[0] if uc else row["label"]
    config = json.loads(row["config_json"])
    semantic_cache.store("system", seed_prompt, [config])
    return PromoteResponse(ok=True, seed_prompt=seed_prompt, library=db.cache_stats())
