import json
import math
import os
import random
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = "https://odoo.cofrial-odoo.dns.army"
DATABASE = "cofrial_odoo19"
MODE = os.getenv("SIM_MODE", "check")

KEY = Path("/run/secrets/odoo_api_key").read_text().strip()

if not KEY:
    raise SystemExit("API Key vacia")

rng = random.Random()

EVENTOS_POR_DIA = 6.0

# Posiciones iniciales conocidas de los camiones de demostracion.
# Los demas vehiculos requieren una posicion GPS previa.
GPS_DEMO = {
    "COFRIAL-CAM-001": (-38.7359, -72.5904),
    "COFRIAL-CAM-002": (-38.7400, -72.6000),
    "COFRIAL-CAM-003": (-38.7500, -72.6100),
}


def call(model, method, payload):
    peticion = Request(
        f"{BASE}/json/2/{model}/{method}",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"bearer {KEY}",
            "X-Odoo-Database": DATABASE,
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(peticion, timeout=15) as respuesta:
            return json.load(respuesta)
    except HTTPError as error:
        raise RuntimeError(
            f"Odoo respondio HTTP {error.code} en {model}/{method}"
        ) from error
    except URLError as error:
        raise RuntimeError(
            f"Error de conexion: {error.reason}"
        ) from error


def obtener_configuracion():
    registros = call(
        "cofrial.iot.simulator.config",
        "search_read",
        {
            "domain": [],
            "fields": [
                "enabled",
                "interval_number",
                "interval_type",
            ],
            "limit": 2,
        },
    )

    if len(registros) != 1:
        raise RuntimeError(
            "Debe existir exactamente una configuracion IoT"
        )

    config = registros[0]
    numero = config["interval_number"]
    unidad = config["interval_type"]

    if (
        type(numero) is not int
        or numero < 1
        or unidad not in ("minutes", "hours")
    ):
        raise RuntimeError("Intervalo de simulacion invalido")

    maximo = 1440 if unidad == "minutes" else 24

    if numero > maximo:
        raise RuntimeError(
            "Intervalo de simulacion fuera de rango"
        )

    minutos = numero * (
        60 if unidad == "hours" else 1
    )

    return bool(config["enabled"]), minutos


def obtener_vehiculos():
    vehiculos = call(
        "fleet.vehicle",
        "search_read",
        {
            "domain": [
                ["iot_monitor_enabled", "=", True]
            ],
            "fields": [
                "id",
                "display_name",
                "iot_monitor_enabled",
                "iot_temp_monitor_enabled",
                "iot_temp_min",
                "iot_temp_max",
            ],
            "limit": 501,
            "order": "id asc",
        },
    )

    if len(vehiculos) > 500:
        raise RuntimeError(
            "Mas de 500 vehiculos: ampliar la paginacion"
        )

    for vehiculo in vehiculos:
        if not vehiculo["iot_monitor_enabled"]:
            raise RuntimeError(
                "La API devolvio un vehiculo sin monitoreo"
            )

        if vehiculo["iot_temp_monitor_enabled"]:
            minimo = float(vehiculo["iot_temp_min"])
            maximo = float(vehiculo["iot_temp_max"])

            if minimo >= maximo:
                raise RuntimeError(
                    "Limites termicos invalidos para "
                    f"vehiculo {vehiculo['id']}"
                )

    return vehiculos


def ultima_lectura(vehicle_id, solo_simulador=True):
    dominio = [
        ["vehicle_id", "=", vehicle_id]
    ]

    if solo_simulador:
        dominio.append(
            ["origen", "=", "simulador"]
        )

    registros = call(
        "cofrial.iot.reading",
        "search_read",
        {
            "domain": dominio,
            "fields": [
                "fecha_lectura",
                "temp_monitored",
                "temp_camara",
                "combustible_pct",
                "lat",
                "long",
            ],
            "order": "fecha_lectura desc, id desc",
            "limit": 1,
        },
    )

    return registros[0] if registros else None


def fecha_utc(texto):
    if not texto:
        raise RuntimeError(
            "Ultima lectura sin fecha"
        )

    fecha = datetime.fromisoformat(
        str(texto).replace("Z", "+00:00")
    )

    if fecha.tzinfo is None:
        fecha = fecha.replace(
            tzinfo=timezone.utc
        )

    return fecha.astimezone(timezone.utc)


def limitar(valor, minimo, maximo):
    return max(minimo, min(maximo, valor))


def posicion_inicial(vehiculo, anterior):
    if anterior:
        lat = float(anterior["lat"])
        lon = float(anterior["long"])

        if (
            math.isfinite(lat)
            and math.isfinite(lon)
            and -90 <= lat <= 90
            and -180 <= lon <= 180
            and (lat != 0.0 or lon != 0.0)
        ):
            return lat, lon

    nombre_corto = (
        vehiculo["display_name"]
        .rsplit("/", 1)[-1]
        .strip()
    )

    return GPS_DEMO.get(nombre_corto)



# Radio de demostracion y velocidad maxima simulada.
RADIO_GPS_M = 2000.0
PASO_GPS_M_POR_MIN = 60.0


def simular_gps(vehiculo, lat, lon, paso):
    nombre = (
        vehiculo["display_name"]
        .rsplit("/", 1)[-1]
        .strip()
    )

    centro = GPS_DEMO.get(nombre)

    # Sin centro conocido, no inventar movimientos.
    if centro is None:
        return round(lat, 6), round(lon, 6)

    metros_lat = 111320.0
    metros_lon = metros_lat * max(
        0.01,
        abs(math.cos(math.radians(lat))),
    )

    norte_centro = (
        centro[0] - lat
    ) * metros_lat

    este_centro = (
        centro[1] - lon
    ) * metros_lon

    distancia_centro = math.hypot(
        norte_centro,
        este_centro,
    )

    max_paso = min(
        300.0,
        PASO_GPS_M_POR_MIN * paso,
    )

    if distancia_centro > RADIO_GPS_M:
        # Regresar gradualmente a la zona.
        mover = min(
            max_paso,
            distancia_centro,
        )

        delta_norte = (
            mover * norte_centro / distancia_centro
        )
        delta_este = (
            mover * este_centro / distancia_centro
        )

    else:
        # Movimiento controlado dentro de la zona.
        direccion = rng.uniform(
            0,
            2 * math.pi,
        )

        mover = rng.uniform(
            0.15,
            0.70,
        ) * max_paso

        delta_norte = (
            math.cos(direccion) * mover
        )
        delta_este = (
            math.sin(direccion) * mover
        )

        distancia_propuesta = math.hypot(
            norte_centro - delta_norte,
            este_centro - delta_este,
        )

        if distancia_propuesta > RADIO_GPS_M:
            if distancia_centro > 0:
                delta_norte = (
                    mover * norte_centro
                    / distancia_centro
                )
                delta_este = (
                    mover * este_centro
                    / distancia_centro
                )
            else:
                delta_norte = 0.0
                delta_este = 0.0

    return (
        round(
            lat + delta_norte / metros_lat,
            6,
        ),
        round(
            lon + delta_este / metros_lon,
            6,
        ),
    )


def generar_lectura(
    vehiculo, anterior, ahora, intervalo
):
    posicion = posicion_inicial(
        vehiculo, anterior
    )

    if posicion is None:
        return None

    lat, lon = posicion

    if anterior:
        transcurridos = max(
            1.0,
            (
                ahora - fecha_utc(
                    anterior["fecha_lectura"]
                )
            ).total_seconds() / 60.0,
        )
        combustible = float(
            anterior["combustible_pct"]
        )
    else:
        transcurridos = float(intervalo)
        combustible = 90.0

    # Evitar saltos grandes tras pausas prolongadas.
    paso = min(transcurridos, 60.0)

    if combustible < 15:
        combustible_nuevo = rng.uniform(
            85, 98
        )
    else:
        combustible_nuevo = (
            combustible
            - rng.uniform(0.04, 0.14) * paso
        )

    nueva_lat, nueva_lon = simular_gps(
        vehiculo, lat, lon, paso
    )

    datos = {
        "vehicle_id": vehiculo["id"],
        "temp_monitored": bool(
            vehiculo["iot_temp_monitor_enabled"]
        ),
        "combustible_pct": round(
            limitar(
                combustible_nuevo, 0, 100
            ),
            2,
        ),
        "lat": nueva_lat,
        "long": nueva_lon,
        "origen": "simulador",
    }

    # Solo generar temperatura si el vehiculo
    # tiene el monitoreo termico habilitado.
    if vehiculo["iot_temp_monitor_enabled"]:
        minimo = float(
            vehiculo["iot_temp_min"]
        )
        maximo = float(
            vehiculo["iot_temp_max"]
        )

        objetivo = (minimo + maximo) / 2.0

        if anterior and anterior["temp_monitored"]:
            temperatura = float(
                anterior["temp_camara"]
            )
        else:
            temperatura = objetivo

        probabilidad = 1.0 - math.exp(
            -EVENTOS_POR_DIA * paso / 1440.0
        )

        # Generar ocasionalmente una nueva
        # desviacion fuera del rango configurado.
        if (
            minimo <= temperatura <= maximo
            and rng.random() < probabilidad
        ):
            exceso = max(
                0.4,
                (maximo - minimo) * 0.15,
            )

            margen = rng.uniform(
                exceso,
                exceso * 2.5,
            )

            if rng.random() < 0.5:
                nueva_temp = minimo - margen
            else:
                nueva_temp = maximo + margen

        else:
            # Recuperacion hacia el centro
            # del rango permitido.
            recuperacion = (
                1.0 - 0.5 ** (paso / 2.0)
            )

            nueva_temp = (
                temperatura
                + recuperacion
                * (objetivo - temperatura)
                + rng.uniform(-0.20, 0.20)
            )

        datos.update({
            "temp_camara": round(
                nueva_temp, 2
            ),
            "temp_min": minimo,
            "temp_max": maximo,
        })

    return datos


def main():
    if MODE not in ("check", "once"):
        raise SystemExit(
            f"Modo SIM_MODE invalido: {MODE}"
        )

    habilitado, intervalo = (
        obtener_configuracion()
    )

    print(
        f"Configuracion Odoo: "
        f"habilitado={habilitado}, "
        f"intervalo={intervalo} min",
        flush=True,
    )

    if not habilitado:
        print(
            "Simulador deshabilitado: "
            "no se crean lecturas",
            flush=True,
        )
        return

    vehiculos = obtener_vehiculos()

    print(
        f"Vehiculos monitoreados: {len(vehiculos)}",
        flush=True,
    )

    if not vehiculos:
        print(
            "Sin vehiculos habilitados: "
            "no se crean lecturas",
            flush=True,
        )
        return

    anteriores_sim = {
        vehiculo["id"]: ultima_lectura(
            vehiculo["id"]
        )
        for vehiculo in vehiculos
    }

    ahora = datetime.now(timezone.utc)

    fechas = [
        fecha_utc(registro["fecha_lectura"])
        for registro in anteriores_sim.values()
        if registro
    ]

    ultima = max(fechas) if fechas else None

    if ultima and ultima > ahora:
        raise RuntimeError(
            "La ultima lectura simulada "
            "tiene fecha futura"
        )

    if ultima:
        transcurridos = (
            int(ahora.timestamp() // 60)
            - int(ultima.timestamp() // 60)
        )

        faltan = intervalo - transcurridos
    else:
        faltan = 0

    corresponde = faltan <= 0

    print(
        f"Corresponde generar: {corresponde}; "
        f"minutos hasta siguiente turno: "
        f"{max(0, faltan)}",
        flush=True,
    )

    if MODE == "once" and not corresponde:
        print(
            "Intervalo no cumplido: "
            "sin lecturas nuevas",
            flush=True,
        )
        return

    lecturas = []

    for vehiculo in vehiculos:
        vid = vehiculo["id"]

        anterior = (
            anteriores_sim[vid]
            or ultima_lectura(
                vid,
                solo_simulador=False,
            )
        )

        datos = generar_lectura(
            vehiculo,
            anterior,
            ahora,
            intervalo,
        )

        if datos is None:
            print(
                f"AVISO: vehiculo {vid} sin GPS inicial; "
                "no se genera lectura para "
                "este vehiculo",
                flush=True,
            )
            continue

        lecturas.append(datos)

        if datos["temp_monitored"]:
            temperatura = (
                f"{datos['temp_camara']} C "
                f"(rango {datos['temp_min']} "
                f"a {datos['temp_max']})"
            )
        else:
            temperatura = "sin sensor termico"

        print(
            f"Vehiculo {vid}: {temperatura} | "
            f"Combustible "
            f"{datos['combustible_pct']}% | "
            f"GPS {datos['lat']}, "
            f"{datos['long']}",
            flush=True,
        )

    if MODE == "check":
        print(
            "Prueba sin escrituras: "
            f"{len(lecturas)} lecturas preparadas",
            flush=True,
        )
        return

    if not lecturas:
        print(
            "Sin lecturas generables: "
            "no se crean registros",
            flush=True,
        )
        return

    ids = call(
        "cofrial.iot.reading",
        "create",
        {"vals_list": lecturas},
    )

    print(
        "Lecturas creadas:",
        ids,
        flush=True,
    )


if __name__ == "__main__":
    main()
