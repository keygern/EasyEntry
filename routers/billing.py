from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import JSONResponse
import os, stripe, logging

stripe.api_key = os.getenv("STRIPE_SK")
STRIPE_WH_SECRET = os.getenv("STRIPE_WH_SECRET")

router = APIRouter(prefix="/billing")
logger = logging.getLogger("billing")
logging.basicConfig(level=logging.INFO)

@router.post("/webhook")
async def stripe_hook(request: Request):
    payload = await request.body()
    sig     = request.headers.get("stripe-signature")

    # ── 1. verify signature ─────────────────────────────
    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WH_SECRET)
    except Exception:
        # covers missing header or bad signature
        return JSONResponse({"error": "Bad signature"}, status_code=400)

    # ── 2. act on event type ────────────────────────────
    if event["type"] == "checkout.session.completed":
        s = event["data"]["object"]

        # accept email from either field
        email = s.get("customer_email") or s.get("customer_details", {}).get("email")
        if not email:
            logger.warning("Checkout session without email; skipping DB write")
            return {"received": True}

        # (DB code is commented until User model exists)
        # with Session() as db:
        #     ...

        logger.info(f"✅ payment confirmed for {email}")

    # ── 3. always return 200 so Stripe stops retrying ───
    return {"received": True}
