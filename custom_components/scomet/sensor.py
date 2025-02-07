import logging
from datetime import datetime
from homeassistant.components.button import ButtonEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """
    Configurează entitățile de tip senzor pentru o intrare specifică din config_entries.
    """
    _LOGGER.debug("Configurarea senzorilor pentru entry_id=%s", entry.entry_id)

    # Obținem coordinatorul din hass.data
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    # Creăm entitățile senzor
    async_add_entities([
        NrPersoaneSensor(coordinator, entry.entry_id),
        TotalSensor(coordinator, entry.entry_id),
        SoldSensor(coordinator, entry.entry_id),
        DataFacturaSensor(coordinator, entry.entry_id),
        DataScadentaSensor(coordinator, entry.entry_id),
        CosnumApaSensor(coordinator, entry.entry_id),
    ])

    _LOGGER.debug("Senzorii au fost adăugați pentru entry_id=%s", entry.entry_id)

class NrPersoaneSensor(CoordinatorEntity, SensorEntity):
    """Senzor pentru afișarea informațiilor despre numărul de persoane."""

    def __init__(self, coordinator, entry_id):
        """Inițializează senzorul NrPersoane."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_unique_id = f"{entry_id}_nrpersoane"
        self._attr_name = "Număr persoane"
        self._entity_id = f"sensor.{DOMAIN}_nrpersoane"
        self._icon = "mdi:account-multiple"
        self._device_class = "Device class"
        self._state_class = "State class"
        self._state = None

    @property
    def state(self):
        """Returnează starea senzorului (numărul de persoane)."""
        _LOGGER.debug("State requested for NrPersoaneSensor: %s", self.coordinator.data)

        if self.coordinator.data is None:
            return "Unknown"

        nrpersoane = self.coordinator.data.get("nrpersoane")

        if nrpersoane is None:
            _LOGGER.error("Eroare: NrPersoaneSensor nu a găsit date în coordinator.")
            return "Unknown"

        return nrpersoane

    @property
    def unique_id(self):
        """Returnează ID-ul unic al senzorului."""
#        return self._attr_unique_id
        return f"{DOMAIN}_nrpersoane"

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
        """Returnează iconița asociată senzorului."""
        return self._icon

    @property
    def device_info(self):
        """Informații despre dispozitiv pentru integrare."""
        return {
            "identifiers": {(DOMAIN, "scomet")},
            "name": "Scomet: Administrăm confortul",
            "manufacturer": "George Neagu (geotibi)",
            "model": "Scomet: Administrăm confortul",
            "entry_type": DeviceEntryType.SERVICE,
        }

    @property
    def device_class(self):
        """Return the state class of the sensor."""
        return self._device_class

    @property
    def state_class(self):
        """Return the state class of the sensor."""
        return self._state_class

    async def async_update(self):
        """Actualizează starea senzorului cu datele din API."""
        try:
            self._state = await self.coordinator.async_get_nrpersoane()
        except Exception as e:
            _LOGGER.error("Eroare la actualizarea NrPersoaneSensor: %s", e)

class TotalSensor(CoordinatorEntity, SensorEntity):
    """Senzor pentru afișarea informațiilor despre totalul de plată."""

    def __init__(self, coordinator, entry_id):
        """Inițializează senzorul Total."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_unique_id = f"{entry_id}_total"
        self._attr_name = "Total"
        self.entity_id = "sensor.scomet_total"
        #self._entity_id = f"sensor.{DOMAIN}_total"
        #self._entity_id = f"sensor.{DOMAIN}_total"
        self._attr_entity_id = "sensor.scomet_total"  # Correctly formatted entity ID
        self._attr_icon = "mdi:sigma"
        self._attr_device_class = "monetary"
        self._attr_state_class = "measurement"
        #self._attr_unit_of_measurement = "Lei"
        self._unique_id = f"scomet_total"

    @property
    def state(self):
        """Returnează starea senzorului total."""
        _LOGGER.debug("State requested for Total: %s", self.coordinator.data)

        if self.coordinator.data is None:
            return "Unknown"

        total = self.coordinator.data.get("total")

        if total is None:
            _LOGGER.error("Eroare: TotalSensor nu a găsit date în coordinator.")
            return "Unknown"

        return total

    @property
    def unique_id(self):
        """Returnează ID-ul unic al senzorului."""
        return f"{DOMAIN}_total"

#    @property
#    def entity_id(self):
#        """Returnează ID-ul entității."""
#        return self._entity_id

