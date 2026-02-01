from mangum import Mangum
from app.main import app

# Handler for Netlify
handler = Mangum(app, lifespan="off")
