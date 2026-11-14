"""Home Assistant integration for directly fetched trash collection calendars."""
import logging
from datetime import timedelta
from urllib.parse import urlencode

from aiohttp import ClientError, ClientTimeout
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .config_flow import CONF_GMINA_ID, CONF_STREET
from .const import DOMAIN
from .parser import parse_schedule

_LOGGER = logging.getLogger(__name__)
BASE_URL = "https://cloud.fxsystems.com.pl/OdbiorySmieci/HarmonogramOnline.dll"
REFRESH_INTERVAL = timedelta(hours=24)
RETRY_INTERVAL = timedelta(hours=1)


class TrashCoordinator(DataUpdateCoordinator[list[dict]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        super().__init__(
            hass, _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=REFRESH_INTERVAL,
        )
        self.entry = entry
        self.store = Store(hass, 1, f"{DOMAIN}_{entry.entry_id}")

    async def _async_update_data(self):
        params = urlencode({
            "gmina_id": self.entry.data[CONF_GMINA_ID],
            "ulica": self.entry.data[CONF_STREET],
        })
        try:
            session = async_get_clientsession(self.hass)
            async with session.get(
                f"{BASE_URL}?{params}", timeout=ClientTimeout(total=45),
                headers={"User-Agent": "Mozilla/5.0"}
            ) as response:
                response.raise_for_status()
                html = await response.text()
            events = parse_schedule(html)
            await self.store.async_save({"events": events})
            self.update_interval = REFRESH_INTERVAL
            _LOGGER.info("Updated Trash Schedule for %s (%d events)", self.entry.title, len(events))
            return events
        except (ClientError, TimeoutError, UnicodeError, ValueError) as err:
            self.update_interval = RETRY_INTERVAL
            _LOGGER.warning("Could not refresh %s: %s; retrying in one hour", self.entry.title, err)
            if self.data is not None:
                return self.data
            cached = await self.store.async_load()
            if isinstance(cached, dict) and isinstance(cached.get("events"), list):
                return cached["events"]
            raise UpdateFailed(f"Unable to download trash schedule: {err}") from err


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    if not entry.data.get(CONF_GMINA_ID) or not entry.data.get(CONF_STREET):
        _LOGGER.error("Trash Schedule configuration is missing municipality or street; remove and add the integration again")
        return False
    coordinator = TrashCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, ["calendar"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    return await hass.config_entries.async_unload_platforms(entry, ["calendar"])
