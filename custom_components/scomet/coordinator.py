"""
Coordinator pentru integrarea Scomet: Administrăm confortul.
"""

import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta

from .utils_http import ScometAPI
from .const import DEFAULT_UPDATE

_LOGGER = logging.getLogger(__name__)

class ScometCoordinator(DataUpdateCoordinator):
    """
    Coordinator care adună toate datele necesare într-un singur loc.
    `self.data` va fi un dicționar cu chei relevante pentru fiecare tip de informație:
      {
        "nrpersoane": ...,
        "total": ...,
        "sold": ...,
        "datafactura": ...,
        "datascadenta": ...,
        "consumapa": ...,
        "payment_url": ...
      }
    """

    def __init__(self, hass: HomeAssistant, config_entry):
        self.hass = hass
        self.config_entry = config_entry

        self.api = ScometAPI(
            hass,
            username=config_entry.data["username"],
            password=config_entry.data["password"],
#            cod_incasare=config_entry.data["cod_incasare"],
#            cod_nlc=config_entry.data["cod_nlc"],
        )

        update_interval_seconds = config_entry.data.get("update_interval", DEFAULT_UPDATE)
        update_interval = timedelta(seconds=update_interval_seconds)

        super().__init__(
            hass,
            _LOGGER,
            name="ScometCoordinator",
            update_interval=update_interval,
        )

    async def _async_update_data(self):
        """
        Metodă apelată periodic de Coordinator (sau la cerere).
        Întoarce un dict cu toate datele, astfel încât senzorii să le poată folosi.
        """
        try:

            _LOGGER.debug("Încep actualizarea datelor din API...")

            # Ensure the cookie is valid before making any API requests
            await self.api._ensure_valid_cookie()

            nrpersoane_data = await self.api.async_get_nrpersoane()
            _LOGGER.debug("Nr. persoane extras: %s", nrpersoane_data)
            total_data = await self.api.async_get_total()
            sold_data = await self.api.async_get_sold()
            datafactura_data = await self.api.async_get_datafactura()
            datascadenta_data = await self.api.async_get_datascadenta()
            consumaparece_data = await self.api.async_get_consumaparece()
            payment_url = await self.api.async_get_payment_url()

            # Putem separa "factura_restanta" de "facturi" dacă dorim
            # facturile restante pot fi filtrate din facturi_data
            # DAR pentru a păstra EXACT structura existentă din senzori,
            # punem tot obiectul complet la "facturi", și încă unul la "factura_restanta".
            data = {
                "nrpersoane": nrpersoane_data,
                "total": total_data,
                "sold": sold_data,
                "datafactura": datafactura_data,
                "datascadenta": datascadenta_data,
                "consumaparece": consumaparece_data,
                "payment_url": payment_url,
            }
            _LOGGER.debug("Datele actualizate: %s", data)

            return data
        except Exception as err:
            # Orice excepție apare, o marcăm drept UpdateFailed
            _LOGGER.error("Eroare în _async_update_data: %s", err)
            raise UpdateFailed(f"Eroare la actualizarea datelor: {err}")
