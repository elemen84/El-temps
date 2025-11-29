import discord
from discord.ext import commands, tasks
import asyncio
import logging
from datetime import time
from config import (
    TOKEN_DISCORD,
    ID_CANAL_ALERTA,
    LOG_FILE_PATH,
    LOG_FORMAT,
    LOCALITAT_ALERTA_PREDETERMINADA
)
from weather_utils import (
    obtenir_dades_temps_actual,
    construir_missatge_temps,
    construir_missatge_alerta_pluja,
    trobar_localitat_correcta,
    comprovar_risc_pluja_alerta
)

# Configuració del sistema de logging
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[logging.FileHandler(LOG_FILE_PATH, encoding='utf-8'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Inicialització del bot Discord
intencions = discord.Intents.default()
intencions.message_content = True
bot = commands.Bot(command_prefix="!", intents=intencions)

# Conversió de l'ID de canal a enter amb valor per defecte
try:
    ID_CANAL_ALERTA_INT = int(ID_CANAL_ALERTA)
except (ValueError, TypeError):
    ID_CANAL_ALERTA_INT = 123456789012345678


@bot.command(name="temps")
async def comanda_temps(ctx, localitat: str = LOCALITAT_ALERTA_PREDETERMINADA):
    """Mostra el temps actual d'una localitat."""
    # Detecció i gestió d'intents d'usar dates
    parts_missatge = ctx.message.content.split()
    if len(parts_missatge) > 2 and ("-" in parts_missatge[2] or "/" in parts_missatge[2]):
        await ctx.send(
            "⚠️ S'ha detectat un format de data. El bot només mostra el **temps actual**. Introdueix només `!temps <localitat>`.")
        return

    # Correcció si s'ha introduït una data com a localitat
    if localitat and (localitat.count('-') == 2 or localitat.count('/') == 2):
        localitat = LOCALITAT_ALERTA_PREDETERMINADA

    localitat_original = localitat
    localitat_corregida, localitat_api = trobar_localitat_correcta(localitat_original)

    await ctx.typing()

    # Obtenció de dades meteorològiques
    dades = await asyncio.to_thread(obtenir_dades_temps_actual, localitat_api)

    if not dades:
        await ctx.send(f"❌ No s'han pogut obtenir dades en temps real per **{localitat_corregida}**.")
        return

    missatge = construir_missatge_temps(dades)
    await ctx.send(missatge)


@bot.command(name="pronostic")
async def comanda_pronostic(ctx, *args):
    """Mostra l'enllaç de la predicció mòbil del Meteocat."""
    enllaç_mobil = "https://m.meteo.cat/"

    missatge = (
        "🗺️ **Pronòstic General / Meteocat Mòbil:**\n"
        f"Per veure el pronòstic a llarg termini o altres localitats:\n"
        f"<{enllaç_mobil}>"
    )
    await ctx.send(missatge)


@bot.command(name="mapes")
async def comanda_mapes(ctx):
    """Mostra enllaços a mapes i observacions del Meteocat."""
    missatge = """
**🗺️ Enllaços Ràpids del Servei Meteorològic de Catalunya (Meteocat):**

**--- OBSERVACIONS ---**
🌡️ **Estacions Aut. (XEMA):** <https://www.meteo.cat/observacions/xema>
⚡ **Llamps (XDDE):** <https://www.meteo.cat/observacions/llamps>
🌧️ **Radar (XRAD):** <https://www.meteo.cat/observacions/radar>
💧 **Pluja o Neu:** <https://www.meteo.cat/observacions/plujaONeu>
🌊 **Temperatura del Mar:** <https://www.meteo.cat/wpweb/climatologia/evolucio-observada-del-clima/temperatura-del-mar/>
🛰️ **Satèl·lit Meteosat:** <https://www.meteo.cat/observacions/satellit>
"""
    await ctx.send(missatge)


@bot.command(name="ajuda")
async def comanda_ajuda(ctx):
    """Mostra ajuda sobre les comandes disponibles."""
    ajuda_text = f"""
**🌤️ Comandes del Bot Meteorològic:**

`!temps` - Temps actual de **{LOCALITAT_ALERTA_PREDETERMINADA}** (per defecte).
`!temps <localitat>` - Temps actual d'una localitat (ex: `!temps Bcn`).
`!pronostic` - Enllaç a la **Pàgina Principal Mòbil del Meteocat**.
`!mapes` - Enllaços ràpids a **Observacions i Mapes** del Meteocat.
`!ajuda` - Mostra aquest missatge

**NOTA:** El bot proporciona dades automàtiques per l'alerta matinal de pluja a {LOCALITAT_ALERTA_PREDETERMINADA}.
"""
    await ctx.send(ajuda_text)


@tasks.loop(time=time(hour=7, minute=0))
async def tasca_alerta_pluja_badalona():
    """Tasca programada per a l'alerta matinal de pluja a les 07:00h."""
    localitat_alerta = LOCALITAT_ALERTA_PREDETERMINADA
    _, localitat_api = trobar_localitat_correcta(localitat_alerta)

    logger.info(f"⏰ Executant comprovació de pluja diària per {localitat_alerta}...")

    dades = await asyncio.to_thread(obtenir_dades_temps_actual, localitat_api)

    if not dades:
        logger.warning(f"No s'han pogut obtenir dades per {localitat_alerta} per l'alerta.")
        return

    risc_pluja = comprovar_risc_pluja_alerta(dades)

    if risc_pluja:
        canal = bot.get_channel(ID_CANAL_ALERTA_INT)
        if canal:
            missatge = construir_missatge_alerta_pluja(dades)
            await canal.send(missatge)
            logger.info("✅ Alerta de pluja (100% a partir de 9:00) enviada amb èxit.")
        else:
            logger.error(f"❌ Error: Canal amb ID {ID_CANAL_ALERTA_INT} no trobat.")
    else:
        logger.info(f"✅ No s'ha detectat pluja segura a partir de les 9:00 per {localitat_alerta}.")


@tasca_alerta_pluja_badalona.before_loop
async def abans_tasca_alerta_pluja():
    """Espera que el bot estigui llest abans d'iniciar la tasca."""
    await bot.wait_until_ready()


@bot.event
async def on_ready():
    """Esdeveniment que s'executa quan el bot està connectat i preparat."""
    logger.info(f"✅ Bot connectat com {bot.user.name}")

    # Inicia la tasca d'alerta si l'ID del canal és vàlid
    if ID_CANAL_ALERTA_INT != 123456789012345678:
        tasca_alerta_pluja_badalona.start()
        logger.info("⏰ Tasca d'alerta de pluja programada per a les 07:00h.")
    else:
        logger.warning("⚠️ Tasca d'alerta no iniciada: ID de canal no configurat.")


if __name__ == "__main__":
    """Punt d'entrada principal de l'aplicació."""
    # Verificació de credencials abans d'iniciar
    if not TOKEN_DISCORD or not (obtenir_dades_temps_actual.__globals__.get('CLAU_WEATHERAPI')):
        logger.error("❌ Falten claus d'API (DISCORD_TOKEN_METEOCAT o WEATHERAPI_KEY).")
        exit(1)

    try:
        bot.run(TOKEN_DISCORD)
    except discord.errors.LoginFailure:
        logger.error("❌ Token de Discord invàlid. Verifica DISCORD_TOKEN_METEOCAT.")
        exit(1)
    except Exception as e:
        logger.error(f"❌ Error inesperat: {e}")
        exit(1)