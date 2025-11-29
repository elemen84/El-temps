import os

CLAU_WEATHERAPI = os.getenv("WEATHERAPI_KEY")
TOKEN_DISCORD = os.getenv("DISCORD_TOKEN_METEOCAT")
ID_CANAL_ALERTA = os.getenv("DISCORD_CHANNEL_ID")

TOTS_MUNICIPIS_CATALUNYA = [
    "Abrera", "Aguilar de Segarra", "Agramunt", "Aiguamúrcia", "Aiguaviva", "Aitona",
    "Alàs i Cerc", "Albagés, L'", "Albatàrrec", "Albesa", "Albi, L'", "Albinyana",
    "Albons", "Alcanar", "Alcarràs", "Alcoletge", "Alcover", "Aldover", "Alella",
    "Alfarràs", "Alfés", "Algerri", "Alguaire", "Alins", "Almoster", "Altafulla",
    "Almacelles", "Almenar", "Alpens", "Amposta", "Anglesola", "Anglès", "Arenys de Mar",
    "Arbeca", "Arbúcies", "Argentona", "Ascó", "Avinyó", "Badalona", "Badia del Vallès",
    "Bàscara", "Balaguer", "Banyoles", "Barberà del Vallès", "Barcelona", "Begues",
    "Bellpuig", "Bellver de Cerdanya", "Benifallet", "Berga", "Besalú", "Blanes",
    "Breda", "El Bruc", "Calafell", "Caldes de Malavella", "Caldes de Montbui",
    "Calella", "Cambrils", "Camprodon", "Canet de Mar", "Canovelles", "Cardedeu",
    "Cassà de la Selva", "Castelldefels", "Castelló d'Empúries", "Cerdanyola del Vallès",
    "Cervelló", "Cervera", "Cunit", "Deltebre", "Esparreguera", "Esplugues de Llobregat",
    "Figueres", "Flix", "Garriguella", "Gavà", "Girona", "Granollers", "Guissona",
    "Igualada", "L'Ametlla de Mar", "La Bisbal d'Empordà", "La Jonquera", "La Pera",
    "Llançà", "Llavorsí", "Lleida", "Lloret de Mar", "Manresa", "Masnou, El",
    "Mataró", "Molins de Rei", "Mollet del Vallès", "Mora d'Ebre", "Olesa de Montserrat",
    "Olot", "Palamós", "Palau-solità i Plegamans", "Pallejà", "Parets del Vallès",
    "El Perelló", "Piera", "Pineda de Mar", "Premià de Mar", "Puigcerdà", "Reus",
    "Ripoll", "Ripollet", "Roda de Barà", "Roses", "Rubí", "Sabadell", "Salou",
    "Salt", "Sant Andreu de la Barca", "Sant Boi de Llobregat", "Sant Cugat del Vallès",
    "Sant Feliu de Guíxols", "Sant Feliu de Llobregat", "Sant Joan Despí",
    "Sant Just Desvern", "Sant Pere de Ribes", "Sant Pol de Mar", "Sant Quirze del Vallès",
    "Sant Vicenç dels Horts", "Santa Coloma de Gramenet", "Santa Perpètua de Mogoda",
    "Sitges", "Solsona", "Sort", "Tarragona", "Tàrrega", "Terrassa", "Tiana",
    "Tordera", "Tortosa", "Tremp", "Vic", "Vilafranca del Penedès", "Vilanova i la Geltrú",
    "Viladecans", "Vila-seca", "Ulldecona", "Vallirana", "Valls"
]
TOTS_MUNICIPIS_CATALUNYA.sort()
MUNICIPIS_CATALUNYA_NOMES = TOTS_MUNICIPIS_CATALUNYA

TRADUCCIONS_PER_API = {
    "Figueres": "Figueras", "Lleida": "Lerida", "Tàrrega": "Tarrega", "Girona": "Gerona"
}

LOCALITAT_ALERTA_PREDETERMINADA = "Badalona"

LOG_FILE_PATH = 'bot.log'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'