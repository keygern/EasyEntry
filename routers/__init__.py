#from .auth import router as auth_router 
from .billing import router as billing_router
from .entry import router as entry_router
from .auth import verify_supabase_jwt

all_routers = [billing_router, entry_router]

