# Especificación Técnica de Arquitectura: "Senda"
## Línea Base de Diseño para Agente de Codificación

Este documento define la arquitectura de software, requisitos, decisiones de diseño y el stack tecnológico para **Senda**, una plataforma minimalista de publicación y feedback para escritores independientes de poemas y ensayos. Servirá como la **directriz y contrato de diseño estricto** para la generación automatizada del código.

---

## 1. Visión General del Sistema
**Senda** es un repositorio personal y público que permite a un escritor (o un grupo reducido de creadores) redactar de manera organizada sus obras literarias (poemas, ensayos, reflexiones) en formato enriquecido (Markdown), publicarlas en un feed limpio, y permitir que lectores externos registrados interactúen de forma constructiva mediante un sistema de comentarios y feedback directo.

El diseño prioriza la **simplicidad estética, la legibilidad tipográfica y una arquitectura interna robusta** pero contenida, ideal para ser desarrollada y mantenida de manera ágil por un solo ingeniero de software, garantizando un despliegue sin fricciones para la demostración académica (UNMSM VII Ciclo).

---

## 2. Requisitos del Sistema

### 2.1. Requisitos Funcionales (RF)

| Código | Requisito Funcional | Descripción Detallada |
| :--- | :--- | :--- |
| **RF-01** | **Autenticación Integrada (OAuth 2.0)** | Permitir el acceso administrativo para el escritor y autenticación para lectores mediante Google OAuth 2.0. Las sesiones de API se gestionarán mediante JSON Web Tokens (JWT) firmados. |
| **RF-02** | **Gestión de Escritos (CRUD)** | El escritor autenticado podrá crear, leer, actualizar y eliminar escritos (poemas/ensayos). Se almacenará título, cuerpo en texto plano con soporte de sintaxis Markdown, fecha de creación/publicación, y estado (Borrador / Publicado). |
| **RF-03** | **Visualización Pública (Feed)** | Acceso público para cualquier visitante (no autenticado) para explorar el feed cronológico de escritos publicados y leer el contenido completo con Markdown renderizado a HTML. |
| **RF-04** | **Sistema de Comentarios y Feedback** | Los lectores autenticados podrán dejar comentarios y valoraciones en cada escrito publicado. El escritor principal podrá moderar (eliminar) comentarios inapropiados de sus propios escritos. |
| **RF-05** | **Búsqueda y Filtrado Simple** | Permitir a los visitantes buscar escritos por etiquetas (tags) o mediante coincidencia de texto básico en títulos y contenido. |

### 2.2. Requisitos No Funcionales (RNF)

| Código | Requisito No Funcional | Meta de Diseño |
| :--- | :--- | :--- |
| **RNF-01** | **Baja Latencia de Lectura** | El tiempo de respuesta del servidor (TTFB) para la carga del feed y de lecturas individuales no debe superar los 200ms en condiciones normales. |
| **RNF-02** | **Seguridad en Escritura** | Las rutas que realicen mutaciones de datos (POST, PUT, DELETE) para escritos deben exigir obligatoriamente validación de JWT con rol verificado de Administrador (Escritor). |
| **RNF-03** | **Persistencia Ligera y Portable** | El motor de base de datos debe requerir cero configuración compleja para la demo local. Los datos de la base de datos deben poder empaquetarse fácilmente en un archivo autocontenido. |
| **RNF-04** | **Diseño Responsivo e Inclusivo** | La interfaz de usuario debe ser móvil-primero, accesible y ultra-minimalista, con un fuerte enfoque en la tipografía (serif) para la lectura prolongada sin fatiga visual. |
| **RNF-05** | **Empaquetado Estándar** | El sistema completo debe poder levantarse con un único comando de orquestación (`docker-compose up --build`) para facilitar la evaluación rápida del jurado. |

---

## 3. Limitaciones y Restricciones de Diseño

1. **Desarrollador Único (Solo Dev):** La arquitectura debe evitar la dispersión de repositorios o la complejidad de microservicios. Se prohíbe la fragmentación de la red y el uso de múltiples backends de procesamiento distribuidos.
2. **Cero Infraestructura de Bases de Datos Pesadas:** SQLite será el motor de almacenamiento relacional predeterminado por su portabilidad, encapsulando el archivo dentro de un volumen Docker.
3. **Frontend Sin Bundlers Complejos:** No se utilizarán frameworks SPA pesados (como Next.js, Angular) que requieran compilaciones complejas o configuración de Webpack/Vite que desvíen la atención de la arquitectura del backend. Se opta por HTML semántico, Tailwind CSS vía CDN o configuración simple, y JavaScript Vanilla (o Vue.js ligero sin compilación) para la interactividad de la UI.

---

