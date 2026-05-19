from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Date, DateTime, Integer, Text, text

Base = declarative_base()

class PersonaORM(Base):
    __tablename__ = 'personas'

    nro_documento = Column(String(10), primary_key=True)
    tipo_documento = Column(String(30), nullable=False)
    primer_nombre = Column(String(30), nullable=False)
    segundo_nombre = Column(String(30))
    apellidos = Column(String(60), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    genero = Column(String(20), nullable=False)
    correo = Column(String(100), nullable=False)
    celular = Column(String(10), nullable=False)
    foto_ruta = Column(String(255))
    fecha_registro = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

class LogORM(Base):
    __tablename__ = 'logs'

    id_log = Column(Integer, primary_key=True, autoincrement=True)
    fecha_transaccion = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    tipo_transaccion = Column(String(50), nullable=False)
    documento_relacionado = Column(String(10))
    detalle = Column(Text, nullable=False)