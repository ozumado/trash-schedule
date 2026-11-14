"""Native Home Assistant calendar entity, one per configured address."""
from datetime import date, datetime, time, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([TrashCalendar(entry.runtime_data, entry)])


class TrashCalendar(CoordinatorEntity, CalendarEntity):
    _attr_icon = "mdi:trash-can"
    _attr_has_entity_name = False

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_name = entry.title
        self._attr_unique_id = f"{entry.entry_id}_collections"

    def _all_events(self):
        events = []
        for item in self.coordinator.data or []:
            try:
                start = date.fromisoformat(item["date"])
                summary = item["summary"]
                if not isinstance(summary, str) or not summary:
                    continue
                events.append(CalendarEvent(
                    start=start, end=start + timedelta(days=1),
                    summary=summary, description=summary
                ))
            except (KeyError, TypeError, ValueError):
                continue
        return sorted(events, key=lambda event: (event.start, event.summary))

    @property
    def event(self):
        today = dt_util.now().date()
        return next((event for event in self._all_events() if event.end > today), None)

    async def async_get_events(self, hass, start_date: datetime, end_date: datetime):
        tz = start_date.tzinfo
        return [
            event for event in self._all_events()
            if datetime.combine(event.end, time.min, tz) > start_date
            and datetime.combine(event.start, time.min, tz) < end_date
        ]
