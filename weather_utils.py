import requests
import datetime
import logging
import json
from fuzzywuzzy import process
from config import (
    CLAU_WEATHERAPI,
    TOTS_MUNICIPIS_CATALUNYA,
    MUNICIPIS_CATALUNYA_NOMES,
    TRADUCCIONS_PER_API
)

# Configuració del logger per a les utilitats meteorològiques
logger = logging.getLogger('weather_utils')

def formatar_data(data_str):
    """Converteix data YYYY-MM-DD a format català complet."""
    try:
        dt = datetime.datetime.strptime(data_str, "%Y-%m-%d")
        dies_ca = ['Dilluns', 'Dimarts', 'Dimecres', 'Dijous', 'Divendres', 'Dissabte', 'Diumenge']
        mesos_ca = ['de gener', 'de febrer', 'de març', 'd\'abril', 'de maig', 'de juny',
                    'de juliol', 'd\'agost', 'de setembre', 'd\'octubre', 'de novembre', 'de desembre']
        dia_setmana = dies_ca[dt.weekday()]
        mes = mesos_ca[dt.month - 1]
        return f"{dia_setmana}, {dt.day} {mes} de {dt.year}"
    except Exception:
        return data_str


def obtenir_emoji_condicio(text_condicio):
    """Retorna emoji corresponent a la condició meteorològica."""
    icones = {
        "Sunny": "☀️", "Clear": "🌕", "Partly cloudy": "⛅", "Cloudy": "☁️",
        "Overcast": "☁️", "Mist": "🌫️", "Patchy rain": "🌦️",
        "Rain": "🌧️", "Drizzle": "💧", "Thunder": "⛈️",
        "Snow": "❄️", "Fog": "🌫️", "Blizzard": "🌨️"
    }
    for clau, icona in icones.items():
        if clau.lower() in text_condicio.lower():
            return icona
    return "🌤️"


def trobar_localitat_correcta(localitat_entrada):
    """Corregeix i tradueix noms de localitats per a la API."""
    if not MUNICIPIS_CATALUNYA_NOMES:
        nom_corregit = localitat_entrada
    else:
        millor_coincidencia = process.extractOne(localitat_entrada, MUNICIPIS_CATALUNYA_NOMES)
        nom_corregit, score = millor_coincidencia
        if score < 75:
            nom_corregit = localitat_entrada

    localitat_per_api = TRADUCCIONS_PER_API.get(nom_corregit, nom_corregit)
    return nom_corregit, localitat_per_api


def obtenir_dades_temps_actual(localitat_api):
    """
    Consulta WeatherAPI per dades meteorològiques actuals.
    Inclou verificació de coherència entre temperatures actuals i pronòstic.
    """
    url_base = "http://api.weatherapi.com/v1/forecast.json"
    params = {
        "key": CLAU_WEATHERAPI, "q": localitat_api, "days": 1,
        "aqi": "no", "alerts": "no", "lang": "ca"
    }

    resposta = None
    dades = {}

    try:
        if not CLAU_WEATHERAPI:
            logger.error("Clau API de WeatherAPI no trobada")
            return None

        # Sistema de reintents per errors temporals
        max_retries = 3
        for attempt in range(max_retries):
            try:
                resposta = requests.get(url_base, params=params, timeout=10)
                resposta.raise_for_status()
                dades = resposta.json()
                break
            except requests.exceptions.HTTPError as http_err:
                if 500 <= resposta.status_code < 600 or resposta.status_code == 429:
                    logger.warning(f"Intent {attempt + 1}/{max_retries}: Error HTTP temporal ({resposta.status_code})")
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(2 ** attempt)
                    else:
                        raise http_err
                else:
                    raise http_err
            except requests.exceptions.RequestException as req_err:
                logger.warning(f"Intent {attempt + 1}/{max_retries}: Error de connexió")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)
                else:
                    raise req_err
        else:
            logger.error(f"Tots els {max_retries} intents de WeatherAPI han fallat")
            return None

    except requests.exceptions.RequestException as e:
        if resposta is not None:
            try:
                dades = resposta.json()
                error_msg = dades.get('error', {}).get('message', 'Localitat no trobada')
                logger.error(f"Error {resposta.status_code}: {error_msg} per '{localitat_api}'")
            except json.JSONDecodeError:
                logger.error(f"Error {resposta.status_code}: Resposta JSON invàlida per a '{localitat_api}'")
        else:
            logger.error(f"Error de connexió amb WeatherAPI: {e}")
        return None

    except Exception as e:
        logger.error(f"Error inesperat consultant WeatherAPI: {e}")
        return None

    if not dades or 'current' not in dades or 'forecast' not in dades:
        logger.error("Resposta de l'API incompleta o sense dades de 'current' o 'forecast'")
        return None

    try:
        dia_avui = dades['forecast']['forecastday'][0]['day']
        temp_actual = dades['current']['temp_c']
        temp_min_pronosticada = dia_avui['mintemp_c']
        temp_max_pronosticada = dia_avui['maxtemp_c']
    except (IndexError, KeyError) as e:
        logger.error(f"Estructura de dades de previsió inesperada: {e}")
        return None

    # Verificació de coherència de temperatures
    coherencia_ajustada = False

    if temp_actual < temp_min_pronosticada:
        logger.warning(f"Incoherència: Actual ({temp_actual}°C) < Mínima ({temp_min_pronosticada}°C)")
        temp_min_pronosticada = temp_actual
        coherencia_ajustada = True

    if temp_actual > temp_max_pronosticada:
        logger.warning(f"Incoherència: Actual ({temp_actual}°C) > Màxima ({temp_max_pronosticada}°C)")
        temp_max_pronosticada = temp_actual
        coherencia_ajustada = True

    resultat = {
        "localitat": dades['location']['name'],
        "data": formatar_data(dades['current']['last_updated'][:10]),
        "temperatura_actual": f"{temp_actual}°C",
        "condicio": dades['current']['condition']['text'],
        "humitat": f"{dades['current']['humidity']}%",
        "vent": f"{dades['current']['wind_kph']} km/h {dades['current']['wind_dir']}",
        "maxima": f"{temp_max_pronosticada}°C",
        "minima": f"{temp_min_pronosticada}°C",
        "hores_pluja_completes": dades['forecast']['forecastday'][0]['hour'],
        "coherencia_ajustada": coherencia_ajustada
    }

    # Detecció de períodes amb pluja segura (100%)
    resultat['pluja_risc'] = []
    for hora in resultat['hores_pluja_completes']:
        if hora.get('chance_of_rain', 0) >= 100:
            resultat['pluja_risc'].append({
                "hora": hora['time'][-5:],
                "prob": f"{hora['chance_of_rain']}%"
            })

    return resultat


