# Proyecto de Infraestructuras para el Procesamiento Masivo de Datos

## Descripción
El objetivo de este trabajo es desplegar una solución que:

1. Ofrezca una API REST para crear/modificar/eliminar registros en una base de datos.
    * El servidor del API estará implementado con Flask
    * Almacenará los datos en una BD MySQL
    * Incorporará un servicio con webUI Adminer para administrar la BD
2. Permita la monitorización completa del sistema usando Prometheus + Grafana
    * El servidor de API y el de BD ofrecerán métricas, que Prometheus leerá y almacenará
        1. Las aplicaciones Flask pueden exportar métricas directamente
        2. MySQL necesita un servicio "exporter" de traducción se sus métricas propias a un sistema
            compatible con Prometheus
    * Grafana accederá a las métricas almacenadas en Prometheus para visualizarlas


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
