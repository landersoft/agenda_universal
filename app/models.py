# aca van los modelos
"""
📚 EXPLICACIÓN DE LIBRERÍAS UTILIZADAS

1. MARSHMALLOW:
   - Es como un "filtro inteligente" para datos
   - Valida que los datos tengan el formato correcto
   - Ejemplo: Si esperamos un email, verifica que tenga @ y .com
   - Limpia datos automáticamente (quita espacios, convierte mayúsculas)

2. DATETIME:
   - Maneja fechas y horas
   - Permite comparar fechas, sumar/restar tiempo
   - Útil para horarios de citas médicas

3. RE (Regular Expressions):
   - Busca patrones en texto
   - Ejemplo: Validar que un teléfono tenga formato +56 9 1234 5678
   - Como un "buscador avanzado" de texto

4. TYPING:
   - Ayuda a especificar qué tipo de datos espera una función
   - Dict[str, Any] = Diccionario con llaves string y valores cualquiera
   - Hace el código más claro y ayuda a encontrar errores
"""

from marshmallow import Schema, fields, validate, ValidationError, pre_load, post_load
from datetime import datetime
import re
from typing import Dict, Any


class BaseSchema(Schema):
    """
    🏗️ ESQUEMA BASE

    ¿Qué hace?
    - Define campos que TODOS los modelos van a tener
    - Como una "plantilla" que otros modelos pueden usar

    ¿Por qué usar esto?
    - Evita repetir código
    - Todos los registros tendrán fecha de creación y modificación
    """

    # dump_default = valor que se usa cuando se convierte a JSON
    created_at = fields.DateTime(dump_default=datetime.utcnow)  # Fecha de creación
    updated_at = fields.DateTime(
        dump_default=datetime.utcnow
    )  # Fecha de última modificación


class EspecialidadSchema(BaseSchema):
    """
    🏥 ESQUEMA PARA ESPECIALIDADES MÉDICAS

    ¿Qué valida?
    - Que el nombre no esté vacío y no sea muy largo
    - Que tenga una descripción clara
    - Que incluya palabras clave para búsquedas

    Ejemplo de datos válidos:
    {
        "nombre": "Cardiología",
        "descripcion": "Especialidad del corazón y sistema cardiovascular",
        "taxonomia": ["corazón", "cardiólogo", "presión", "infarto"]
    }
    """

    # required=True = Campo obligatorio
    # validate=validate.Length() = Validar longitud del texto
    nombre = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=100),  # Entre 2 y 100 caracteres
        error_messages={"required": "El nombre de la especialidad es obligatorio"},
    )

    descripcion = fields.Str(
        required=True,
        validate=validate.Length(min=10, max=500),  # Descripción más larga
        error_messages={"required": "La descripción es obligatoria"},
    )

    # fields.List() = Una lista de elementos
    # fields.Str() dentro = cada elemento de la lista debe ser texto
    taxonomia = fields.List(
        fields.Str(
            validate=validate.Length(min=2, max=50)
        ),  # Cada palabra entre 2-50 caracteres
        validate=validate.Length(min=1, max=20),  # Entre 1 y 20 palabras
        error_messages={"required": "Debe incluir al menos una palabra clave"},
    )

    # dump_default=True = Por defecto será True cuando se guarde
    activa = fields.Bool(dump_default=True)

    @pre_load  # Se ejecuta ANTES de validar los datos
    def clean_data(self, data, **kwargs):
        """
        🧹 LIMPIEZA DE DATOS

        ¿Qué hace?
        - Se ejecuta antes de validar
        - Limpia y mejora los datos que llegan
        - Ejemplo: "cardiología  " → "Cardiología"

        ¿Por qué es útil?
        - Los usuarios pueden escribir mal (espacios extra, mayúsculas)
        - Mejora la consistencia de datos
        """
        if isinstance(data, dict):  # Si es un diccionario
            # Limpiar nombre: quitar espacios y poner primera letra mayúscula
            if "nombre" in data:
                data["nombre"] = data["nombre"].strip().title()

            # Limpiar taxonomía: convertir a minúsculas y quitar espacios
            if "taxonomia" in data and isinstance(data["taxonomia"], list):
                data["taxonomia"] = [
                    term.strip().lower()  # Quitar espacios y convertir a minúsculas
                    for term in data["taxonomia"]
                    if term.strip()  # Solo si no está vacío
                ]
        return data