## 4. Drivers Arquitectónicos Priorizados

1. **Modificabilidad (Mantenibilidad):** El código debe estructurarse de tal manera que las reglas de negocio estén completamente desacopladas de la persistencia y de la capa de API. Si en el futuro se decide migrar de SQLite a PostgreSQL, o añadir un proveedor de OAuth diferente a Google, la lógica central del dominio debe permanecer intacta.
2. **Seguridad:** Los tokens de sesión (JWT) deben tener un tiempo de expiración corto (máximo 60 minutos) y estar firmados criptográficamente con una clave secreta del entorno (`ENV`). Se debe prevenir activamente el spoofing de identidad y vulnerabilidades OWASP básicas (XSS mediante saneamiento de Markdown).
3. **Simplicidad de Despliegue:** Despliegue local rápido y confiable para entornos de evaluación académica (UNMSM).

---

## 5. Estilo Arquitectónico y Patrones

### Estilo: Monolito Modular
El sistema se organiza en un único despliegue físico (monolito) pero estructurado lógicamente en módulos desacoplados basados en capacidades del negocio (`auth`, `content`, `feedback`). Esto elimina la complejidad de red de los microservicios, pero mantiene la cohesión y el orden del código para una potencial migración futura.

### Patrón de Arquitectura: Arquitectura Limpia (Clean Architecture / Hexagonal)
Para asegurar el driver de **Modificabilidad**, el backend estructurará sus capas siguiendo la regla de dependencia: **las dependencias solo apuntan hacia adentro**.

```
  +-------------------------------------------------------------+
  |                   CAPAS DE LA ARQUITECTURA                  |
  +-------------------------------------------------------------+
  |                                                             |
  |     [ INFRAESTRUCTURA / ADAPTADORES EXTERNOS ]             |
  |     (Rutas FastAPI, SQLAlchemy, Google OAuth, SQLite)       |
  |                             |                               |
  |                             v                               |
  |                 [ APLICACIÓN / CASOS DE USO ]               |
  |                 (PublicarEscrito, CrearComentario)          |
  |                             |                               |
  |                             v                               |
  |                     [ DOMINIO / ENTIDADES ]                 |
  |                     (Escrito, Comentario, Usuario)          |
  |                                                             |
  +-------------------------------------------------------------+
```

#### Estructura de Directorios del Proyecto Backend (`/app`)
El agente de codificación deberá ceñirse estrictamente a la siguiente estructura:

```text
app/
│
├── domain/                      # Reglas de negocio puras (Cero dependencias externas)
│   ├── models.py                # Clases de dominio (Python dataclasses o clases puras)
│   ├── exceptions.py            # Excepciones de negocio de dominio
│   └── repositories.py          # Interfaces/Abstracciones de los repositorios (Port de Salida)
│
├── use_cases/                   # Casos de uso específicos de la aplicación
│   ├── auth/                    # Casos de uso de login, validación de usuario
│   ├── content/                 # Casos de uso de escritos (crear, editar, listar)
│   └── feedback/                # Casos de uso de comentarios y moderación
│
├── infrastructure/              # Adaptadores de Entrada/Salida e integraciones
│   ├── api/                     # Adaptadores de Entrada (REST API)
│   │   ├── routers/             # Rutas y controladores de FastAPI
│   │   ├── schemas/             # Modelos de validación Pydantic (Input/Output DTOs)
│   │   └── dependencies.py      # Proveedores de inyección de dependencias de FastAPI
│   │
│   ├── database/                # Adaptadores de Salida (Persistencia)
│   │   ├── models.py            # Modelos declarativos de SQLAlchemy
│   │   ├── repositories.py      # Implementación concreta de las interfaces del dominio
│   │   └── session.py           # Configuración del motor y sesión de base de datos
│   │
│   ├── auth_provider/           # Cliente de autenticación e integraciones externas
│   │   └── google_client.py     # Integración con Google OAuth
│   │
│   └── config.py                # Configuración de variables de entorno y constantes de sistema
│
├── main.py                      # Punto de entrada de la aplicación FastAPI
└── requirements.txt             # Dependencias del backend
```

---

## 6. Atributos de Calidad, Escenarios y Tácticas

### 6.1. Atributo: Modificabilidad
*   **Escenario:** El desarrollador decide migrar la base de datos relacional SQLite local a una instancia PostgreSQL en la nube para producción. El cambio debe realizarse modificando únicamente archivos de la capa de infraestructura, con cero alteración a los archivos de lógica de negocio en `domain/` y `use_cases/`.
*   **Táctica:** **Inversión de Dependencias (Dependency Inversion).** Los casos de uso interactúan únicamente a través de clases abstractas de repositorio definidas en `domain/repositories.py`. FastAPI inyectará la implementación de infraestructura en tiempo de ejecución (mediante dependencias).

