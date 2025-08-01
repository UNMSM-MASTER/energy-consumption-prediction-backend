from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from decouple import config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = config("SECRET_KEY", default="your-secret-key-here")
