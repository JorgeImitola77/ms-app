import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

# Configurar logs para documentar errores
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Transformar la URL de psycopg2 a asyncpg
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# 1. Engine async con pool de conexiones (Requerimiento)
engine = create_async_engine(
    DATABASE_URL,
    echo=False,           # Pon en True si quieres ver las consultas SQL en la terminal
    pool_size=5,          # Conexiones base
    max_overflow=10,      # Conexiones extra si hay mucho tráfico
    pool_timeout=30       # Segundos de espera antes de dar error por saturación
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 2. Dependencia para FastAPI (Requerimiento)
async def get_db():
    """Generador de sesiones asíncronas para inyectar en los endpoints."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            logger.error(f"Error en la transacción de base de datos: {str(e)}")
            await session.rollback()
            raise
        finally:
            await session.close()

# 3. Función helper para consultas con manejo de errores documentado (Requerimiento)
async def execute_query_with_error_handling(session: AsyncSession, query, params=None):
    """Ejecuta una consulta atrapando y documentando errores de base de datos."""
    try:
        result = await session.execute(query, params)
        return result
    except SQLAlchemyError as e:
        logger.error(f"Excepción crítica al ejecutar query: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor de base de datos")