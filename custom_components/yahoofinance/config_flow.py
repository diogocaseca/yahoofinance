"""Config flow for Yahoo Finance integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, OptionsFlowWithConfigEntry
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from . import DEFAULT_ENTRY_OPTIONS
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
    DOMAIN,
)

OPT_SYMBOLS = "Symbols"
OPT_MANUAL_SCAN = "Disable automatic updates"
OPT_SCAN_SECONDS = "Global automatic update interval (seconds)"
OPT_TARGET_CURRENCY = "Target currency (optional)"
OPT_SHOW_TRENDING = "Show trending icon"
OPT_SHOW_CURRENCY_SYMBOL = "Use currency symbol as unit"
OPT_DECIMAL_PLACES = "Decimal places"
OPT_INCLUDE_FIFTY_DAY = "Include 50-day values"
OPT_INCLUDE_POST = "Include post-market values"
OPT_INCLUDE_PRE = "Include pre-market values"
OPT_INCLUDE_TWO_HUNDRED_DAY = "Include 200-day values"
OPT_INCLUDE_FIFTY_TWO_WEEK = "Include 52-week values"
OPT_INCLUDE_DIVIDEND = "Include dividend values"
OPT_SHOW_OFF_MARKET = "Use latest off-market value as state"


def _parse_symbols(raw_symbols: str) -> list[str]:
    """Parse a free-text list of symbols into uppercase unique values."""
    split_values = raw_symbols.replace("\n", ",").split(",")
    parsed: list[str] = []

    for item in split_values:
        symbol = item.strip().upper()
        if symbol != "" and symbol not in parsed:
            parsed.append(symbol)

    return parsed


class YahooFinanceConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Yahoo Finance."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Handle the initial setup step with only required fields."""

        errors: dict[str, str] = {}

        if user_input is not None:
            symbols = _parse_symbols(user_input[CONF_SYMBOLS])
            if len(symbols) == 0:
                errors[CONF_SYMBOLS] = "symbols_required"
            else:
                title = "Yahoo Finance"
                if symbols:
                    title = f"Yahoo Finance ({symbols[0]})"

                return self.async_create_entry(
                    title=title,
                    data={
                        CONF_SYMBOLS: symbols,
                        CONF_MANUAL_SCAN_INTERVAL: user_input[
                            CONF_MANUAL_SCAN_INTERVAL
                        ],
                        CONF_SCAN_INTERVAL_SECONDS: user_input[
                            CONF_SCAN_INTERVAL_SECONDS
                        ],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SYMBOLS): str,
                    vol.Required(
                        CONF_MANUAL_SCAN_INTERVAL,
                        default=DEFAULT_ENTRY_OPTIONS[CONF_MANUAL_SCAN_INTERVAL],
                    ): bool,
                    vol.Required(
                        CONF_SCAN_INTERVAL_SECONDS,
                        default=DEFAULT_ENTRY_OPTIONS[CONF_SCAN_INTERVAL_SECONDS],
                    ): vol.All(vol.Coerce(int), vol.Range(min=30)),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Create the options flow."""
        return YahooFinanceOptionsFlow(config_entry)


class YahooFinanceOptionsFlow(OptionsFlowWithConfigEntry):
    """Handle Yahoo Finance options."""

    async def async_step_init(self, user_input: dict | None = None) -> FlowResult:
        """Manage options for an existing Yahoo Finance config entry."""

        errors: dict[str, str] = {}

        if user_input is not None:
            symbols = _parse_symbols(user_input[OPT_SYMBOLS])
            if len(symbols) == 0:
                errors["base"] = "symbols_required"
            else:
                options_data = {
                    CONF_SYMBOLS: symbols,
                    CONF_MANUAL_SCAN_INTERVAL: user_input[OPT_MANUAL_SCAN],
                    CONF_SCAN_INTERVAL_SECONDS: user_input[OPT_SCAN_SECONDS],
                    CONF_TARGET_CURRENCY: user_input[OPT_TARGET_CURRENCY],
                    CONF_SHOW_TRENDING_ICON: user_input[OPT_SHOW_TRENDING],
                    CONF_SHOW_CURRENCY_SYMBOL_AS_UNIT: user_input[
                        OPT_SHOW_CURRENCY_SYMBOL
                    ],
                    CONF_DECIMAL_PLACES: user_input[OPT_DECIMAL_PLACES],
                    CONF_INCLUDE_FIFTY_DAY_VALUES: user_input[OPT_INCLUDE_FIFTY_DAY],
                    CONF_INCLUDE_POST_VALUES: user_input[OPT_INCLUDE_POST],
                    CONF_INCLUDE_PRE_VALUES: user_input[OPT_INCLUDE_PRE],
                    CONF_INCLUDE_TWO_HUNDRED_DAY_VALUES: user_input[
                        OPT_INCLUDE_TWO_HUNDRED_DAY
                    ],
                    CONF_INCLUDE_FIFTY_TWO_WEEK_VALUES: user_input[
                        OPT_INCLUDE_FIFTY_TWO_WEEK
                    ],
                    CONF_INCLUDE_DIVIDEND_VALUES: user_input[OPT_INCLUDE_DIVIDEND],
                    CONF_SHOW_OFF_MARKET_VALUES: user_input[OPT_SHOW_OFF_MARKET],
                }

                target_currency = options_data.get(CONF_TARGET_CURRENCY)
                if isinstance(target_currency, str):
                    options_data[CONF_TARGET_CURRENCY] = (
                        target_currency.upper().strip()
                    )

                return self.async_create_entry(title="", data=options_data)

        options = DEFAULT_ENTRY_OPTIONS.copy()
        options.update(self.config_entry.data)
        options.update(self.config_entry.options)
        symbols = options.get(CONF_SYMBOLS, self.config_entry.data.get(CONF_SYMBOLS, []))
        symbols_as_text = ", ".join(symbols)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        OPT_SYMBOLS,
                        default=symbols_as_text,
                    ): str,
                    vol.Required(
                        OPT_MANUAL_SCAN,
                        default=options[CONF_MANUAL_SCAN_INTERVAL],
                    ): bool,
                    vol.Required(
                        OPT_SCAN_SECONDS,
                        default=options[CONF_SCAN_INTERVAL_SECONDS],
                    ): vol.All(vol.Coerce(int), vol.Range(min=30)),
                    vol.Optional(
                        OPT_TARGET_CURRENCY,
                        default=options.get(CONF_TARGET_CURRENCY) or "",
                    ): str,
                    vol.Required(
                        OPT_SHOW_TRENDING,
                        default=options[CONF_SHOW_TRENDING_ICON],
                    ): bool,
                    vol.Required(
                        OPT_SHOW_CURRENCY_SYMBOL,
                        default=options[CONF_SHOW_CURRENCY_SYMBOL_AS_UNIT],
                    ): bool,
                    vol.Required(
                        OPT_DECIMAL_PLACES,
                        default=options[CONF_DECIMAL_PLACES],
                    ): vol.Coerce(int),
                    vol.Required(
                        OPT_INCLUDE_FIFTY_DAY,
                        default=options[CONF_INCLUDE_FIFTY_DAY_VALUES],
                    ): bool,
                    vol.Required(
                        OPT_INCLUDE_POST,
                        default=options[CONF_INCLUDE_POST_VALUES],
                    ): bool,
                    vol.Required(
                        OPT_INCLUDE_PRE,
                        default=options[CONF_INCLUDE_PRE_VALUES],
                    ): bool,
                    vol.Required(
                        OPT_INCLUDE_TWO_HUNDRED_DAY,
                        default=options[CONF_INCLUDE_TWO_HUNDRED_DAY_VALUES],
                    ): bool,
                    vol.Required(
                        OPT_INCLUDE_FIFTY_TWO_WEEK,
                        default=options[CONF_INCLUDE_FIFTY_TWO_WEEK_VALUES],
                    ): bool,
                    vol.Required(
                        OPT_INCLUDE_DIVIDEND,
                        default=options[CONF_INCLUDE_DIVIDEND_VALUES],
                    ): bool,
                    vol.Required(
                        OPT_SHOW_OFF_MARKET,
                        default=options[CONF_SHOW_OFF_MARKET_VALUES],
                    ): bool,
                }
            ),
            errors=errors,
        )
