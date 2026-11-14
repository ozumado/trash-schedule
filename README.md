# Trash Schedule

A standalone **Home Assistant custom integration** providing a native waste collection calendar from FX Systems.

**No add-on, Docker container, ICS, MQTT, or external calendar integration is required.**

## Install with HACS

1. Open **HACS → Integrations → ⋮ → Custom repositories**.
2. Enter `https://github.com/ozumado/trash-schedule` and select **Integration**.
3. Download **Trash Schedule** and restart Home Assistant.
4. Open **Settings → Devices & services → Add integration → Trash Schedule**.
5. Enter your municipality ID (**gmina_id**) and street name (**ulica**).

For another location, add the integration again with a different municipality ID and/or street.

## Manual install

Copy the repository's `custom_components/trash_schedule/` directory to your Home Assistant configuration's `custom_components/trash_schedule/` directory. Restart Home Assistant, then add **Trash Schedule** under **Devices & services**.

## Features

- A native `CalendarEntity` for each configured municipality/street.
- Schedule downloaded directly by Home Assistant on setup and every **24 hours**.
- Schedule entries are parsed from `.schedule-card` HTML blocks and displayed as separate all-day events.
- Automatic retry after one hour on download errors.
- Last successful schedule cached in Home Assistant's storage.
- No preset street or municipality ID in the repository.

## Migrating from the former add-on

1. Stop and uninstall the old **Trash Schedule** add-on.
2. Install this integration using HACS or manually. Because the old add-on may have copied files into `custom_components/trash_schedule`, overwrite those files with the new version.
3. Restart Home Assistant.
4. Remove any old **Trash Schedule** integration entry that does not have municipality and street settings, then add it again.

The remote schedule host is `cloud.fxsystems.com.pl`. Municipality ID and street are stored in the Home Assistant config entry, not in the source code.