### 6.2. Atributo: Seguridad
*   **Escenario:** Un usuario malintencionado intercepta la red o intenta falsificar una petición para borrar un poema escrito por el administrador. El sistema detecta la falta de firma de seguridad, rechaza la transacción y registra el intento fallido sin alterar la integridad de los datos en menos de 50ms.
*   **Táctica:** **Autorización Centralizada.** Uso de Middleware e interceptores para parsear cabeceras `Authorization: Bearer <JWT>`. Firma criptográfica HMAC con SHA-256 (`HS256`).

### 6.3. Atributo: Desempeño (Performance)
*   **Escenario:** 50 lectores acceden de manera concurrente al feed público para leer las publicaciones. El backend debe responder a las peticiones GET en menos de 150ms utilizando un motor local.
*   **Táctica:** **Consultas Optimizadas y DTOs Minimalistas.** Paginación forzada en base de datos en las rutas del feed (`limit` y `offset`). Retorno de modelos de datos pydantic optimizados (sin información innecesaria de auditoría o relaciones pesadas).

---

## 7. Stack Tecnológico Detallado

*   **Backend:** Python 3.11+
    *   **FastAPI:** Framework web asíncrono para construir APIs rápidas con autogeneración de documentación interactiva (OpenAPI/Swagger).
    *   **Pydantic v2:** Validación estricta de tipos de datos, serialización rápida y configuración de esquemas.
    *   **SQLAlchemy 2.0:** Mapeador objeto-relacional (ORM) moderno utilizando estilos declarativos con tipado estático opcional.
    *   **Alembic:** Sistema de migraciones para el esquema de la base de datos (opcional para desarrollo local, pero recomendado).
    *   **PyJWT:** Para la generación, firma y desencriptación segura de JSON Web Tokens de sesión.
*   **Persistencia:**
    *   **SQLite:** Archivo local para desarrollo ágil y fácil de portar para el jurado calificador.
*   **Frontend:**
    *   **HTML5 & Tailwind CSS (v3/v4):** Estructuración de UI minimalista basada en utilidades rápidas y estilos adaptables.
    *   **Markdown-it / Marked.js:** Librería de JavaScript para parsear y renderizar el texto enriquecido de los escritos de forma dinámica en el cliente.
    *   **Vanilla JS:** Manejo de peticiones asíncronas con `fetch` hacia el backend, renderizado dinámico de la interfaz y manejo seguro del almacenamiento del JWT en `sessionStorage` o cookies HTTPOnly.
*   **Infraestructura y Orquestación:**
    *   **Docker & Docker Compose:** Contenerización del backend (`Dockerfile` multi-stage ligero) para aislamiento completo de la aplicación.

---

## 8. Directrices de Programación para el Agente de Codificación

Cuando comiences a generar el código para este proyecto, debes adherirte rigurosamente a las siguientes normas:

1. **Mantén la Pureza del Dominio:** El directorio `app/domain/` no puede importar nada de `fastapi`, `sqlalchemy`, `pydantic` o dependencias de terceros para bases de datos o red. Solo utiliza librerías nativas de Python.
2. **Definición de Puertos de Entrada/Salida:** Cada repositorio del dominio debe ser una clase abstracta (`abc.ABC`):
   ```python
   from abc import ABC, abstractmethod
   from app.domain.models import Escrito

   class IEscritoRepository(ABC):
       @abstractmethod
       def get_by_id(self, id: int) -> Escrito | None:
           pass
       # ... otros métodos
   ```
3. **Inyección de Dependencias Limpia:** Utiliza el sistema `Depends` de FastAPI en la capa de endpoints para resolver e inyectar los Casos de Uso y sus correspondientes repositorios concretos hacia los controladores.
4. **Validación de Errores Explicita:** No devuelvas códigos de estado HTTP genéricos en caso de fallos lógicos. Atrapa excepciones de dominio (ej. `EscritoNoEncontradoException`) en la capa de routers (o mediante un exception handler global en FastAPI) y conviértelas en códigos HTTP semánticos (ej. `HTTPException(status_code=404, detail="El escrito especificado no existe")`).
5. **Seguridad Robusta por Defecto:** Almacena los secretos (`JWT_SECRET`, `GOOGLE_CLIENT_ID`, etc.) estrictamente en variables de entorno leídas a través de un esquema de configuración Pydantic `BaseSettings`. No dejes credenciales hardcoded en el repositorio.

---
*Este documento constituye la especificación de referencia para construir el proyecto Senda conforme a los estándares de evaluación de Arquitectura de Software del VII Ciclo de Ingeniería de Sistemas - UNMSM.*
