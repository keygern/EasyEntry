from fastapi import APIRouter, Depends
from .auth import verify_supabase_jwt
from sqlmodel import Session, select
from db import engine
from models import UserPlan

router = APIRouter(prefix="/user", tags=["user"])

@router.get("")
def get_user(user_id: str = Depends(verify_supabase_jwt)):
    with Session(engine) as db:
        rec = db.exec(select(UserPlan).where(UserPlan.user_id == user_id)).first()
        if not rec:
            rec = UserPlan(user_id=user_id)
            db.add(rec)
            db.commit()
            db.refresh(rec)
    return {"plan": rec.plan, "quota_remaining": rec.quota_remaining}
