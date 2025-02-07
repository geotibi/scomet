DOMAIN = "scomet"  # The domain of the integration (matches folder name)
CONF_EMAIL = "email"        # Configuration field for email
CONF_PASSWORD = "password"  # Configuration field for password
PLATFORMS = ["sensor","button"]

# Sensor names

# Defaults
DEFAULT_NAME = "Scomet: Administrăm confortul"
DEFAULT_USER = "username"
DEFAULT_PASS = "password"
DEFAULT_UPDATE = 300  # Interval de actualizare în secunde

# POST request
HEADERS_POST = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
}

# Authentication payload
PAYLOAD_LOGIN = {
    "username": DEFAULT_USER,
    "password": DEFAULT_PASS,
}


# URLs
URL_LOGIN = "https://scomet.ro/index.php?vprog=proprietari&autentificare=true"
URL_SITUATIE = "https://scomet.ro/index.php?meniu=apartament&submeniu=situatie"
URL_FACTURI = "https://scomet.ro/index.php?meniu=apartament&submeniu=facturi"
URL_PLATA = "https://scomet.ro/index.php?meniu=apartament&submeniu=plateste"
URL_CONSUM_APA = "https://scomet.ro/index.php?meniu=apartament&submeniu=consumuri"