class HorarioSchema(Schema):
    """
    ⏰ ESQUEMA PARA HORARIOS DE ATENCIÓN

    ¿Para qué sirve?
    - Define cuándo trabaja cada doctor
    - Ejemplo: Lunes de 9:00 a 17:00

    ¿Qué valida?
    - Que el día sea válido (lunes, martes, etc.)
    - Que las horas estén en formato correcto
    - Que la hora de inicio sea menor que la de fin
    """

    # validate.OneOf() = Solo permite estos valores específicos
    dia = fields.Str(
        required=True,
        validate=validate.OneOf(
            ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
        ),
        error_messages={"required": "El día es obligatorio"},
    )

    # fields.Time() = Solo acepta horas (09:00, 14:30, etc.)
    inicio = fields.Time(
        required=True, error_messages={"required": "La hora de inicio es obligatoria"}
    )

    fin = fields.Time(
        required=True, error_messages={"required": "La hora de fin es obligatoria"}
    )

    activo = fields.Bool(dump_default=True)

    @post_load  # Se ejecuta DESPUÉS de validar los datos básicos
    def validate_horario(self, data, **kwargs):
        """
        ✅ VALIDACIÓN PERSONALIZADA

        ¿Qué hace?
        - Verifica lógica de negocio
        - Ejemplo: No puedes terminar antes de empezar

        ¿Cuándo se ejecuta?
        - Después de que todos los campos individuales sean válidos
        - Antes de guardar en la base de datos
        """
        if data["inicio"] >= data["fin"]:
            raise ValidationError("La hora de inicio debe ser menor que la hora de fin")
        return data


class ProfesionalSchema(BaseSchema):
    """
    👨‍⚕️ ESQUEMA PARA DOCTORES/PROFESIONALES

    ¿Qué información guarda?
    - Datos personales del doctor
    - Su especialidad
    - Horarios de trabajo
    - Información de contacto

    Validaciones especiales:
    - RUT chileno válido
    - Teléfono con formato chileno
    - Email válido
    """

    nombre = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=100),
        error_messages={"required": "El nombre del profesional es obligatorio"},
    )

    apellido = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=100),
        error_messages={"required": "El apellido es obligatorio"},
    )

    # RUT: Identificación chilena única
    rut = fields.Str(
        required=True,
        validate=validate.Length(min=9, max=12),  # 12.345.678-9 = 12 caracteres máximo
        error_messages={"required": "El RUT es obligatorio"},
    )

    # Referencia a la especialidad que maneja
    especialidad_id = fields.Str(
        required=True, error_messages={"required": "La especialidad es obligatoria"}
    )

    # validate.Regexp() = Validar usando expresión regular (patrón)
    # Patrón para teléfonos chilenos: +56 9 1234 5678 o +56 2 1234 5678
    telefono = fields.Str(
        required=True,
        validate=validate.Regexp(
            r"^\+?56\s?[2-9]\d{8}$|^\+?56\s?9\s?\d{4}\s?\d{4}$",
            error="Formato de teléfono chileno inválido",
        ),
        error_messages={"required": "El teléfono es obligatorio"},
    )

    # fields.Email() = Validación automática de email
    email = fields.Email(
        required=True, error_messages={"required": "El email es obligatorio"}
    )

    direccion = fields.Str(validate=validate.Length(max=200))

    # fields.List() con fields.Nested() = Lista de objetos complejos
    # Cada doctor puede tener varios horarios (lunes 9-17, martes 14-20, etc.)
    horarios = fields.List(
        fields.Nested(HorarioSchema),  # Cada elemento usa el esquema de HorarioSchema
        validate=validate.Length(min=1, max=7),  # Mínimo 1, máximo 7 días
        error_messages={"required": "Debe definir al menos un horario"},
    )

    disponible = fields.Bool(dump_default=True)

    # Campos opcionales adicionales
    registro_profesional = fields.Str(validate=validate.Length(max=50))
    experiencia_anos = fields.Int(validate=validate.Range(min=0, max=50))
    foto_url = fields.Url()  # URL de foto del doctor

    @pre_load
    def clean_profesional_data(self, data, **kwargs):
        """
        🧹 LIMPIEZA DE DATOS DEL PROFESIONAL

        ¿Qué limpia?
        - Nombres: "juan carlos" → "Juan Carlos"
        - RUT: "12.345.678-9" → "123456789"
        - Teléfono: "+56 9 1234 5678" → "+5691234578"
        """
        if isinstance(data, dict):
            # Normalizar nombres (primera letra mayúscula)
            if "nombre" in data:
                data["nombre"] = data["nombre"].strip().title()
            if "apellido" in data:
                data["apellido"] = data["apellido"].strip().title()

            # Limpiar RUT: quitar puntos, guiones, espacios
            # re.sub() = reemplazar caracteres que NO sean dígitos o K
            if "rut" in data:
                data["rut"] = re.sub(r"[^\dkK]", "", data["rut"].upper())

            # Limpiar teléfono: quitar espacios, guiones, paréntesis
            if "telefono" in data:
                data["telefono"] = re.sub(r"[^\d+]", "", data["telefono"])

        return data

    @post_load
    def validate_rut(self, data, **kwargs):
        """
        ✅ VALIDACIÓN DE RUT CHILENO

        ¿Qué hace?
        - Verifica que el RUT tenga el formato correcto
        - Calcula el dígito verificador
        - Se asegura que sea un RUT real

        ¿Cómo funciona un RUT?
        - 12.345.678-9: Los primeros números son el cuerpo, el último es verificador
        - El verificador se calcula con una fórmula matemática
        """
        rut = data.get("rut", "")
        if rut and not self._validar_rut_chileno(rut):
            raise ValidationError({"rut": ["RUT chileno inválido"]})
        return data

    def _validar_rut_chileno(self, rut: str) -> bool:
        """
        🧮 ALGORITMO DE VALIDACIÓN DE RUT CHILENO

        ¿Cómo funciona?
        1. Separar cuerpo (12345678) del dígito verificador (9)
        2. Multiplicar cada dígito del cuerpo por 2,3,4,5,6,7,2,3,4...
        3. Sumar todos los resultados
        4. Calcular resto de dividir por 11
        5. El dígito verificador se calcula según reglas específicas

        Ejemplo: 12345678-9
        - 8*2 + 7*3 + 6*4 + 5*5 + 4*6 + 3*7 + 2*2 + 1*3 = 139
        - 139 % 11 = 7
        - 11 - 7 = 4 (pero como es 9, hay que verificar)
        """
        if len(rut) < 8:
            return False

        cuerpo = rut[:-1]  # Todos menos el último
        dv = rut[-1].upper()  # Último carácter en mayúscula

        if not cuerpo.isdigit():  # Verificar que el cuerpo sean solo números
            return False

        # Algoritmo de cálculo del dígito verificador
        suma = 0
        multiplo = 2

        # Recorrer el cuerpo desde atrás hacia adelante
        for digit in reversed(cuerpo):
            suma += int(digit) * multiplo
            multiplo = multiplo + 1 if multiplo < 7 else 2  # Ciclo 2,3,4,5,6,7,2,3...

        resto = suma % 11
        # Reglas del dígito verificador chileno
        dv_calculado = "K" if resto == 1 else ("0" if resto == 0 else str(11 - resto))

        return dv == dv_calculado


