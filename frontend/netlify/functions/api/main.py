from mangum import Mangum
from app.main import app

def handler(event, context):
    asgi_handler = Mangum(app, lifespan="off")
    return asgi_handler(event, context)
