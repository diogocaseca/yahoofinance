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
                await self.async_set_unique_id("single_instance")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title="Yahoo Finance",
                    data={CONF_SYMBOLS: symbols},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SYMBOLS): str,
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
            symbols = _parse_symbols(user_input[CONF_SYMBOLS])
            if len(symbols) == 0:
                errors["base"] = "symbols_required"
            else:
                user_input[CONF_SYMBOLS] = symbols

            target_currency = user_input.get(CONF_TARGET_CURRENCY)
            if isinstance(target_currency, str):
                user_input[CONF_TARGET_CURRENCY] = target_currency.upper().strip()

                return self.async_create_entry(title="", data=user_input)

        options = DEFAULT_ENTRY_OPTIONS.copy()
        options.update(self.config_entry.options)
        symbols = options.get(CONF_SYMBOLS, self.config_entry.data.get(CONF_SYMBOLS, []))
        symbols_as_text = ", ".join(symbols)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SYMBOLS,
                        default=symbols_as_text,
                    ): str,
                    vol.Required(
                        CONF_MANUAL_SCAN_INTERVAL,
                        default=options[CONF_MANUAL_SCAN_INTERVAL],
                    ): bool,
                    vol.Required(
                        CONF_SCAN_INTERVAL_SECONDS,
                        default=options[CONF_SCAN_INTERVAL_SECONDS],
                    ): vol.All(vol.Coerce(int), vol.Range(min=30)),
                    vol.Optional(
                        CONF_TARGET_CURRENCY,
                        default=options.get(CONF_TARGET_CURRENCY) or "",
                    ): str,
                    vol.Required(
                        CONF_SHOW_TRENDING_ICON,
                        default=options[CONF_SHOW_TRENDING_ICON],
                    ): bool,
                    vol.Required(
                        CONF_SHOW_CURRENCY_SYMBOL_AS_UNIT,
                        default=options[CONF_SHOW_CURRENCY_SYMBOL_AS_UNIT],
                    ): bool,
                    vol.Required(
                        CONF_DECIMAL_PLACES,
                        default=options[CONF_DECIMAL_PLACES],
                    ): vol.Coerce(int),
                    vol.Required(
                        CONF_INCLUDE_FIFTY_DAY_VALUES,
                        default=options[CONF_INCLUDE_FIFTY_DAY_VALUES],
                    ): bool,
                    vol.Required(
                        CONF_INCLUDE_POST_VALUES,
                        default=options[CONF_INCLUDE_POST_VALUES],
                    ): bool,
                    vol.Required(
                        CONF_INCLUDE_PRE_VALUES,
                        default=options[CONF_INCLUDE_PRE_VALUES],
                    ): bool,
                    vol.Required(
                        CONF_INCLUDE_TWO_HUNDRED_DAY_VALUES,
                        default=options[CONF_INCLUDE_TWO_HUNDRED_DAY_VALUES],
                    ): bool,
                    vol.Required(
                        CONF_INCLUDE_FIFTY_TWO_WEEK_VALUES,
                        default=options[CONF_INCLUDE_FIFTY_TWO_WEEK_VALUES],
                    ): bool,
                    vol.Required(
                        CONF_INCLUDE_DIVIDEND_VALUES,
                        default=options[CONF_INCLUDE_DIVIDEND_VALUES],
                    ): bool,
                    vol.Required(
                        CONF_SHOW_OFF_MARKET_VALUES,
                        default=options[CONF_SHOW_OFF_MARKET_VALUES],
                    ): bool,
                }
            ),
            errors=errors,
        )
