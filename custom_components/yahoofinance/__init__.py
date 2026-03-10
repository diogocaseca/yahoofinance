"""The Yahoo finance component.

https://github.com/iprak/yahoofinance
"""

from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_create_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_DECIMAL_PLACES,
    CONF_INCLUDE_DIVIDEND_VALUES,
    CONF_INCLUDE_FIFTY_DAY_VALUES,
    CONF_INCLUDE_FIFTY_TWO_WEEK_VALUES,
    CONF_INCLUDE_POST_VALUES,
    CONF_INCLUDE_PRE_VALUES,
    CONF_INCLUDE_TWO_HUNDRED_DAY_VALUES,
    CONF_MANUAL_SCAN_INTERVAL,
    CONF_SCAN_INTERVAL_SECONDS,
    CONF_SHOW_CURRENCY_SYMBOL_AS_UNIT,
    CONF_SHOW_OFF_MARKET_VALUES,
    CONF_SHOW_TRENDING_ICON,
    CONF_SYMBOLS,
    CONF_TARGET_CURRENCY,
    DEFAULT_CONF_DECIMAL_PLACES,
    DEFAULT_CONF_INCLUDE_DIVIDEND_VALUES,
    DEFAULT_CONF_INCLUDE_FIFTY_DAY_VALUES,
    DEFAULT_CONF_INCLUDE_FIFTY_TWO_WEEK_VALUES,
    DEFAULT_CONF_INCLUDE_POST_VALUES,
    DEFAULT_CONF_INCLUDE_PRE_VALUES,
    DEFAULT_CONF_INCLUDE_TWO_HUNDRED_DAY_VALUES,
    DEFAULT_CONF_SHOW_CURRENCY_SYMBOL_AS_UNIT,
    DEFAULT_CONF_SHOW_OFF_MARKET_VALUES,
    DEFAULT_CONF_SHOW_TRENDING_ICON,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    HASS_DATA_CONFIG,
    HASS_DATA_COORDINATORS,
    HASS_DATA_ENTRIES,
    HASS_DATA_SERVICES_REGISTERED,
    LOGGER,
    MANUAL_SCAN_INTERVAL,
    MAX_LINE_SIZE,
    MINIMUM_SCAN_INTERVAL,
    SERVICE_REFRESH,
)
from .coordinator import CrumbCoordinator, YahooSymbolUpdateCoordinator
from .dataclasses import SymbolDefinition

PLATFORMS: list[Platform] = [Platform.SENSOR]

DEFAULT_ENTRY_OPTIONS = {
    CONF_SCAN_INTERVAL_SECONDS: int(DEFAULT_SCAN_INTERVAL.total_seconds()),
    CONF_MANUAL_SCAN_INTERVAL: False,
    CONF_TARGET_CURRENCY: None,
    CONF_SHOW_TRENDING_ICON: DEFAULT_CONF_SHOW_TRENDING_ICON,
    CONF_SHOW_CURRENCY_SYMBOL_AS_UNIT: DEFAULT_CONF_SHOW_CURRENCY_SYMBOL_AS_UNIT,
    CONF_DECIMAL_PLACES: DEFAULT_CONF_DECIMAL_PLACES,
    CONF_INCLUDE_FIFTY_DAY_VALUES: DEFAULT_CONF_INCLUDE_FIFTY_DAY_VALUES,
    CONF_INCLUDE_POST_VALUES: DEFAULT_CONF_INCLUDE_POST_VALUES,
    CONF_INCLUDE_PRE_VALUES: DEFAULT_CONF_INCLUDE_PRE_VALUES,
    CONF_INCLUDE_TWO_HUNDRED_DAY_VALUES: DEFAULT_CONF_INCLUDE_TWO_HUNDRED_DAY_VALUES,
    CONF_INCLUDE_FIFTY_TWO_WEEK_VALUES: DEFAULT_CONF_INCLUDE_FIFTY_TWO_WEEK_VALUES,
    CONF_INCLUDE_DIVIDEND_VALUES: DEFAULT_CONF_INCLUDE_DIVIDEND_VALUES,
    CONF_SHOW_OFF_MARKET_VALUES: DEFAULT_CONF_SHOW_OFF_MARKET_VALUES,
}


CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


def normalize_input_symbols(defined_symbols: list[str]) -> list[SymbolDefinition]:
    """Normalize symbols and remove duplicates."""
    symbols: set[str] = set()
    symbol_definitions: list[SymbolDefinition] = []

    for value in defined_symbols:
        symbol = value.upper()
        if symbol in symbols:
            continue
        symbols.add(symbol)
        symbol_definitions.append(SymbolDefinition(symbol))

    return symbol_definitions


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the component (UI configuration only)."""

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(HASS_DATA_ENTRIES, {})

    _async_register_services(hass)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Yahoo Finance from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(HASS_DATA_ENTRIES, {})

    _async_register_services(hass)

    domain_config = _domain_config_from_entry(entry)
    coordinators = await _async_setup_coordinators(
        hass,
        domain_config[CONF_SYMBOLS],
        domain_config[CONF_SCAN_INTERVAL],
    )

    if coordinators is None:
        raise ConfigEntryNotReady("Unable to get Yahoo Finance crumb")

    hass.data[DOMAIN][HASS_DATA_ENTRIES][entry.entry_id] = {
        HASS_DATA_CONFIG: domain_config,
        HASS_DATA_COORDINATORS: coordinators,
    }

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if not unload_ok:
        return False

    entry_data = hass.data.get(DOMAIN, {}).get(HASS_DATA_ENTRIES, {}).pop(
        entry.entry_id, None
    )
    if entry_data:
        await _async_shutdown_coordinators(entry_data.get(HASS_DATA_COORDINATORS, {}))

    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options change."""

    await hass.config_entries.async_reload(entry.entry_id)


def _async_register_services(hass: HomeAssistant) -> None:
    """Register services once for both YAML and UI configured entries."""

    if hass.data[DOMAIN].get(HASS_DATA_SERVICES_REGISTERED):
        return

    async def handle_refresh_symbols(_call: ServiceCall) -> None:
        """Refresh symbol data."""
        LOGGER.info("Processing refresh_symbols")

        coordinators: dict[
            str | timedelta, YahooSymbolUpdateCoordinator
        ] = hass.data[
            DOMAIN
        ].get(HASS_DATA_COORDINATORS, {})
        if coordinators:
            for coordinator in coordinators.values():
                await coordinator.async_refresh()

        entries = hass.data[DOMAIN].get(HASS_DATA_ENTRIES, {})
        for entry_data in entries.values():
            for coordinator in entry_data.get(HASS_DATA_COORDINATORS, {}).values():
                await coordinator.async_refresh()

    hass.services.async_register(DOMAIN, SERVICE_REFRESH, handle_refresh_symbols)
    hass.data[DOMAIN][HASS_DATA_SERVICES_REGISTERED] = True


async def _async_setup_coordinators(
    hass: HomeAssistant,
    symbol_definitions: list[SymbolDefinition],
    global_scan_interval: str | timedelta,
) -> dict[str | timedelta, YahooSymbolUpdateCoordinator] | None:
    """Create and refresh coordinators for symbols grouped by scan interval."""

    symbols_by_scan_interval: dict[str | timedelta, list[str]] = {}
    for symbol in symbol_definitions:
        if symbol.scan_interval is None:
            symbol.scan_interval = global_scan_interval

        if symbol.scan_interval in symbols_by_scan_interval:
            symbols_by_scan_interval[symbol.scan_interval].append(symbol.symbol)
        else:
            symbols_by_scan_interval[symbol.scan_interval] = [symbol.symbol]

    LOGGER.info("Total %d unique scan intervals", len(symbols_by_scan_interval))

    # Testing showed that the response header for initial request can be up to 40KB.
    websession = async_create_clientsession(
        hass, max_field_size=MAX_LINE_SIZE, max_line_size=MAX_LINE_SIZE
    )

    crumb_coordinator = CrumbCoordinator.get_static_instance(hass, websession)

    crumb = await crumb_coordinator.try_get_crumb_cookies()
    if crumb is None:
        return None

    coordinators: dict[str | timedelta, YahooSymbolUpdateCoordinator] = {}
    for key_scan_interval, symbols in symbols_by_scan_interval.items():
        LOGGER.info(
            "Creating coordinator with scan_interval %s for symbols %s",
            key_scan_interval,
            symbols,
        )
        coordinator = YahooSymbolUpdateCoordinator(
            symbols, hass, key_scan_interval, crumb_coordinator, websession
        )
        coordinators[key_scan_interval] = coordinator

        LOGGER.info(
            "Requesting initial data from coordinator with update interval of %s",
            key_scan_interval,
        )
        await coordinator.async_refresh()

    for coordinator in coordinators.values():
        if not coordinator.last_update_success:
            LOGGER.debug("Coordinator did not report any data, requesting async_refresh")
            hass.async_create_task(coordinator.async_request_refresh())

    return coordinators


