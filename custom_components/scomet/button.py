from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import logging
import webbrowser
from .const import DOMAIN, URL_PLATA, HEADERS_POST
import json
import asyncio

# Convert headers to a JavaScript object
headers_js = json.dumps(HEADERS_POST)

_LOGGER = logging.getLogger(__name__)

class ScometRedirectButton(CoordinatorEntity, ButtonEntity):
    """Buton pentru redirecționare către pagina de plată Scomet."""

    def __init__(self, coordinator, entry_id, api):
        """Inițializează butonul de redirecționare."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._api = api  # Instance of ScometAPI
        self._attr_unique_id = f"{entry_id}_redirect_button"
        self._attr_name = "Plătește acum"
        self._entity_id = f"button.{DOMAIN}_redirect_button_{entry_id}"
        self._icon = "mdi:credit-card"
        self._state = None

    @property
    def unique_id(self):
        """Returnează ID-ul unic al butonului."""
        return self._attr_unique_id

    @property
    def entity_id(self):
        """Returnează ID-ul entității."""
        return self._entity_id

    @entity_id.setter
    def entity_id(self, value):
        """Setează ID-ul entității."""
        self._entity_id = value

    @property
    def icon(self):
        """Returnează iconița asociată butonului."""
        return self._icon

    @property
    def device_info(self):
        """Informații despre dispozitiv pentru integrare."""
        return {
            "identifiers": {(DOMAIN, "scomet")},
            "name": "Scomet: Administrăm confortul",
            "manufacturer": "George Neagu (geotibi)",
            "model": "Scomet: Administrăm confortul",
            "entry_type": "service",
        }

##    async def async_press(self):
##        """Execută acțiunea la apăsarea butonului."""
##        try:
##            # Retrieve the payment URL from the API
##            payment_url = await self._api.async_get_payment_url()
##            
##            if not payment_url:
##                _LOGGER.error("Nu s-a putut obține URL-ul de plată.")
##                return
##
##            _LOGGER.info("Redirecționare către URL: %s", payment_url)
##
##            # Open the payment URL in a new tab (this will only work on the frontend)
##            webbrowser.open(payment_url)
##
##        except Exception as e:
##            _LOGGER.error("Eroare la redirecționare: %s", e)

    async def async_press(self):
        """Execută acțiunea la apăsarea butonului."""
        try:
            # Retrieve the payment URL from the API
            payment_url = await self._api.async_get_payment_url()
            
            if not payment_url:
                _LOGGER.error("Nu s-a putut obține URL-ul de plată.")
                return

            _LOGGER.info("Redirecționare către URL: %s", payment_url)

            # Retrieve the deskis cookie from the API
            deskis_cookie = self._api.deskis_cookie

            if not deskis_cookie:
                _LOGGER.error("Eroare: _deskis_cookie is missing!")
                return
            # Extract only the actual cookie value
            deskis_cookie = deskis_cookie.value  # Correct way to get the value
            _LOGGER.info(f"Using cleaned deskis cookie: {deskis_cookie}")

            # If browser_mod is available, open the URL in a new window
            await asyncio.sleep(1)
            services = self.hass.services.async_services()
            _LOGGER.info(f"Available services: {services}")
            if "browser_mod" in self.hass.services.async_services():
                _LOGGER.info("browser_mod is available")

                # Prepare JavaScript code with headers and cookies
                javascript_code = f"""
                    // Set the deskis cookie
                    document.cookie = "Set-Cookie: deskis={deskis_cookie}; path=/";

                    // Create an XMLHttpRequest to send headers
                    var xhr = new XMLHttpRequest();
                    xhr.open('GET', 'https://scomet.ro/index.php?meniu=apartament&submeniu=plateste', true);

                    // Set headers to match the curl example
                    xhr.setRequestHeader("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7");
                    xhr.setRequestHeader("Accept-Language", "en-GB,en;q=0.9,ro-RO;q=0.8,ro;q=0.7,en-US;q=0.6");
                    xhr.setRequestHeader("Cache-Control", "max-age=0");
                    xhr.setRequestHeader("Connection", "keep-alive");
                    xhr.setRequestHeader("Referer", "https://scomet.ro/index.php?meniu=apartament&submeniu=situatie");
                    xhr.setRequestHeader("Sec-Fetch-Dest", "document");
                    xhr.setRequestHeader("Sec-Fetch-Mode", "navigate");
                    xhr.setRequestHeader("Sec-Fetch-Site", "same-origin");
                    xhr.setRequestHeader("Sec-Fetch-User", "?1");
                    xhr.setRequestHeader("Upgrade-Insecure-Requests", "1");
                    xhr.setRequestHeader("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36");
                    xhr.setRequestHeader("sec-ch-ua", "Not A(Brand);v=8, Chromium;v=132, Google Chrome;v=132");
                    xhr.setRequestHeader("sec-ch-ua-mobile", "?0");
                    xhr.setRequestHeader("sec-ch-ua-platform", "Windows");

                    // Send the request
                    xhr.send();

                    // Open the payment page in a new window after request
                    window.open('https://scomet.ro/index.php?meniu=apartament&submeniu=plateste', '_blank');
                """
                _LOGGER.error(f"javascript_code is: {javascript_code}")
                # Execute JavaScript via browser_mod
                await self.hass.services.async_call(
                    "browser_mod",
                    "javascript",
                    {"code": javascript_code}
                )
            else:
                _LOGGER.error("browser_mod is not available, using fallback method")
        except Exception as e:
            _LOGGER.error("Eroare la redirecționare: %s", e)

async def async_setup_entry(hass, entry, async_add_entities):
    """Configurează butonul Scomet."""
    api = hass.data[DOMAIN][entry.entry_id]["api"]
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    async_add_entities([ScometRedirectButton(coordinator, entry.entry_id, api)])
