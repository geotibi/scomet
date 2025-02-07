import logging
import aiohttp
from bs4 import BeautifulSoup
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import URL_LOGIN, HEADERS_POST, URL_SITUATIE, URL_PLATA, URL_FACTURI, URL_CONSUM_APA

_LOGGER = logging.getLogger(__name__)

class ScometAPI:
    """
    Manager for SCOMET integration
    Authenticate and get data from the server.
    """

    def __init__(self, hass: HomeAssistant, username: str, password: str):
        self._hass = hass
        self._username = username
        self._password = password
        self._session = async_get_clientsession(self._hass)
        self._cookies = None
        self._deskis_cookie = None  # New variable to store deskis cookie
    
    @property
    def deskis_cookie(self):
        """Return the stored deskis cookie."""
        return self._deskis_cookie

    async def async_login(self) -> bool:
        """
        Login and store cookies for session management.
        Return true if login is successful.
        """
        try:
            payload = {
                "utilizator": self._username,
                "parola": self._password,
            }
            async with self._session.post(URL_LOGIN, headers=HEADERS_POST, data=payload) as resp:
                if resp.status == 200:
                    # Here we extract cookies from the response
                    self._cookies = self._session.cookie_jar.filter_cookies(URL_LOGIN)
                    self._deskis_cookie = self._cookies.get("deskis")  # Extract the deskis cookie
                    if self._deskis_cookie:
                        _LOGGER.error("Autentificare reușită, deskis cookie: %s", self._deskis_cookie)
                        return True
                    else:
                        _LOGGER.error("Eroare: Nu s-a găsit cookie-ul deskis.")
                else:
                    _LOGGER.error("Eroare HTTP la login: Status=%s", resp.status)
        except aiohttp.ClientError as err:
            _LOGGER.error("Excepție în timpul autentificării: %s", err)

        # Dacă nu a reușit
        self._cookies = None
        self._deskis_cookie = None
        return False

    async def _ensure_valid_cookie(self):
        """
        Verifică dacă cookie-ul este valid și reautentifică dacă este necesar.
        """
        if not self._deskis_cookie:
            _LOGGER.debug("Cookie deskis inexistent. Încercăm autentificarea...")
            auth_ok = await self.async_login()
            if not auth_ok:
                raise Exception("Autentificare eșuată! Nu s-a putut obține cookie-ul deskis.")
        else:
            # Optionally, you can test the validity of the cookie by making a lightweight request.
            _LOGGER.debug("Cookie deskis este setat. Presupunem că este valid.")


    async def async_request(self, url: str) -> dict | None:
        """
        GET request with cookies for session management.
        If no previous session, it will try to log in.
        """
        # Dacă nu avem cookies, încercăm să ne autentificăm
        if not self._deskis_cookie:
            auth_ok = await self.async_login()
            if not auth_ok:
                _LOGGER.error("Eroare: Nu s-a putut obține cookies de autentificare.")
                return None

        # We now use the extracted deskis cookie for the GET request
        headers = {
            "accept": "application/json",
            "user-agent": HEADERS_POST["User-Agent"],
        }
        
        cookies = {
            "deskis": self._deskis_cookie
        }

        try:
            async with self._session.get(url, headers=headers, cookies=cookies) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    _LOGGER.error("Răspuns OK de la %s: %s", url, data)
                    return data
                else:
                    _LOGGER.error("Eroare la request: Status=%s, URL=%s, Răspuns=%s",resp.status, url, await resp.text())
        except aiohttp.ClientError as err:
            _LOGGER.error("Eroare conexiune la URL=%s: %s", url, err)

        return None

    async def async_get_nrpersoane(self):
        url = URL_SITUATIE
        if not self._deskis_cookie:
            auth_ok = await self.async_login()
            if not auth_ok:
                _LOGGER.error("Eroare: Nu s-a putut obține cookie-ul deskis.")
                return None

        headers = HEADERS_POST

        cookies = {
            "deskis": self._deskis_cookie  # ✅ Use dynamically obtained cookie
        }

        try:
            async with self._session.get(url, headers=headers, cookies=cookies) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch data: HTTP {response.status}")

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                # Find the div that contains "Numar curent persoane"
                num_pers_div = None
                for div in soup.find_all("div", class_="ibox-title"):
                    if div.find("h5") and "Numar curent  persoane" in div.find("h5").text:
                        num_pers_div = div.find_parent("div", class_="ibox")
                        break

                if not num_pers_div:
                    raise Exception("Could not find the section for 'Numar curent persoane'.")

                # Extract the number inside the h1 tag within the found section
                h1_tag = num_pers_div.select_one("div.ibox-content h1.no-margins")
                if not h1_tag:
                    raise Exception("Could not find the number of people inside the correct section.")

                # Extract and convert to integer
                num_people = int(float(h1_tag.text.strip()))
                _LOGGER.debug("Nr. persoane extras corect: %s", num_people)

                return num_people

        except Exception as e:
            _LOGGER.error("Error in async_get_nrpersoane: %s", e)
            return None

    async def async_get_total(self):
        url = URL_FACTURI
        if not self._deskis_cookie:
            auth_ok = await self.async_login()
            if not auth_ok:
                _LOGGER.error("Eroare: Nu s-a putut obține cookie-ul deskis pentru datafactura.")
                return None

        headers = HEADERS_POST

        cookies = {
            "deskis": self._deskis_cookie  # ✅ Use dynamically obtained cookie
        }

        try:
            async with self._session.get(url, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch data: HTTP {response.status}")
                
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

            # Find the first <td> with data-label="Data" and extract the text (date)
            first_total_td = soup.find("td", {"data-label": "Valoare"})
            if not first_total_td:
                raise Exception("Could not find the total with data-label='Valoare'.")

            # Extract the date from the text content of the <td>
            total_value = first_total_td.text.strip().replace(",", ".")
            _LOGGER.info(f"Found total_value: {total_value}")
            total=float(total_value)
            _LOGGER.info(f"Found total: {total}")
            return total

        except Exception as e:
            _LOGGER.error(f"Error occurred while extracting total: {str(e)}")
            return None
        
    async def async_get_sold(self):
        url = URL_SITUATIE
        if not self._deskis_cookie:
            auth_ok = await self.async_login()
            if not auth_ok:
                _LOGGER.error("Eroare: Nu s-a putut obține cookie-ul deskis.")
                return None

        headers = HEADERS_POST

        cookies = {
            "deskis": self._deskis_cookie  # ✅ Use dynamically obtained cookie
        }

        try:
            async with self._session.get(url, headers=headers, cookies=cookies) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch data: HTTP {response.status}")

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                # Find the div that contains "Sold profilul curent"
                sold_div = None
                for div in soup.find_all("div", class_="ibox-title"):
                    if div.find("h5") and "Sold profilul curent" in div.find("h5").text:
                        sold_div = div.find_parent("div", class_="ibox")
                        break

                if not sold_div:
                    raise Exception("Could not find the section for 'Sold profilul curent'.")

                # Extract the number inside the h1 tag within the found section
                h1_tag = sold_div.select_one("div.ibox-content h1.no-margins")
                if not h1_tag:
                    raise Exception("Could not find sold inside the correct section.")

                # Extract and Convert ->"341,63" → "341.63" → float
                sold_value = h1_tag.text.strip().replace(",", ".")
                sold = float(sold_value)

                _LOGGER.debug("Sold extras corect: %s", sold)

                return sold

        except Exception as e:
            _LOGGER.error("Error in async_get_sold: %s", e)
            return None
        
    async def async_get_datafactura(self):
        url = URL_FACTURI
        if not self._deskis_cookie:
            auth_ok = await self.async_login()
            if not auth_ok:
                _LOGGER.error("Eroare: Nu s-a putut obține cookie-ul deskis pentru datafactura.")
                return None

        headers = HEADERS_POST

        cookies = {
            "deskis": self._deskis_cookie  # ✅ Use dynamically obtained cookie
        }

        try:
            async with self._session.get(url, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch data: HTTP {response.status}")
                
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

            # Find the first <td> with data-label="Data" and extract the text (date)
            first_date_td = soup.find("td", {"data-label": "Data"})
            if not first_date_td:
                raise Exception("Could not find a date with data-label='Data'.")

            # Extract the date from the text content of the <td>
            date = first_date_td.text.strip()
            _LOGGER.info(f"Found date: {date}")
            return date

        except Exception as e:
            _LOGGER.error(f"Error occurred while extracting data: {str(e)}")
            return None
        

    async def async_get_datascadenta(self):
        url = URL_FACTURI
        if not self._deskis_cookie:
            auth_ok = await self.async_login()
            if not auth_ok:
                _LOGGER.error("Eroare: Nu s-a putut obține cookie-ul deskis pentru datafactura.")
                return None

        headers = HEADERS_POST

        cookies = {
            "deskis": self._deskis_cookie  # ✅ Use dynamically obtained cookie
        }

        try:
            async with self._session.get(url, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch data: HTTP {response.status}")
                
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

            # Find the first <td> with data-label="Data" and extract the text (date)
            first_date_td = soup.find("td", {"data-label": "Data scadenta"})
            if not first_date_td:
                raise Exception("Could not find a date with data-label='Data scadenta'.")

            # Extract the date from the text content of the <td>
            datascadenta = first_date_td.text.strip()
            _LOGGER.info(f"Found date: {datascadenta}")
            return datascadenta

        except Exception as e:
            _LOGGER.error(f"Error occurred while extracting datascadenta: {str(e)}")
            return None
        
    async def async_get_consumaparece(self):
        url = URL_CONSUM_APA
        if not self._deskis_cookie:
            auth_ok = await self.async_login()
            if not auth_ok:
                _LOGGER.error("Eroare: Nu s-a putut obține cookie-ul deskis pentru datafactura.")
                return None

        headers = HEADERS_POST

        cookies = {
            "deskis": self._deskis_cookie  # ✅ Use dynamically obtained cookie
        }

        try:
            async with self._session.get(url, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch data: HTTP {response.status}")

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

            # Locate the correct section using <h5> tag
            apa_rece_header = soup.find("h5", string="Apa rece General")

            if not apa_rece_header:
                raise Exception("Could not find 'Apa rece General' header.")

            # Find the associated table (searching for the next <table>)
            apa_rece_table = apa_rece_header.find_next("table")

            if not apa_rece_table:
                raise Exception("Could not find 'Apa rece General' table after header.")

            # Get all rows inside the table
            rows = apa_rece_table.find_all("tr")

            if not rows or len(rows) < 2:
                raise Exception("Could not find enough rows in 'Apa rece General' table.")

            # Find the first data row (skip headers if present)
            first_data_row = None
            for row in rows:
                td_elements = row.find_all("td")
                if len(td_elements) >= 3:  # Ensure there are enough columns
                    first_data_row = row
                    break
                
            if not first_data_row:
                raise Exception("No valid data row found in the table.")

            # Find the third <td> (which contains the "Consum" value)
            consum_td = first_data_row.find_all("td")[2]  # Third column (Index 2)

            # Extract and clean the text
            consum_text = consum_td.text.strip().replace("\xa0", "").replace(",", ".")

            # Convert to float
            consum_value = float(consum_text)

            _LOGGER.info(f"Found Consum apa rece: {consum_value}")
            return consum_value

        except Exception as e:
            _LOGGER.error(f"Error occurred while extracting consumaparece: {str(e)}")
            return None
        
    async def async_get_payment_url(self):
        """Obține URL-ul paginii de plată utilizând cookie-ul deskis."""

        url = URL_PLATA # Payment page URL

        if not self._deskis_cookie:
            auth_ok = await self.async_login()
            if not auth_ok:
                _LOGGER.error("Eroare: Nu s-a putut obține cookie-ul deskis.")
                return None

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        }

        cookies = {
            "deskis": self._deskis_cookie  # ✅ Use dynamically obtained cookie
        }

        try:
            async with self._session.get(url, headers=headers, cookies=cookies) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch payment page: HTTP {response.status}")

                _LOGGER.info("Accesare pagină de plată reușită: %s", url)
                return url  # ✅ Return the payment page URL

        except Exception as e:
            _LOGGER.error("Error in async_get_payment_url: %s", e)
            return None
