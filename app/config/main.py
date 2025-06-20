from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from google.cloud import firestore

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = firestore.Client()
