from .billing import router as billing_router
from .checkout import router as checkout_router
from .documents import router as documents_router
from .user import router as user_router

all_routers = [billing_router, checkout_router, documents_router, user_router]