def construir_missatge_temps(dades):
    """Construeix el missatge visual per Discord per a la comanda !temps."""
    icona = obtenir_emoji_condicio(dades['condicio'])

    missatge = f"**{icona} TEMPS ACTUAL A {dades['localitat'].upper()}**\n"
    missatge += "──────────────────────────────\n"
    missatge += f"📅 **{dades['data']}**\n"
    missatge += f"🌡️ **Actual:** {dades['temperatura_actual']}\n"
    missatge += f"🔺 **Màx Avui:** {dades['maxima']} | 🔻 **Mín Avui:** {dades['minima']}\n"

    # if dades.get('coherencia_ajustada', False):
    #     missatge += "*(S'han ajustat les temperatures per coherència)*\n"

    missatge += f"💧 **Humitat:** {dades['humitat']}\n"
    missatge += f"🌬️ **Vent:** {dades['vent']}\n"
    missatge += f"**{dades['condicio']}**\n"
    missatge += "──────────────────────────────"

    if dades['pluja_risc']:
        hores_pluja = ", ".join([h['hora'] for h in dades['pluja_risc']])
        missatge += f"\n☔ **AVÍS:** Pluja segura (100%) al voltant de les: {hores_pluja}"

    return missatge


def construir_missatge_alerta_pluja(dades):
    """Genera missatge d'alerta per a pluja segura a partir de les 9:00."""
    icona = obtenir_emoji_condicio(dades['condicio'])

    missatge = f"🚨 **ALERTA DE PLUJA A {dades['localitat'].upper()} AVUI** 🚨\n"
    missatge += "════════════════════════════════════════\n"
    missatge += f"📅 **{dades['data']}**\n\n"
    missatge += f"{icona} **Condició General:** {dades['condicio']}\n"
    missatge += f"🌡️ **Temperatura:** {dades['temperatura_actual']} (Màx: {dades['maxima']} | Mín: {dades['minima']})\n"

    # Processament d'hores amb pluja segura a partir de les 9:00
    hores_interval = {}
    for hora_dades in dades['hores_pluja_completes']:
        try:
            hora_int = int(hora_dades['time'][-5:-3])
            prob_pluja = hora_dades.get('chance_of_rain', 0)
            if hora_int >= 9 and prob_pluja >= 100:
                hores_interval[hora_int] = prob_pluja
        except ValueError:
            continue

    if hores_interval:
        missatge += "\n⚠️ **Pluja Segura (100%) a partir de les 9:00:**\n"
        hores_a_processar = sorted(hores_interval.keys())
        resums = []
        i = 0
        while i < len(hores_a_processar):
            inici = hores_a_processar[i]
            prob_inici = hores_interval[inici]
            final = inici
            j = i + 1
            # Agrupa hores consecutives
            while j < len(hores_a_processar) and hores_a_processar[j] == final + 1 and hores_interval[hores_a_processar[j]] == prob_inici:
                final = hores_a_processar[j]
                j += 1

            hora_inici_str = f"{inici:02d}:00"
            if final > inici:
                hora_final_str = f"{final:02d}:00"
                resums.append(f"   🕒 **{hora_inici_str} - {hora_final_str}** → {prob_inici}%")
            else:
                resums.append(f"   🕒 **{hora_inici_str}** → {prob_inici}%")
            i = j
        missatge += "\n".join(resums)

    missatge += f"\n🔍 **Més detalls (Meteocat):** <https://m.meteo.cat/>"
    missatge += "\n════════════════════════════════════════"

    return missatge


def comprovar_risc_pluja_alerta(dades):
    """Determina si hi ha risc de pluja per a l'alerta matinal."""
    return any(int(h['prob'].strip('%')) >= 100 and int(h['hora'][:2]) >= 9 for h in dades['pluja_risc'])