#    @entity_id.setter
#    def entity_id(self, value):
#        """Setează ID-ul entității."""
#        self._entity_id = value

#    @property
#    def icon(self):
#        """Returnează iconița asociată senzorului."""
#        return self._icon

    @property
    def device_info(self):
        """Informații despre dispozitiv pentru integrare."""
        return {
            "identifiers": {(DOMAIN, "scomet")},
            "name": "Scomet: Administrăm confortul",
            "manufacturer": "George Neagu (geotibi)",
            "model": "Scomet: Administrăm confortul",
            "entry_type": DeviceEntryType.SERVICE,
        }

#    @property
#    def device_class(self):
#        """Return the device class of the sensor."""
#        return "MONETARY"

#    @property
#    def state_class(self):
#        """Return the state class of the sensor."""
#        return "measurement"

    async def async_update(self):
        """Actualizează starea senzorului cu datele din API."""
        try:
            self._state = await self.coordinator.async_get_total()
        except Exception as e:
            _LOGGER.error("Eroare la actualizarea Totalului: %s", e)

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of the sensor."""
        return "Lei"

class SoldSensor(CoordinatorEntity, SensorEntity):
    """Senzor pentru afișarea informațiilor despre soldul ramas."""

    def __init__(self, coordinator, entry_id):
        """Inițializează senzorul Sold."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        #self._attr_unique_id = f"{entry_id}_sold3"
        self._attr_name = "Sold"
        self.entity_id = f"sensor.{DOMAIN}_sold"
        #self._entity_id = f"sensor.{DOMAIN}_sold2"
        #self._attr_entity_id = "sensor.scomet_sold1"  # Correctly formatted entity ID
        self._attr_icon = "mdi:sigma"
        self._attr_device_class = "monetary"
        self._attr_state_class = "measurement"
        #self._attr_unit_of_measurement = "Lei"
        self._unique_id = f"{DOMAIN}_sold"

    @property
    def state(self):
        """Returnează starea senzorului (sold)."""
        _LOGGER.debug("State requested for Sold: %s", self.coordinator.data)

        if self.coordinator.data is None:
            return "Unknown"

        sold = self.coordinator.data.get("sold")

        if sold is None:
            _LOGGER.error("Eroare: SoldSensor nu a găsit date în coordinator.")
            return "Unknown"

        return sold

    @property
    def unique_id(self):
        """Returnează ID-ul unic al senzorului."""
        return "scomet_sold"

#    @property
#    def entity_id(self):
#        """Returnează ID-ul entității."""
#        return self._entity_id
#
#    @entity_id.setter
#    def entity_id(self, value):
#        """Setează ID-ul entității."""
#        self._entity_id = value

#    @property
#    def icon(self):
#        """Returnează iconița asociată senzorului."""
#        return self._icon

    @property
    def device_info(self):
        """Informații despre dispozitiv pentru integrare."""
        return {
            "identifiers": {(DOMAIN, "scomet")},
            "name": "Scomet: Administrăm confortul",
            "manufacturer": "George Neagu (geotibi)",
            "model": "Scomet: Administrăm confortul",
            "entry_type": DeviceEntryType.SERVICE,
        }

#    @property
#    def device_class(self):
#        """Return the device class of the sensor."""
#        return "MONETARY"

#    @property
#    def state_class(self):
#        """Return the state class of the sensor."""
#        return "measurement"
    
    async def async_update(self):
        """Actualizează starea senzorului cu datele din API."""
        try:
            self._state = await self.coordinator.async_get_sold()
        except Exception as e:
            _LOGGER.error("Eroare la actualizarea Soldului: %s", e)

    @property
    def unit_of_measurement(self):
        """Return the measurement unit of the sensor."""
        return "Lei"

