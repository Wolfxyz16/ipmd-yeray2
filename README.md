# Proyecto de Infraestructuras para el Procesamiento Masivo de Datos

## Objetivos de aprendizaje
1. Creación de servicios disponibles vía API REST
2. Soluciones basadas en contenedores
3. Orquestación de contenedores con Docker Compose
4. Monitorización del rendimiento de servicios
5. Opcional: servicios escalables
6. Opcional: orquestación de contenedores con Kubernetes
7. Opcional: despliegue de contenedores en proveedores cloud

## Descripción
El objetivo de este trabajo es desplegar una solución que:

1. Ofrezca una API REST para crear/modificar/eliminar registros en una base de datos.
    1. El servidor del API estará implementado con Flask
    2. Almacenará los datos en una BD MySQL
    3. Incorporará un servicio con webUI Adminer para administrar la BD

2. Permita la monitorización completa del sistema usando Prometheus + Grafana
    1. El servidor de API y el de BD ofrecerán métricas, que Prometheus leerá y almacenará
        1. Las aplicaciones Flask pueden exportar métricas directamente
        2. MySQL necesita un servicio "exporter" de traducción se sus métricas propias a un sistema
            compatible con Prometheus
    2. Grafana accederá a las métricas almacenadas en Prometheus para visualizarlas

## Implementación 
La solución para este trabajo tendra los siguientes contenedores:
* API REST: Desarrollada con Flask y conectada a mariadb.
* Base de Datos (mariadb): Almacena los registros.
* Adminer: Interfaz web para administrar la base de datos.
* Prometheus: Sistema de monitoreo y recolección de métricas.
* MySQL Exporter: Adaptador para convertir métricas de mariadb a un formato compatible con Prometheus.
* Grafana: Visualización de métricas mediante dashboards.
* Ngix: Balandeador de carga para replicación de contenedores

## Monitoreo con Prometheus y Grafana
Al haber implementado servicios escalables, las metricas se exponen a traves de nginx 

Nginx expone métricas en http://localhost:80/metrics.
MySQL Exporter expone métricas en http://localhost:9104/metrics.
Grafana utiliza Prometheus como fuente de datos para visualizar las métricas.

## Modo de uso
1. Clona el repositorio:
    ```bash
    git clone https://github.com/Wolfxyz16/ipmd-yeray2.git
    ```
2. Navega al directorio del proyecto:
    ```bash
    cd ipmd-yeray2/trabajo-practico-1
    ```
3. Ejecutar docker compose
    ```bash
    docker compose up -d
    ```
