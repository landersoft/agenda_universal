"""
⚙️ CONFIGURACIÓN DE LA APLICACIÓN AGENDA UNIVERSAL

📚 ¿QUÉ HACE ESTE ARCHIVO?
- Lee las variables del archivo .env (como MONGO_URI, FLASK_ENV, etc.)
- Organiza las configuraciones por ambiente (desarrollo, producción, testing)
- Valida que todo esté configurado correctamente
- Proporciona valores por defecto seguros

💡 ANALOGÍA: Es como un "traductor" que toma las variables del .env y las organiza
"""

import os
from dotenv import load_dotenv
import logging

# Cargar variables de entorno desde archivo .env
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """
    🏗️ CONFIGURACIÓN BASE (común para todos los ambientes)

    ¿Para qué sirve?
    - Define configuraciones que son iguales en desarrollo, testing y producción
    - Lee las variables que definiste en tu .env
    - Proporciona valores por defecto si algo falta
    """

    # 🚀 CONFIGURACIONES DE FLASK (las que ya tienes en .env)
    FLASK_APP = os.getenv("FLASK_APP", "app:create_app")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")

    # 🗄️ BASE DE DATOS (usando tu configuración actual)
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:admin123@mongodb:27017")

    # 🔐 SEGURIDAD (nuevas variables que deberías agregar a tu .env)
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-cambiar-en-produccion")

    # 📝 CONFIGURACIÓN DE LOGGING
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # 🌐 CONFIGURACIÓN DE SERVIDOR
    FLASK_DEBUG = (
        os.getenv(
            "FLASK_DEBUG", "True" if FLASK_ENV == "development" else "False"
        ).lower()
        == "true"
    )
    FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
    FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")

    # 📄 CONFIGURACIÓN DE PAGINACIÓN (para cuando tengas muchos doctores/pacientes)
    DEFAULT_PAGE_SIZE = int(os.getenv("DEFAULT_PAGE_SIZE", "10"))
    MAX_PAGE_SIZE = int(os.getenv("MAX_PAGE_SIZE", "50"))

    # ⏱️ TIMEOUTS (tiempos límite)
    DB_TIMEOUT = int(os.getenv("DB_TIMEOUT", "30"))  # segundos para conectar a MongoDB
    REQUEST_TIMEOUT = int(
        os.getenv("REQUEST_TIMEOUT", "60")
    )  # segundos para requests HTTP

    # 🔒 CORS (para que el frontend pueda conectarse)
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

    # 🏥 CONFIGURACIONES ESPECÍFICAS DE LA AGENDA MÉDICA
    MAX_CITAS_POR_DIA = int(os.getenv("MAX_CITAS_POR_DIA", "20"))
    DURACION_CITA_DEFAULT = int(os.getenv("DURACION_CITA_DEFAULT", "30"))  # minutos
    HORARIO_APERTURA = os.getenv("HORARIO_APERTURA", "08:00")
    HORARIO_CIERRE = os.getenv("HORARIO_CIERRE", "20:00")

    @staticmethod
    def validate():
        """
        ✅ VALIDADOR DE CONFIGURACIÓN

        ¿Para qué sirve?
        - Verifica que tu .env tenga todo lo necesario
        - Valida que los valores tengan sentido
        - Te avisa si falta algo importante

        ¿Cuándo se ejecuta?
        - Al iniciar la aplicación
        - Te ayuda a detectar problemas de configuración temprano
        """
        logger.info("🔍 Validando configuración...")

        # Verificar que existe MONGO_URI
        if not Config.MONGO_URI:
            raise ValueError("❌ MONGO_URI no está configurado. Revisar archivo .env")

        # Verificar formato de MONGO_URI
        if not Config.MONGO_URI.startswith("mongodb://"):
            raise ValueError("❌ MONGO_URI debe empezar con mongodb://")

        # Advertencia sobre SECRET_KEY en desarrollo
        if Config.SECRET_KEY == "dev-key-cambiar-en-produccion":
            if Config.FLASK_ENV == "production":
                raise ValueError("❌ Debes cambiar SECRET_KEY en producción")
            else:
                logger.warning("⚠️ Usando SECRET_KEY por defecto (OK para desarrollo)")

        # Validar configuraciones numéricas
        if Config.DEFAULT_PAGE_SIZE <= 0:
            raise ValueError("❌ DEFAULT_PAGE_SIZE debe ser mayor a 0")

        if Config.MAX_PAGE_SIZE < Config.DEFAULT_PAGE_SIZE:
            raise ValueError("❌ MAX_PAGE_SIZE debe ser mayor que DEFAULT_PAGE_SIZE")

        # Validar horarios de la clínica
        try:
            from datetime import datetime

            datetime.strptime(Config.HORARIO_APERTURA, "%H:%M")
            datetime.strptime(Config.HORARIO_CIERRE, "%H:%M")
        except ValueError:
            raise ValueError(
                "❌ HORARIO_APERTURA y HORARIO_CIERRE deben ser formato HH:MM (ej:08:00)"
            )

        logger.info("✅ Configuración válida")


