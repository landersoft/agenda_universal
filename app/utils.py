"""
🛠️ UTILIDADES COMPARTIDAS PARA AGENDA UNIVERSAL
Funciones que todos los módulos pueden usar + Sistema de Logs

📚 ¿QUÉ ES ESTE ARCHIVO?
- Funciones que se usan en varios lugares del proyecto
- Sistema de logs para detectar problemas
- Respuestas estandarizadas para la API
- Validaciones comunes

💡 ANALOGÍA: Es como una "caja de herramientas" que todos los módulos pueden usar
"""

from flask import current_app, request
from marshmallow import ValidationError
from pymongo.errors import PyMongoError, DuplicateKeyError
from bson import ObjectId
import logging
import os
from datetime import datetime
from typing import Dict, Any, Tuple, Optional


# 📝 CONFIGURACIÓN DEL SISTEMA DE LOGS


def setup_logging():
    """
    📋 CONFIGURADOR DE LOGS

    ¿Qué son los logs?
    - Son como un "diario" de lo que pasa en la aplicación
    - Registran errores, acciones importantes, y eventos
    - Nos ayudan a encontrar problemas cuando algo falla

    ¿Por qué es importante?
    - En producción no podemos hacer "print()" para ver qué pasa
    - Los logs nos ayudan a investigar errores después
    - Podemos ver patrones de uso y problemas recurrentes

    Tipos de logs que usamos:
    - INFO: Información general (usuario creó cuenta, etc.)
    - WARNING: Algo raro pero no crítico (usuario intentó login fallido)
    - ERROR: Algo falló pero la app sigue funcionando
    - CRITICAL: Error grave que puede tumbar la aplicación
    """

    # Crear carpeta de logs si no existe
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Configurar formato de los mensajes de log
    # Ejemplo: "2025-01-15 10:30:45 - ERROR - models.py:45 - Usuario no encontrado"
    log_format = "%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s"

    # Configurar logging principal
    logging.basicConfig(
        level=logging.INFO,  # Registrar desde INFO hacia arriba
        format=log_format,
        handlers=[
            # Handler 1: Mostrar en consola (para desarrollo)
            logging.StreamHandler(),
            # Handler 2: Guardar en archivo (para producción)
            logging.FileHandler("logs/agenda_universal.log", encoding="utf-8"),
            # Handler 3: Archivo solo para errores graves
            logging.FileHandler("logs/errors.log", encoding="utf-8"),
        ],
    )

    # Configurar logger específico para errores
    error_logger = logging.getLogger("errors")
    error_handler = logging.FileHandler("logs/errors.log", encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(log_format))
    error_logger.addHandler(error_handler)

    return logging.getLogger(__name__)


# Inicializar logger
logger = setup_logging()


# 🏥 FUNCIONES DE RESPUESTA API (RESPUESTAS ESTANDARIZADAS)


def success_response(
    data: Any = None, message: str = "Operación exitosa", status_code: int = 200
) -> Tuple[Dict, int]:
    """
    ✅ RESPUESTA DE ÉXITO ESTÁNDAR

    ¿Por qué necesitamos esto?
    - Todas las respuestas exitosas deben tener el mismo formato
    - El frontend siempre sabe qué esperar
    - Fácil de mantener y cambiar en el futuro

    ¿Qué incluye una respuesta exitosa?
    - success: true (para que el frontend sepa que todo salió bien)
    - message: descripción de lo que pasó
    - data: los datos solicitados (opcional)
    - count: número de elementos si es una lista

    Ejemplo de respuesta:
    {
        "success": true,
        "message": "Doctores encontrados",
        "data": [{"nombre": "Dr. López"}, {"nombre": "Dra. García"}],
        "count": 2
    }

    Parámetros:
    - data: Los datos a devolver (puede ser dict, list, string, etc.)
    - message: Mensaje descriptivo para el usuario
    - status_code: Código HTTP (200=OK, 201=Creado, etc.)

    Retorna:
    - Tupla con (diccionario_respuesta, código_http)
    """

    # Registrar en logs que se hizo una operación exitosa
    logger.info(f"Operación exitosa: {message}")

    # Crear estructura base de respuesta
    response = {
        "success": True,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),  # Cuándo pasó esto
    }

    # Solo agregar 'data' si hay algo que mostrar
    if data is not None:
        response["data"] = data

        # Si es una lista, agregar contador para facilitar al frontend
        if isinstance(data, list):
            response["count"] = len(data)
            logger.info(f"Retornando {len(data)} elementos")

    return response, status_code


