# COFRIAL – Módulos Odoo 19

## 1. Descripción del proyecto

Este documento describe los módulos personalizados desarrollados para el proyecto de Transformación Digital de COFRIAL SpA.

La solución utiliza **Odoo 19 Community** e integra funcionalidades de gestión comercial, monitoreo IoT, Business Intelligence e inteligencia artificial.

El entorno original fue implementado en AWS, utilizando instancias EC2, Amazon RDS para PostgreSQL y Amazon EFS para almacenamiento compartido.

## 2. Módulos estándar de Odoo

Los siguientes módulos corresponden a las aplicaciones principales utilizadas o consideradas en el proyecto.

| Módulo técnico | Aplicación | Función |
|---|---|---|
| `crm` | CRM | Gestión de clientes potenciales y oportunidades comerciales |
| `sale_management` | Ventas | Cotizaciones, pedidos de venta y gestión comercial |
| `contacts` | Contactos | Gestión de clientes, empresas y conductores |
| `fleet` | Flota | Administración de vehículos |
| `stock` | Inventario | Gestión de productos y existencias |
| `website_sale` | Comercio electrónico | Sitio web con catálogo y ventas online |

Esta tabla presenta los módulos principales del proyecto. La lista completa de módulos instalados en AWS está pendiente de verificar.

Odoo instala automáticamente algunas dependencias cuando se instalan las aplicaciones correspondientes.

## 3. Módulos personalizados de COFRIAL

Estos módulos fueron desarrollados específicamente para el proyecto y no pertenecen al conjunto estándar de Odoo.

### 3.1. `cofrial_bi`

**Nombre:** Dashboard Business Intelligence COFRIAL

**Estado en AWS:** Instalado y probado.

**Funcionalidades:**
- Dashboard personalizado para visualizar indicadores comerciales.
- Indicadores relacionados con ventas y CRM.
- Gráficos de evolución de ventas.
- Visualización de información de monitoreo IoT.
- Interfaz desarrollada con JavaScript, XML y estilos personalizados.

**Directorio:** `cofrial_bi/`

### 3.2. `cofrial_fleet_iot`

**Nombre:** Monitoreo IoT de Flota COFRIAL

**Estado en AWS:** Instalado y probado.

**Funcionalidades:**
- Integración de vehículos con datos de telemetría.
- Registro y consulta de lecturas IoT.
- Visualización de información de monitoreo.
- Actualización periódica de vistas.
- Filtros y agrupaciones para analizar registros.

**Directorio:** `cofrial_fleet_iot/`

**Consideraciones:** Para reproducir la generación automática de telemetría se necesita configurar también el servicio externo de simulación IoT.

### 3.3. `cofrial_crm_ai`

**Nombre:** Clasificación IA de CRM COFRIAL

**Estado en AWS:** Código preparado. Instalación y pruebas funcionales pendientes de confirmación.

**Funcionalidades previstas:**
- Clasificación de consultas comerciales mediante Google Gemini.
- Integración con oportunidades de CRM.
- Categorías de clasificación:
  - Cotización.
  - Disponibilidad.
  - Reclamo.
- Botón de clasificación mediante inteligencia artificial.
- Configuración de la API Key desde los ajustes de CRM.

**Directorio:** `cofrial_crm_ai/`

**Consideraciones:**
- Requiere una API Key válida de Google Gemini.
- La configuración de la clave fue preparada para almacenarse mediante `ir.config_parameter`.
- La integración debe instalarse y probarse antes de considerarse funcional.

## 4. Estructura de los módulos

```text
cofrial_modulos_hito2/
│
├── cofrial_bi/
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── models/
│   ├── views/
│   ├── security/
│   └── static/
│
├── cofrial_fleet_iot/
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── models/
│   ├── controllers/
│   ├── views/
│   ├── security/
│   ├── demo/
│   └── static/
│
└── cofrial_crm_ai/
    ├── __init__.py
    ├── __manifest__.py
    ├── models/
    ├── views/
    ├── security/
    └── data/
```

La estructura es referencial y puede contener archivos adicionales según la versión descargada.

## 5. Requisitos de instalación

### Software

- Odoo 19 Community.
- PostgreSQL compatible con Odoo 19.
- Python y dependencias necesarias para Odoo 19.
- Módulos estándar requeridos por cada módulo personalizado.

### Servicios externos

| Servicio | Uso | Obligatorio |
|---|---|---|
| Google Gemini API | Clasificación de consultas comerciales | Para clasificación IA |
| Simulador IoT en Docker | Generación de lecturas de telemetría | Para reproducir el flujo IoT |
| Amazon RDS | Base de datos del entorno AWS original | No, puede utilizarse PostgreSQL local |
| Amazon EFS | Almacenamiento compartido del entorno AWS | No, para una instalación local individual |

## 6. Instalación local

1. Instalar y configurar Odoo 19 Community.
2. Preparar una base de datos PostgreSQL.
3. Copiar las carpetas `cofrial_bi`, `cofrial_fleet_iot` y `cofrial_crm_ai` a un directorio de módulos personalizados.
4. Agregar ese directorio al parámetro `addons_path` de Odoo.
5. Revisar el archivo `__manifest__.py` de cada módulo para conocer las dependencias exactas.
6. Instalar los módulos estándar requeridos.
7. Actualizar la lista de aplicaciones desde Odoo.
8. Instalar los módulos personalizados.
9. Configurar los servicios externos correspondientes.
10. Realizar pruebas funcionales.

Si se utiliza una base de datos existente, realizar un respaldo antes de instalar o actualizar módulos.

## 7. Diferencias entre el entorno AWS y la instalación local

La descarga de estos módulos incluye el código fuente, pero no contiene necesariamente:

- La base de datos PostgreSQL de COFRIAL.
- Los datos de clientes, ventas, vehículos y telemetría.
- Los archivos adjuntos almacenados en EFS.
- Las credenciales de servicios externos.
- La configuración de infraestructura AWS.
- El servicio Docker que genera las lecturas IoT.

Para reproducir completamente el entorno original, estos elementos deben respaldarse y configurarse por separado.