# 🎯 FUNCIONES DE UTILIDAD PARA USAR LOS ESQUEMAS


def validate_data(schema_class: Schema, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    ✅ VALIDADOR UNIVERSAL

    ¿Para qué sirve?
    - Función que puedes usar con cualquier esquema
    - Valida datos y devuelve datos limpios
    - Si hay errores, los reporta claramente

    ¿Cómo usar?
    especialidad_limpia = validate_data(EspecialidadSchema, datos_del_usuario)

    Parámetros:
    - schema_class: Qué tipo de datos validar (EspecialidadSchema, ProfesionalSchema)
    - data: Los datos que envió el usuario

    Retorna:
    - Datos validados y limpios, listos para guardar en base de datos
    """
    schema = schema_class()  # Crear instancia del validador
    try:
        return schema.load(data)  # Validar y limpiar datos
    except ValidationError as e:
        # Si hay errores, mostrarlos de forma clara
        raise ValidationError(f"Errores de validación: {e.messages}")


def serialize_data(schema_class: Schema, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    📤 SERIALIZADOR PARA RESPUESTAS JSON

    ¿Para qué sirve?
    - Convierte datos de la base de datos a formato JSON
    - Se asegura que las fechas se vean bien
    - Omite campos sensibles si es necesario

    ¿Cuándo usar?
    - Cuando envías datos al frontend
    - Para APIs que devuelven JSON
    """
    schema = schema_class()
    return schema.dump(data)


# 📝 EJEMPLOS DE USO COMENTADOS

"""
# EJEMPLO 1: Validar una especialidad
try:
    datos_usuario = {
        "nombre": "  cardiología  ",  # Tiene espacios extra
        "descripcion": "Especialidad del corazón",
        "taxonomia": ["CORAZÓN", "Cardiólogo", " presión "]
        } # Formato inconsistente
    # Esto limpiará y validará automáticamente:
    # - nombre: "Cardiología" (sin espacios, primera letra mayúscula)
    # - taxonomia: ["corazón", "cardiólogo", "presión"](todo en minúsculas, sin espacio)
    datos_limpios =validate_data(EspecialidadSchema,datos_usuario)
    print("✅ Datos válidos:",datos_limpios)
except ValidationError as e:
    print("❌ Errores encontrados:", e.messages)

# EJEMPLO 2: Validar un profesional
try:
    datos_doctor = {
        "nombre": "juan carlos",
        "apellido": "GONZÁLEZ",
        "rut": "12.345.678-5",             # Con puntos y guión
        "especialidad_id": "cardiologia",
        "telefono": "+56 9 1234 5678",     # Con espacios
        "email": "doctor@hospital.cl",
        "horarios": [
            {
                "dia": "lunes",
                "inicio": "09:00",
                "fin": "17:00"
            },
            {
                "dia":"martes",
                "inicio":"14:00",
                "fin":"20:00"
            }
        ]
    }
    # Validar datos del doctor
    # Esto validará:
    # - RUT chileno (algoritmo matemático)
    # - Teléfono formato chileno
    # - Email válido
    # - Horarios lógicos (inicio < fin)
    datos_doctor_limpios = validate_data(ProfesionalSchema, datos_doctor)
    print("✅ Doctor válido:", datos_doctor_limpios)
except ValidationError as e:
    print("❌ Errores en doctor:", e.messages)
"""