class DataFacturaSensor(CoordinatorEntity, SensorEntity):
    """Senzor pentru afișarea informațiilor despre data de emitere a facturii."""

    def __init__(self, coordinator, entry_id):
        """Inițializează senzorul Data Factură."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_unique_id = f"{entry_id}_datafactura"
        self._attr_name = "Dată emitere factură"
        self._entity_id = f"sensor.{DOMAIN}_datafactura"
        self._icon = "mdi:calendar"
        self._device_class = "Device class"
        self._state = "State"
        self._state_class = "State class"

    @property
    def state(self):
        """Returnează starea senzorului dată factură."""
        _LOGGER.debug("State requested for Data factura: %s", self.coordinator.data)

        if self.coordinator.data is None:
            return "Unknown"

        datafactura = self.coordinator.data.get("datafactura")

        if datafactura is None:
            _LOGGER.error("Eroare: DataFacturaSensor nu a găsit date în coordinator.")
            return "Unknown"

        return datafactura

    @property
    def unique_id(self):
        """Returnează ID-ul unic al senzorului."""
        return f"{DOMAIN}_datafactura"

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
        """Returnează iconița asociată senzorului."""
        return self._icon

    @property
    def device_info(self):
        """Informații despre dispozitiv pentru integrare."""
        return {
            "identifiers": {(DOMAIN, "scomet")},
            "name": "Scomet: Administrăm confortul",
            "manufacturer": "George Neagu (geotibi)",
            "model": "Scomet: Administrăm confortul",
            "entry_type": DeviceEntryType.SERVICE,
        }

    @property
    def device_class(self):
        """Return the state class of the sensor."""
        return self._device_class

    @property
    def state_class(self):
        """Return the state class of the sensor."""
        return self._state_class

class DataScadentaSensor(CoordinatorEntity, SensorEntity):
    """Senzor pentru afișarea informațiilor despre data scadentă a facturii."""

    def __init__(self, coordinator, entry_id):
        """Inițializează senzorul Data Scadentă"""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_unique_id = f"{entry_id}_datascadenta"
        self._attr_name = "Dată scadentă factură"
        self._entity_id = f"sensor.{DOMAIN}_datascadenta"
        self._icon = "mdi:calendar-alert"
        self._device_class = "Device class"
        self._state = "State"
        self._state_class = "State class"

    @property
    def state(self):
        """Returnează starea senzorului dată scadentă."""
        _LOGGER.debug("State requested for Data scadenta: %s", self.coordinator.data)

        if self.coordinator.data is None:
            return "Unknown"

        datascadenta = self.coordinator.data.get("datascadenta")

        if datascadenta is None:
            _LOGGER.error("Eroare: DataScadentaSensor nu a găsit date în coordinator.")
            return "Unknown"

        return datascadenta

    @property
    def unique_id(self):
        """Returnează ID-ul unic al senzorului."""
        return f"{DOMAIN}_datascadenta"

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
        """Returnează iconița asociată senzorului."""
        return self._icon

    @property
    def device_info(self):
        """Informații despre dispozitiv pentru integrare."""
        return {
            "identifiers": {(DOMAIN, "scomet")},
            "name": "Scomet: Administrăm confortul",
            "manufacturer": "George Neagu (geotibi)",
            "model": "Scomet: Administrăm confortul",
            "entry_type": DeviceEntryType.SERVICE,
        }

    @property
    def device_class(self):
        """Return the state class of the sensor."""
        return self._device_class

    @property
    def state_class(self):
        """Return the state class of the sensor."""
        return self._state_class

class CosnumApaSensor(CoordinatorEntity, SensorEntity):
    """Senzor pentru afișarea informațiilor despre consumul de apă."""

    def __init__(self, coordinator, entry_id):
        """Inițializează senzorul consum apă rece"""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_unique_id = f"{entry_id}_consumaparece"
        self._attr_name = "Consum Apă Rece"
        self._entity_id = f"sensor.{DOMAIN}_consumaparece"
        self._icon = "mdi:water-pump"
        self._device_class = "Device class"
        self._state = "State"
        self._state_class = "State class"

    @property
    def state(self):
        """Returnează starea senzorului consum apă."""
        _LOGGER.debug("State requested for Consum Apa Rece: %s", self.coordinator.data)

        if self.coordinator.data is None:
            return "Unknown"

        consumaparece = self.coordinator.data.get("consumaparece")

        if consumaparece is None:
            _LOGGER.error("Eroare: ConsumApaReceSensor nu a găsit date în coordinator.")
            return "Unknown"

        return consumaparece

    @property
    def unique_id(self):
        """Returnează ID-ul unic al senzorului."""
        return f"{DOMAIN}_consumaparece"

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
        """Returnează iconița asociată senzorului."""
        return self._icon

    @property
    def device_info(self):
        """Informații despre dispozitiv pentru integrare."""
        return {
            "identifiers": {(DOMAIN, "scomet")},
            "name": "Scomet: Administrăm confortul",
            "manufacturer": "George Neagu (geotibi)",
            "model": "Scomet: Administrăm confortul",
            "entry_type": DeviceEntryType.SERVICE,
        }

    @property
    def device_class(self):
        """Return the state class of the sensor."""
        return "WATER"

    @property
    def state_class(self):
        """Return the state class of the sensor."""
        return "measurement"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of the sensor."""
        return "m³"