class DevelopmentConfig(Config):
    """
    🔧 CONFIGURACIÓN PARA DESARROLLO (tu ambiente actual)

    ¿Cuándo se usa?
    - Cuando FLASK_ENV=development (como tienes en tu .env)
    - Para desarrollo local con Docker
    - Cuando estás programando y testeando

    ¿Qué tiene de especial?
    - DEBUG activado (muestra errores detallados)
    - Logs más verbosos para debugging
    - Validaciones más permisivas
    - Base de datos usando tu Docker MongoDB
    """

    DEBUG = True
    TESTING = False

    # Usar exactamente tu configuración de MongoDB con Docker
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:admin123@mongodb:27017")

    # En desarrollo, SECRET_KEY puede ser simple
    SECRET_KEY = os.getenv("SECRET_KEY", "desarrollo-agenda-universal-2025")

    # Logging más detallado para desarrollo
    LOG_LEVEL = "DEBUG"

    # CORS permisivo para desarrollo (permite conexiones desde cualquier origen)
    CORS_ORIGINS = ["*"]

    @staticmethod
    def validate():
        """Validación específica para desarrollo"""
        logger.info("🔧 Validando configuración de DESARROLLO...")

        # Ejecutar validaciones base
        Config.validate()

        # Verificar que MongoDB esté disponible (tu container Docker)
        if "mongodb" not in DevelopmentConfig.MONGO_URI:
            logger.warning(
                "⚠️ MONGO_URI no apunta a container 'mongodb'. ¿Docker corriendo?"
            )

        # Verificar credenciales de MongoDB
        if "admin:admin123" not in DevelopmentConfig.MONGO_URI:
            logger.warning("⚠️ Credenciales de MongoDB diferentes a las esperadas")

        logger.info("✅ Configuración de desarrollo válida")


class ProductionConfig(Config):
    """
    🚀 CONFIGURACIÓN PARA PRODUCCIÓN (Render, AWS, etc.)

    ¿Cuándo se usa?
    - Cuando FLASK_ENV=production
    - En el servidor real (Render, Heroku, etc.)
    - Para usuarios reales

    ¿Qué tiene de especial?
    - DEBUG desactivado (no mostrar errores internos)
    - Validaciones estrictas de seguridad
    - Logs optimizados
    - Configuraciones seguras
    """

    DEBUG = False
    TESTING = False

    # En producción, estas variables DEBEN estar en .env del servidor
    MONGO_URI = os.getenv("MONGO_URI")  # Sin valor por defecto
    SECRET_KEY = os.getenv("SECRET_KEY")  # Sin valor por defecto

    # Logging optimizado para producción
    LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING")

    # CORS más restrictivo (solo dominios específicos)
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "https://mi-frontend.com").split(",")

    @staticmethod
    def validate():
        """Validación ESTRICTA para producción"""
        logger.info("🚀 Validando configuración de PRODUCCIÓN...")

        # Ejecutar validaciones base
        Config.validate()

        # En producción, estas variables son OBLIGATORIAS
        if not ProductionConfig.MONGO_URI:
            raise ValueError("❌ MONGO_URI es obligatorio en producción")

        if not ProductionConfig.SECRET_KEY:
            raise ValueError("❌ SECRET_KEY es obligatorio en producción")

        # SECRET_KEY debe ser suficientemente segura
        if len(ProductionConfig.SECRET_KEY) < 32:
            raise ValueError(
                "❌ SECRET_KEY debe tener al menos 32 caracteres en producción"
            )

        # Verificar que no use credenciales por defecto
        if "admin:admin123" in ProductionConfig.MONGO_URI:
            raise ValueError("❌ No usar credenciales por defecto en producción")

        logger.info("✅ Configuración de producción válida")


