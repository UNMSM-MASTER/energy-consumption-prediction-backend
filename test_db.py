from app.config.database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('Database connection test:', result.scalar())
        print('Database connection successful!')
except Exception as e:
    print('Database connection failed:', e) 