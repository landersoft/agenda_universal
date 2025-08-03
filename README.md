# Agenda Universal API

API RESTful para la gestión de especialidades médicas, pensada para integrarse con otros sistemas de agenda en centros de salud. Desarrollada en Python usando Flask, MongoDB y JWT para autenticación.

---

## Tabla de contenido

- [Tecnologías](#tecnologías)
- [Instalación local](#instalación-local)
- [Instalación con Docker](#instalación-con-docker)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Rutas disponibles](#rutas-disponibles)
- [Autenticación JWT](#autenticación-jwt)
- [Testing](#testing)
- [Extender la API](#extender-la-api)

---

## Tecnologías

- Python 3.10+
- Flask
- Flask-JWT-Extended
- MongoDB
- Marshmallow
- Pytest
- Swagger (Fasgger)

---

## Instalación local

```bash
# Clona el repositorio
$ git clone https://github.com/landersoft/agenda_universal.git
$ cd agenda_universal

# Crea entorno virtual (opcional)
$ python -m venv env
$ source env/bin/activate

# Instala dependencias
$ pip install -r requirements.txt

# Correr la aplicación
$ python app.py
```

Accede a Swagger en: [http://localhost:5000/apidocs](http://localhost:5000/apidocs)

---

## Instalación con Docker

```bash
# Construir imagen
$ docker build -t agenda_universal .

# Levantar contenedor
$ docker run -p 5000:5000 agenda_universal
```

---

## Estructura del proyecto

```
agenda_universal/
|├── app.py                # Punto de entrada principal
|├── models/              # Modelos de datos
|├── routes/              # Endpoints organizados por Blueprint
|├── schemas/             # Validaciones con Marshmallow
|├── services/            # Lógica de negocio
|├── tests/               # Pruebas automatizadas
|├── docs/                # Documentación Swagger en YAML
|├── utils/               # Funciones auxiliares
|├── requirements.txt    # Dependencias
```

---

## Rutas disponibles

Autenticación:

- `POST /login`

Especialidades:

- `POST /especialidades`
- `GET /especialidades`
- `GET /especialidades/<id>`
- `PUT /especialidades/<id>`
- `DELETE /especialidades/<id>`

Swagger:

- `GET /apidocs`

---

## Autenticación JWT

Para usar los endpoints protegidos:

1. Primero, inicia sesión:

```bash
POST /login
{
  "username": "admin",
  "password": "admin"
}
```

2. Obtendrás un `access_token`. Agrégalo al header en tus requests:

```bash
Authorization: Bearer <token>
```

---

## Testing

```bash
# Ejecutar todos los tests
$ pytest
```

---

## Extender la API

1. Crea un nuevo archivo en `routes/` usando Blueprint.
2. Agrega lógica en `services/` si es necesario.
3. Define un esquema en `schemas/` para validar entrada/salida.
4. Si quieres documentar la ruta:
   - Usa docstrings tipo Swagger o
   - Crea un YAML en `docs/` y usa `@swag_from()`

---

## Recomendaciones para nuevos desarrolladores

- Usa virtualenv o Docker para aislar el entorno.
- Sigue la estructura de carpetas.
- Cubre tus nuevos endpoints con tests en `tests/`.
- Documenta siempre con Swagger.
- Usa JWT para proteger rutas sensibles.

---

Para cualquier duda, contacta con el desarrollador principal o revisa los comentarios incluidos en el código.

