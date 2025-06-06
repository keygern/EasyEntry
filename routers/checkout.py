# routers/checkout.py
import os, stripe
from fastapi import APIRouter, HTTPException, Depends
from .auth import verify_supabase_jwt

stripe.api_key = os.getenv("STRIPE_SK")
router = APIRouter(prefix="/checkout", tags=["checkout"], dependencies=[Depends(verify_supabase_jwt)])

PRICE_IDS = {          # copy from Stripe dashboard
    "hobby":   "price_1RShI44CX61ljtwHs6hCNWUB",
    "growth":  "price_1RShIW4CX61ljtwHs1XpbP8N",
    "pro":     "price_1RSjgs4CX61ljtwH22W3pqzF",
}

@router.post("/{plan}")
def create_session(plan: str):
    if plan not in PRICE_IDS:
        raise HTTPException(404, "plan not found")

    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": PRICE_IDS[plan], "quantity": 1}],
        success_url="https://easyentry.vercel.app/success?session_id={CHECKOUT_SESSION_ID}",
        cancel_url="https://easyentry.vercel.app/cancel",
        automatic_tax={"enabled": False},
    )
    return {"url": session.url}