class TestingConfig(Config):
    """
    🧪 CONFIGURACIÓN PARA TESTING (pruebas automáticas)

    ¿Cuándo se usa?
    - Para correr pytest
    - Para pruebas automáticas en CI/CD
    - Para testing de funcionalidades

    ¿Qué tiene de especial?
    - Base de datos separada para pruebas
    - Configuraciones optimizadas para velocidad
    - No afecta datos reales
    """

    DEBUG = True
    TESTING = True

    # Base de datos separada para pruebas (no afecta datos reales)
    MONGO_URI = os.getenv(
        "MONGO_TEST_URI", "mongodb://admin:admin123@mongodb:27017/agenda_test"
    )

    # SECRET_KEY simple para testing
    SECRET_KEY = "testing-key-no-importa-seguridad"

    # Configuraciones optimizadas para velocidad de testing
    DEFAULT_PAGE_SIZE = 5
    MAX_PAGE_SIZE = 10
    DB_TIMEOUT = 5

    @staticmethod
    def validate():
        """Validación para testing"""
        logger.info("🧪 Validando configuración de TESTING...")

        # Validaciones mínimas para testing
        if not TestingConfig.MONGO_URI:
            raise ValueError("❌ MONGO_TEST_URI requerido para testing")

        # Verificar que use base de datos de testing
        if "test" not in TestingConfig.MONGO_URI.lower():
            logger.warning(
                "⚠️ Base de datos de testing debería incluir 'test' en el nombre"
            )

        logger.info("✅ Configuración de testing válida")


# 🎯 FUNCIÓN PARA OBTENER CONFIGURACIÓN CORRECTA
def get_config():
    """
    🎯 SELECTOR AUTOMÁTICO DE CONFIGURACIÓN

    ¿Para qué sirve?
    - Lee tu FLASK_ENV del .env
    - Retorna la configuración correcta automáticamente
    - development → DevelopmentConfig
    - production → ProductionConfig
    - testing → TestingConfig

    ¿Cómo se usa?
    config = get_config()
    app.config.from_object(config)
    """

    env = os.getenv("FLASK_ENV", "development").lower()

    if env == "production":
        logger.info("🚀 Usando configuración de PRODUCCIÓN")
        return ProductionConfig
    elif env == "testing":
        logger.info("🧪 Usando configuración de TESTING")
        return TestingConfig
    else:
        logger.info("🔧 Usando configuración de DESARROLLO")
        return DevelopmentConfig


# 📋 VARIABLES ADICIONALES RECOMENDADAS PARA TU .ENV

"""
📝 VARIABLES RECOMENDADAS PARA AGREGAR A TU .env:

# Seguridad (IMPORTANTE para producción)
SECRET_KEY=tu-clave-super-secreta-de-32-caracteres

# Logging (opcional)
LOG_LEVEL=INFO

# Servidor (opcional, ya tienes buenos defaults)
FLASK_PORT=5000
FLASK_HOST=0.0.0.0

# Agenda médica (opcional)
MAX_CITAS_POR_DIA=25
DURACION_CITA_DEFAULT=30
HORARIO_APERTURA=08:00
HORARIO_CIERRE=20:00

# Para testing (opcional)
MONGO_TEST_URI=mongodb://admin:admin123@mongodb:27017/agenda_test

# CORS (cuando tengas frontend)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
"""

# 🚀 INICIALIZACIÓN
logger.info("📁 Módulo config.py cargado correctamente")
logger.info(f"🌍 Ambiente detectado: {os.getenv('FLASK_ENV', 'development')}")
logger.info(f"🗄️ MongoDB: {os.getenv('MONGO_URI', 'No configurado')}")
