from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
import os, stripe, logging
from db import engine
from models import UserPlan

stripe.api_key = os.getenv("STRIPE_SK")
STRIPE_WH_SECRET = os.getenv("STRIPE_WH_SECRET")

router = APIRouter(prefix="/billing", tags=["billing"])
logger = logging.getLogger("billing")
logging.basicConfig(level=logging.INFO)

PLAN_QUOTAS = {"hobby": 5, "growth": 50, "pro": None}

@router.post("/webhook")
async def stripe_hook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WH_SECRET)
    except Exception:
        return JSONResponse({"error": "Bad signature"}, status_code=400)

    if event["type"] == "checkout.session.completed":
        data = event["data"]["object"]
        user_id = data.get("client_reference_id")
        plan = data.get("metadata", {}).get("plan")
        if user_id and plan in PLAN_QUOTAS:
            quota = PLAN_QUOTAS[plan] or 0
            with Session(engine) as db:
                rec = db.exec(select(UserPlan).where(UserPlan.user_id == user_id)).first()
                if rec:
                    rec.plan = plan
                    rec.quota_remaining = quota
                else:
                    rec = UserPlan(user_id=user_id, plan=plan, quota_remaining=quota)
                db.add(rec)
                db.commit()
            logger.info("Updated plan for %s to %s", user_id, plan)

    if event["type"] in {"invoice.payment_failed", "customer.subscription.deleted"}:
        sub = event["data"]["object"]
        user_id = sub.get("client_reference_id") or sub.get("customer_email")
        if user_id:
            with Session(engine) as db:
                rec = db.exec(select(UserPlan).where(UserPlan.user_id == user_id)).first()
                if rec:
                    rec.plan = "hobby"
                    rec.quota_remaining = PLAN_QUOTAS["hobby"]
                    db.add(rec)
                    db.commit()
            logger.info("Downgraded %s to hobby", user_id)

    return {"received": True}
