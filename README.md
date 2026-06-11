# Módulo SIAU - Gestión PQRSDF

Módulo de microservicio para el Sistema de Información y Atención al Usuario (SIAU) de NexoSalud.

## Stack

- **Spring Boot 3.2.5 + WebFlux** (reactivo)
- **Java 17**
- **R2DBC + PostgreSQL 15**
- **Lombok, Validation, SpringDoc OpenAPI**

## API Endpoints

Todas las rutas se acceden a través del Gateway: `http://localhost:8080/api/v1/siau/...`

### PQRSDF (`/api/v1/siau/pqrsdf`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/` | Crear nueva PQRSDF |
| GET | `/` | Listar (paginado, con filtros) |
| GET | `/{id}` | Obtener por ID |
| PATCH | `/{id}` | Actualizar datos |
| POST | `/{id}/responder` | Responder PQRSDF |
| POST | `/{id}/cerrar` | Cerrar PQRSDF |
| GET | `/{id}/trazabilidad` | Historial de cambios |

### Departamentos (`/api/v1/siau/departamentos`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/` | Crear departamento |
| GET | `/` | Listar todos |
| GET | `/activos` | Listar solo activos |
| GET | `/{id}` | Obtener por ID |
| PUT | `/{id}` | Actualizar |
| PATCH | `/{id}/toggle` | Activar/desactivar |

### Asignaciones (`/api/v1/siau/asignaciones`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/asignaciones` | Asignar PQRSDF a departamento |
| GET | `/asignaciones/{id}` | Obtener asignación |
| GET | `/pqrsdf/{id}/asignaciones` | Asignaciones de una PQRSDF |
| GET | `/departamentos/{id}/asignaciones` | Asignaciones de un departamento |
| POST | `/asignaciones/{id}/responder` | Responder desde el área asignada |

### Dashboard (`/api/v1/siau/dashboard`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/dashboard` | Estadísticas generales |

### Actas de Buzón (`/api/v1/siau/actas-buzon`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/` | Crear acta de apertura |
| GET | `/` | Listar todas |
| GET | `/{id}` | Obtener por ID |

### Catálogos (`/api/v1/siau/catalogos`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/tipos-pqrsdf` | Tipos (P/Q/R/S/D/F) |
| GET | `/medios-recepcion` | Medios de recepción |
| GET | `/clasificaciones` | 12 clasificaciones Supersalud |
| GET | `/plazos-respuesta` | Plazos legales por tipo |

## Modelo de Datos

### `siau_pqrsdf` - Registro principal

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BIGSERIAL | PK |
| consecutivo | VARCHAR(30) | Código único (PQRS-P-2026-0001) |
| tipo | VARCHAR(2) | P/Q/R/S/D/F |
| fecha_radicado | DATE | Fecha de recepción |
| nombres_usuario | VARCHAR(300) | Nombre del ciudadano |
| tipo_documento / numero_documento | | Documento de identidad |
| eps / regimen | | EPS y régimen del usuario |
| medio_recepcion | VARCHAR(30) | Buzón, oficio, email, etc. |
| descripcion | TEXT | Descripción de la solicitud |
| estado | VARCHAR(20) | RECIBIDO/ASIGNADO/EN_GESTION/RESPONDIDO/CERRADO |

### `siau_departamentos` - Áreas de la ESE

| Campo | Tipo | Descripción |
|-------|------|-------------|
| nombre | VARCHAR(200) | Nombre del departamento |
| responsable | VARCHAR(200) | Persona encargada |
| activo | BOOLEAN | Si está operativo |

### `siau_asignaciones` - Asignación a áreas

| Campo | Tipo | Descripción |
|-------|------|-------------|
| pqrsdf_id | BIGINT | FK a siau_pqrsdf |
| departamento_id | BIGINT | FK a siau_departamentos |
| funcionario_id | BIGINT | FK opcional a employees |
| fecha_limite_respuesta | DATE | Fecha tope (con días hábiles) |
| estado | VARCHAR(20) | PENDIENTE/EN_GESTION/RESPONDIDA/VENCIDA |

## Integración con Gateway

Agregar en `GatewayController.java`:

```java
private String urlSiau = System.getenv().getOrDefault("SIAU_SERVICE_URL", "http://localhost:8088");
webClients.put("/api/v1/siau", WebClient.create(urlSiau));
```

Y en `docker-compose.yml`:

```yaml
siau-service:
  build:
    context: ./backend-module-siau
    dockerfile: Dockerfile
  container_name: nexosalud-siau
  environment:
    - SPRING_PROFILES_ACTIVE=prod
    - SERVER_PORT=8088
    - SPRING_R2DBC_URL=r2dbc:postgresql://postgres:5432/nexosalud
    - SPRING_R2DBC_USERNAME=postgres
    - SPRING_R2DBC_PASSWORD=postgres
  networks:
    - nexo-network
```

## Ejemplo de uso

```bash
# Crear un departamento
curl -X POST http://localhost:8080/api/v1/siau/departamentos \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Facturación", "descripcion": "Gestión de facturación"}'

# Crear una PQRSDF
curl -X POST http://localhost:8080/api/v1/siau/pqrsdf \
  -H "Content-Type: application/json" \
  -H "x-employee-id: 1" \
  -d '{
    "tipo": "Q",
    "nombresUsuario": "Juan Pérez",
    "tipoDocumento": "CC",
    "numeroDocumento": "12345678",
    "telefono": "3001234567",
    "medioRecepcion": "PRESENCIAL",
    "descripcion": "Mala atención en el servicio de urgencias"
  }'

# Asignar a departamento
curl -X POST http://localhost:8080/api/v1/siau/asignaciones \
  -H "Content-Type: application/json" \
  -d '{
    "pqrsdfId": 1,
    "departamentoId": 3,
    "observaciones": "Revisar con urgencia"
  }'
```
