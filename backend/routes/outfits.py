from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from middleware.auth import require_auth
from services import db_services
from services.gemini_services import analyse_outfit, get_suggestions

router = APIRouter(tags=["outfits"])


class UploadUrlRequest(BaseModel):
    filename: str


class AnalyseRequest(BaseModel):
    image_url: str


class SuggestionsRequest(BaseModel):
    analysis_id: str
    selected_vibe: str
    image_url: str


@router.post("/outfits/upload-url")
def get_upload_url(request: UploadUrlRequest, current_user=Depends(require_auth)):
    path = db_services.create_upload_path(current_user.id, request.filename)
    signed = db_services.supabase.storage.from_("outfits").create_signed_upload_url(path)

    return {
        "upload_url": signed["signedURL"],
        "public_url": db_services.public_url_for(path),
    }


@router.post("/analyse-outfit")
async def analyse_outfit_route(request: AnalyseRequest, current_user=Depends(require_auth)):
    try:
        result = await analyse_outfit(request.image_url)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"AI returned invalid JSON: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    outfit_id = db_services.save_outfit(current_user.id, request.image_url)
    analysis_id = db_services.save_analysis(outfit_id, result["pieces"], result["vibes"])

    return {"analysis_id": analysis_id, **result}


@router.post("/get-suggestions")
async def get_suggestions_route(request: SuggestionsRequest, current_user=Depends(require_auth)):
    analysis = db_services.get_analysis(request.analysis_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")

    outfit = db_services.get_outfit(analysis["outfit_id"])
    if outfit is None or outfit["user_id"] != current_user.id:
        raise HTTPException(status_code=404, detail="Analysis not found")

    vibe = next(
        (v for v in analysis["vibes_json"] if v["name"] == request.selected_vibe),
        None,
    )
    if vibe is None:
        raise HTTPException(status_code=400, detail="selected_vibe does not match this analysis")

    try:
        result = await get_suggestions(
            request.image_url,
            analysis["pieces_json"],
            vibe["name"],
            vibe["tags"],
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"AI returned invalid JSON: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    db_services.save_suggestion(request.analysis_id, request.selected_vibe, result)
    return result


@router.get("/outfits/history")
def get_history(current_user=Depends(require_auth)):
    return {"outfits": db_services.get_outfit_history(current_user.id)}