async def _async_shutdown_coordinators(
    coordinators: dict[str | timedelta, YahooSymbolUpdateCoordinator],
) -> None:
    """Shutdown coordinator resources."""

    for coordinator in coordinators.values():
        await coordinator.async_shutdown()


def _domain_config_from_entry(entry: ConfigEntry) -> dict:
    """Build runtime domain config from config entry data and options."""

    options = DEFAULT_ENTRY_OPTIONS.copy()
    options.update(entry.options)

    scan_interval: str | timedelta = MANUAL_SCAN_INTERVAL
    if not options[CONF_MANUAL_SCAN_INTERVAL]:
        scan_seconds_value = options.get(
            CONF_SCAN_INTERVAL_SECONDS,
            int(DEFAULT_SCAN_INTERVAL.total_seconds()),
        )
        if scan_seconds_value is None:
            scan_seconds_value = int(DEFAULT_SCAN_INTERVAL.total_seconds())

        scan_seconds = max(
            int(scan_seconds_value),
            int(MINIMUM_SCAN_INTERVAL.total_seconds()),
        )
        scan_interval = timedelta(seconds=scan_seconds)

    symbols = [symbol.upper() for symbol in entry.data.get(CONF_SYMBOLS, [])]
    symbol_definitions = normalize_input_symbols(symbols)

    target_currency = options.get(CONF_TARGET_CURRENCY)
    if isinstance(target_currency, str) and target_currency != "":
        target_currency = target_currency.upper()
    elif target_currency == "":
        target_currency = None

    domain_config = {
        CONF_SYMBOLS: symbol_definitions,
        CONF_SCAN_INTERVAL: scan_interval,
        CONF_TARGET_CURRENCY: target_currency,
        CONF_SHOW_TRENDING_ICON: options[CONF_SHOW_TRENDING_ICON],
        CONF_SHOW_CURRENCY_SYMBOL_AS_UNIT: options[CONF_SHOW_CURRENCY_SYMBOL_AS_UNIT],
        CONF_DECIMAL_PLACES: options[CONF_DECIMAL_PLACES],
        CONF_INCLUDE_FIFTY_DAY_VALUES: options[CONF_INCLUDE_FIFTY_DAY_VALUES],
        CONF_INCLUDE_POST_VALUES: options[CONF_INCLUDE_POST_VALUES],
        CONF_INCLUDE_PRE_VALUES: options[CONF_INCLUDE_PRE_VALUES],
        CONF_INCLUDE_TWO_HUNDRED_DAY_VALUES: options[
            CONF_INCLUDE_TWO_HUNDRED_DAY_VALUES
        ],
        CONF_INCLUDE_FIFTY_TWO_WEEK_VALUES: options[
            CONF_INCLUDE_FIFTY_TWO_WEEK_VALUES
        ],
        CONF_INCLUDE_DIVIDEND_VALUES: options[CONF_INCLUDE_DIVIDEND_VALUES],
        CONF_SHOW_OFF_MARKET_VALUES: options[CONF_SHOW_OFF_MARKET_VALUES],
    }

    return domain_config


def convert_to_float(value) -> float | None:
    """Convert specified value to float."""
    try:
        return float(value)
    except Exception:
        return None