def error_response(
    message: str, status_code: int = 400, details: Dict = None
) -> Tuple[Dict, int]:
    """
    ❌ RESPUESTA DE ERROR ESTÁNDAR

    ¿Por qué necesitamos esto?
    - Todos los errores deben tener el mismo formato
    - El frontend puede manejar errores de forma consistente
    - Los logs registran todos los errores para debugging

    ¿Qué incluye una respuesta de error?
    - success: false (frontend sabe que algo falló)
    - error: mensaje descriptivo del problema
    - details: información técnica adicional (opcional)
    - timestamp: cuándo ocurrió el error

    Ejemplo de respuesta:
    {
        "success": false,
        "error": "Doctor no encontrado",
        "details": {"id": "El ID proporcionado no existe"},
        "timestamp": "2025-01-15T10:30:45"
    }

    Parámetros:
    - message: Descripción del error para mostrar al usuario
    - status_code: Código HTTP de error (400=Bad Request, 404=Not Found, etc.)
    - details: Información técnica adicional (útil para errores de validación)

    Retorna:
    - Tupla con (diccionario_respuesta, código_http)
    """

    # Registrar error en logs (diferentes niveles según gravedad)
    if status_code >= 500:
        logger.error(f"Error del servidor ({status_code}): {message}")
    elif status_code >= 400:
        logger.warning(f"Error del cliente ({status_code}): {message}")

    # Si hay detalles técnicos, también registrarlos
    if details:
        logger.debug(f"Detalles del error: {details}")

    # Crear estructura de respuesta de error
    response = {
        "success": False,
        "error": message,
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Agregar detalles técnicos si los hay
    if details:
        response["details"] = details

    return response, status_code


# 🗄️ FUNCIONES DE BASE DE DATOS


def handle_mongo_error(e: PyMongoError, context: str = "") -> Tuple[Dict, int]:
    """
    🚨 MANEJADOR INTELIGENTE DE ERRORES DE MONGODB

    ¿Por qué necesitamos esto?
    - MongoDB puede dar muchos tipos de errores diferentes
    - Algunos errores son técnicos y no deben mostrarse al usuario
    - Necesitamos registrar errores técnicos pero mostrar mensajes amigables

    Tipos de errores comunes de MongoDB:
    - DuplicateKeyError: Intentar crear algo que ya existe (ej: email duplicado)
    - ConnectionError: No se puede conectar a la base de datos
    - TimeoutError: La consulta tardó demasiado
    - ValidationError: Los datos no cumplen las reglas de la base

    Parámetros:
    - e: El error que lanzó MongoDB
    - context: Contexto donde ocurrió el error (ej: "creando usuario")

    Retorna:
    - Respuesta de error apropiada para el usuario
    """

    # Registrar error técnico completo en logs (para desarrolladores)
    logger.error(f"Error MongoDB en {context}: {type(e).__name__}: {str(e)}")

    # Manejar tipos específicos de errores
    if isinstance(e, DuplicateKeyError):
        # Error: Ya existe un registro con esos datos únicos
        logger.warning(f"Intento de duplicar datos en {context}")
        return error_response(
            "Ya existe un registro con esos datos únicos", 409  # 409 = Conflicto
        )

    elif "timeout" in str(e).lower():
        # Error: La consulta tardó mucho (base lenta o consulta compleja)
        logger.error(f"Timeout en operación de base de datos: {context}")
        return error_response(
            "La operación tardó demasiado, intente nuevamente",
            504,  # 504 = Gateway Timeout
        )

    elif "connection" in str(e).lower():
        # Error: No se puede conectar a MongoDB
        logger.critical(f"Error de conexión a MongoDB en {context}")
        return error_response(
            "Error de conexión con la base de datos", 503  # 503 = Service Unavailable
        )

    else:
        # Error genérico: no revelar detalles técnicos al usuario
        logger.error(f"Error desconocido de MongoDB en {context}: {e}")
        return error_response("Error interno del servidor", 500)


def validate_object_id(obj_id: str) -> Optional[ObjectId]:
    """
    🔍 VALIDADOR DE IDs DE MONGODB

    ¿Qué son los ObjectIds?
    - MongoDB usa IDs especiales de 24 caracteres hexadecimales
    - Ejemplo: "507f1f77bcf86cd799439011"
    - Si el usuario envía un ID malformado, MongoDB da error

    ¿Por qué validar IDs?
    - Evitar errores feos cuando el usuario envía IDs inválidos
    - Dar mensajes de error más claros
    - Registrar intentos de acceso con IDs malformados (posible ataque)

    Parámetros:
    - obj_id: String que debería ser un ObjectId válido

    Retorna:
    - ObjectId válido si el string es correcto
    - None si el string no es un ObjectId válido

    Ejemplo de uso:
    doctor_id = validate_object_id("507f1f77bcf86cd799439011")
    if not doctor_id:
        return error_response("ID de doctor inválido", 400)
    """
    try:
        # Intentar convertir string a ObjectId
        valid_id = ObjectId(obj_id)
        logger.debug(f"ObjectId válido: {obj_id}")
        return valid_id
    except Exception as e:
        # Si falla, registrar intento de ID inválido
        logger.warning(f"Intento de usar ObjectId inválido: {obj_id} - Error: {e}")
        return None


def get_db_collection(collection_name: str):
    """
    📚 OBTENER COLECCIÓN DE BASE DE DATOS

    ¿Qué es una colección?
    - En MongoDB, es como una "tabla" en bases de datos tradicionales
    - Ejemplos: "profesionales", "pacientes", "citas", "especialidades"

    ¿Por qué usar esta función?
    - Acceso centralizado a las colecciones
    - Evita repetir current_app.db en todos lados
    - Facilita cambios futuros en la estructura de base
    - Registra accesos a la base para monitoring

    Parámetros:
    - collection_name: Nombre de la colección a acceder

    Retorna:
    - Objeto de colección de MongoDB listo para usar

    Ejemplo de uso:
    profesionales = get_db_collection("profesionales")
    doctor = profesionales.find_one({"_id": doctor_id})
    """
    try:
        collection = current_app.db[collection_name]
        logger.debug(f"Accediendo a colección: {collection_name}")
        return collection
    except Exception as e:
        logger.error(f"Error accediendo a colección {collection_name}: {e}")
        raise


# ✅ FUNCIONES AVANZADAS DE VALIDACIÓN


def validate_data_with_schema(
    schema_class, data: Dict[str, Any], partial: bool = False
) -> Tuple[Optional[Dict], Optional[Tuple]]:
    """
    🔍 VALIDADOR UNIVERSAL CON MANEJO AUTOMÁTICO DE ERRORES

    ¿Para qué sirve?
    - Valida datos usando cualquier esquema de Marshmallow
    - Maneja automáticamente todos los errores de validación
    - Retorna respuesta lista para enviar al usuario
    - Registra intentos de validación en logs

    ¿Qué es 'partial'?
    - partial=False: Todos los campos requeridos deben estar presentes (CREATE)
    - partial=True: Permite campos faltantes, solo valida los presentes (UPDATE)

    Parámetros:
    - schema_class: Clase del esquema a usar (EspecialidadSchema, ProfesionalSchema,)
    - data: Datos enviados por el usuario a validar
    - partial: Si permite campos faltantes (útil para actualizaciones)

    Retorna:
    - (datos_validados, None) si la validación fue exitosa
    - (None, tupla_respuesta_error) si hubo errores de validación

    Ejemplo de uso:
    validated_data, error = validate_data_with_schema(EspecialidadSchema, request.get_json())
    if error:
        return error  # Retornar error directamente al usuario
    # Si llegamos acá, los datos están validados y limpios
    """

    # Verificar que se enviaron datos
    if not data:
        logger.warning("Intento de validación sin datos")
        return None, error_response("No se enviaron datos")

    logger.info(f"Validando datos con esquema {schema_class.__name__}")
    logger.debug(f"Datos recibidos: {data}")

    try:
        # Crear instancia del esquema
        schema = schema_class(partial=partial)

        # Validar y limpiar datos
        validated_data = schema.load(data)

        logger.info(f"Validación exitosa con {schema_class.__name__}")
        logger.debug(f"Datos validados: {validated_data}")

        return validated_data, None

    except ValidationError as e:
        # Error de validación: datos incorrectos
        logger.warning(f"Error de validación con {schema_class.__name__}: {e.messages}")
        return None, error_response(
            "Los datos enviados no son válidos", 400, details=e.messages
        )
    except Exception as e:
        # Error inesperado durante validación
        logger.error(f"Error inesperado durante validación: {e}")
        return None, error_response("Error interno durante validación", 500)


def check_required_fields(
    data: Dict[str, Any], required_fields: list
) -> Optional[Tuple]:
    """
    📋 VERIFICADOR RÁPIDO DE CAMPOS OBLIGATORIOS

    ¿Para qué sirve?
    - Verificación rápida antes de validaciones complejas
    - Útil para endpoints que necesitan ciertos campos específicos
    - Ahorra procesamiento si faltan campos básicos

    Parámetros:
    - data: Datos enviados por el usuario
    - required_fields: Lista de nombres de campos que deben estar presentes

    Retorna:
    - None si todos los campos están presentes
    - Tupla de respuesta de error si falta algún campo

    Ejemplo de uso:
    error = check_required_fields(data, ['nombre', 'email', 'telefono'])
    if error:
        return error
    """

    if not data:
        return error_response("No se enviaron datos")

    missing_fields = []

    for field in required_fields:
        if field not in data or not data[field]:
            missing_fields.append(field)

    if missing_fields:
        logger.warning(f"Campos faltantes: {missing_fields}")
        return error_response(
            f"Faltan campos obligatorios: {', '.join(missing_fields)}", 400
        )

    return None


# 🔒 FUNCIONES DE SEGURIDAD Y AUDITORÍA


def log_user_action(
    action: str, user_info: str = "unknown", resource: str = "", resource_id: str = ""
):
    """
    📊 REGISTRADOR DE ACCIONES DE USUARIO

    ¿Para qué sirve?
    - Auditoría: saber quién hizo qué y cuándo
    - Seguridad: detectar patrones sospechosos
    - Debugging: entender cómo usan la aplicación

    Parámetros:
    - action: Qué acción se realizó ("CREATE", "UPDATE", "DELETE", "READ")
    - user_info: Información del usuario (IP, email, etc.)
    - resource: Tipo de recurso ("doctor", "paciente", "cita")
    - resource_id: ID específico del recurso

    Ejemplo de uso:
    log_user_action("CREATE", "192.168.1.1", "doctor", str(doctor_id))
    """

    # Obtener información de la request actual
    if request:
        ip = request.remote_addr
        user_agent = request.headers.get("User-Agent", "unknown")
        endpoint = request.endpoint
    else:
        ip = "unknown"
        user_agent = "unknown"
        endpoint = "unknown"

    # Registrar acción completa
    logger.info(
        f"USER_ACTION: {action} | Resource: {resource} | ID: {resource_id} | "
        f"User: {user_info} | IP: {ip} | Endpoint: {endpoint}"
    )


def sanitize_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    🧼 LIMPIADOR DE DATOS DE ENTRADA

    ¿Para qué sirve?
    - Seguridad: remover caracteres peligrosos
    - Consistencia: normalizar espacios, mayúsculas, etc.
    - Prevenir inyecciones y ataques

    Parámetros:
    - data: Diccionario con datos del usuario

    Retorna:
    - Diccionario con datos limpiados
    """

    if not isinstance(data, dict):
        return data

    cleaned_data = {}

    for key, value in data.items():
        if isinstance(value, str):
            # Limpiar strings: quitar espacios extra, caracteres de control
            cleaned_value = value.strip()
            # Remover caracteres de control peligrosos
            cleaned_value = "".join(char for char in cleaned_value if ord(char) >= 32)
            cleaned_data[key] = cleaned_value
        elif isinstance(value, dict):
            # Recursivamente limpiar diccionarios anidados
            cleaned_data[key] = sanitize_input(value)
        elif isinstance(value, list):
            # Limpiar listas
            cleaned_data[key] = [
                sanitize_input(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            # Otros tipos (int, bool, etc.) se mantienen igual
            cleaned_data[key] = value

    return cleaned_data


# 🔧 FUNCIONES DE UTILIDAD GENERAL


def paginate_results(
    collection, query: Dict, page: int = 1, per_page: int = 10, sort_field: str = "_id"
):
    """
    📄 PAGINADOR DE RESULTADOS

    ¿Para qué sirve?
    - Evitar cargar miles de registros de una vez
    - Mejorar rendimiento de la API
    - Mejor experiencia de usuario en el frontend

    Parámetros:
    - collection: Colección de MongoDB
    - query: Filtros para la búsqueda
    - page: Número de página (empezando en 1)
    - per_page: Cuántos registros por página
    - sort_field: Campo por el cual ordenar

    Retorna:
    - Diccionario con datos paginados y metadatos
    """

    try:
        # Calcular offset
        skip = (page - 1) * per_page

        # Obtener total de registros
        total = collection.count_documents(query)

        # Obtener registros de la página actual
        results = list(
            collection.find(query, {"_id": 0})
            .sort(sort_field, 1)
            .skip(skip)
            .limit(per_page)
        )

        # Calcular metadatos de paginación
        total_pages = (total + per_page - 1) // per_page  # Redondear hacia arriba
        has_next = page < total_pages
        has_prev = page > 1

        pagination_info = {
            "data": results,
            "pagination": {
                "current_page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev,
            },
        }

        logger.info(
            f"Paginación: página {page}/{total_pages}, {len(results)} resultados"
        )

        return pagination_info

    except Exception as e:
        logger.error(f"Error en paginación: {e}")
        raise


# 📊 FUNCIONES DE MONITOREO


def monitor_performance(func):
    """
    ⏱️ DECORADOR PARA MONITOREAR RENDIMIENTO

    ¿Para qué sirve?
    - Medir cuánto tardan las funciones
    - Detectar funciones lentas
    - Optimizar rendimiento

    Uso:
    @monitor_performance
    def mi_funcion_lenta():
        # código aquí
    """

    def wrapper(*args, **kwargs):
        start_time = datetime.utcnow()

        try:
            result = func(*args, **kwargs)
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            logger.info(
                f"PERFORMANCE: {func.__name__} ejecutada en {duration:.3f} segundos"
            )

            return result

        except Exception as e:
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            logger.error(
                f"PERFORMANCE: {func.__name__} falló después de {duration:.3f} segundos: {e}"
            )
            raise

    return wrapper


# 🚀 INICIALIZACIÓN
logger.info("Módulo utils.py inicializado correctamente")
logger.info("Sistema de logs configurado y funcionando")
