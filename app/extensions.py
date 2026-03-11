from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask import request

csrf = CSRFProtect()
limiter = Limiter(key_func=lambda: request.remote_addr, default_limits=["200 per day", "50 per hour"])
