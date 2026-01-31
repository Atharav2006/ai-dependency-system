from mangum import Mangum
from app.main import app

# This is the handler that Netlify/AWS Lambda will call
handler = Mangum(app, lifespan="off")
