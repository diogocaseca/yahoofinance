![GitHub Release](https://img.shields.io/github/v/release/iprak/yahoofinance)
[![License](https://img.shields.io/packagist/l/phplicengine/bitly)](https://packagist.org/packages/phplicengine/bitly)
<a href="https://buymeacoffee.com/leolite1q" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" height="20px"></a>

## Summary

A custom component to display stock information from [Yahoo finance](https://finance.yahoo.com/).

Currency details can be presented in an different currency than what is reported (`target_currency`). Data is downloaded at regular intervals (`scan_interval`) but a retry is attempted after 20 seconds in case of failure.

Note: ```This integration will mostly only work in US mainland. Data privacy requirements like GDPR can cause requests to fail. This is as of release 1.2.12.```

## Installation

This can be installed through [HACS](https://hacs.xyz/) or by copying all the files from `custom_components/yahoofinance/` to `<config directory>/custom_components/yahoofinance/`.

## Configuration

This integration is configured from the Home Assistant UI only.

### 1. Add the integration

1. Open `Settings` > `Devices & Services`.
2. Click `Add Integration`.
3. Search for `Yahoo Finance`.
4. Fill the initial form:
   - `symbols`: symbols separated by comma (example: `PETR4.SA, VALE3.SA`)
   - `manual_scan_interval`: disable automatic updates (global)
   - `scan_interval_seconds`: automatic update interval in seconds (global)
5. Save.

Notes:
- You can create more than one Yahoo Finance integration entry.
- `scan_interval` is global for all symbols inside the same integration entry.

### 2. Change settings later

After the integration is created, open `Configure` in the same integration card.

In this screen you can:
- Add or remove symbols.
- Change the global update interval.
- Enable or disable optional data groups and display behavior.

Available advanced options:
- `target_currency`
- `show_trending_icon`
- `show_currency_symbol_as_unit`
- `decimal_places`
- `include_fifty_day_values`
- `include_post_values`
- `include_pre_values`
- `include_two_hundred_day_values`
- `include_fifty_two_week_values`
- `include_dividend_values`
- `show_off_market_values`

The above configuration will generate an entity with the id `sensor.yahoofinance_istnx` and current value as the state along with these attributes:

```
state_class: measurement
attribution: Data provided by Yahoo Finance
currencySymbol: $
symbol: ISTNX
quoteType: MUTUALFUND
quoteSourceName: Delayed Quote
marketState: PRE
averageDailyVolume10Day: 0
averageDailyVolume3Month: 0
regularMarketChange: -0.5
regularMarketChangePercent: -0.57
regularMarketDayHigh: 0
regularMarketDayLow: 0
regularMarketPreviousClose: 88.34
regularMarketPrice: 87.84
regularMarketVolume: 0
regularMarketTime: 2025-08-16T00:01:15+00:00
forwardPE: 0
trailingPE: 0
fiftyDayAverage: 83.88
fiftyDayAverageChange: 3.96
fiftyDayAverageChangePercent: 4.73
preMarketChange: 0
preMarketChangePercent: 0
preMarketTime: 0
preMarketPrice: 0
postMarketChange: 0
postMarketChangePercent: 0
postMarketPrice: 0
postMarketTime: 0
twoHundredDayAverage: 75.97
twoHundredDayAverageChange: 11.87
twoHundredDayAverageChangePercent: 15.63
fiftyTwoWeekLow: 57.36
fiftyTwoWeekLowChange: 30.48
fiftyTwoWeekLowChangePercent: 53.14
fiftyTwoWeekHigh: 88.41
fiftyTwoWeekHighChange: -0.57
fiftyTwoWeekHighChangePercent: -0.64
dividendDate: null
dividendRate: 0
dividendYield: 0
trailingAnnualDividendRate: 0
trailingAnnualDividendYield: 0
trending: down
unit_of_measurement: $
icon: mdi:trending-down
friendly_name: Delaware Ivy Science and Techno
```

#### Attributes
* The attributes can be null if there is no data present.
* The `dividendDate` is in ISO format (YYYY-MM-DD).



## Optional Configuration

### Integration

- Data fetch interval can be adjusted with:
  - `manual_scan_interval`
  - `scan_interval_seconds` (minimum 30 seconds)

- Trending icons (trending-up, trending-down or trending-neutral) can be displayed instead of currency based icon by specifying `show_trending_icon`.
  Enable `show_trending_icon` in the integration options.
- All numeric values are by default rounded to 2 places of decimal. This can be adjusted by the `decimal_places` setting. A value of 0 will return in integer values and -1 will suppress rounding.

  Set `decimal_places` in the integration options.

- The dividend, fifty_day, post, pre and two_hundred attributes can be included as following. They are all excluded by default.
  Enable the corresponding `include_*` options in the integration settings.

- Show post, pre market prices in the default sensor value, by default disabled. When enabled, it is recommended to also set `include_post_values` and `include_pre_values` to `true`.
  Enable `include_post_values`, `include_pre_values` and
  `show_off_market_values` in options.

  ### Optional attributes
  #### include_dividend_values
  - dividendDate
  - dividendRate
  - dividendYield
  - trailingAnnualDividendRate
  - trailingAnnualDividendYield

  #### include_fifty_day_values
  - fiftyDayAverage
  - fiftyDayAverageChange
  - fiftyDayAverageChangePercent

  #### include_pre_values
  - preMarketChange
  - preMarketChangePercent
  - preMarketPrice
  - preMarketTime

  #### include_post_values
  - postMarketChange
  - postMarketChangePercent
  - postMarketPrice
  - postMarketTime

  #### include_fifty_two_week_values
  - fiftyTwoWeekLow
  - fiftyTwoWeekLowChange
  - fiftyTwoWeekLowChangePercent
  - fiftyTwoWeekHigh
  - fiftyTwoWeekHighChange
  - fiftyTwoWeekHighChangePercent

  ### include_two_hundred_day_values
  - twoHundredDayAverage
  - twoHundredDayAverageChange
  - twoHundredDayAverageChangePercent

- The currency symbol e.g. $ can be shown as the unit instead of USD by
  enabling `show_currency_symbol_as_unit`.
  - **Note:** Using this setting will generate a warning like `The unit of this entity changed to '$' which can't be converted ...` You will have to manually resolve it by picking the first option to update the unit of the historicalvalues without convertion. This can be done from `Developer tools > STATISTICS`.


### Symbol

- An alternate target currency can be configured globally through the
  `target_currency` option.

  If data for the target currency is not found, then the display will remain in original currency. The conversion is only applied on the attributes representing prices.

- The data fetch interval is configured at integration level in options.

## Examples

- The symbol can also represent a financial index such as
  [this](https://finance.yahoo.com/world-indices/).

- Yahoo also provides currency conversion as a symbol.

- A complete sample setup can be created from UI by adding symbols first and
  then enabling optional values in `Configure`.

- The trending icons themselves cannot be colored but colors can be added using [lovelace-card-mod](https://github.com/thomasloven/lovelace-card-mod). Here [auto-entities](https://github.com/thomasloven/lovelace-auto-entities) is being used to simplify the code.

  ```
  - type: custom:auto-entities
    card:
      type: entities
      title: Financial
    filter:
      include:
        - group: group.stocks
          options:
            entity: this.entity_id
            style: |
              :host {
                --paper-item-icon-color: {% set value=state_attr(config.entity,"trending") %}
                                        {% if value=="up" -%} green
                                        {% elif value=="down" -%} red
                                        {% else %} var(--paper-item-icon-color))
                                        {% endif %};
  ```

## Services

* The component exposes the service `yahoofinance.refresh_symbols` which can be used to refresh all the data.

## Events

* The event `yahoofinance_data_updated` is sent when data is updated. It contains the list of symbols updated. This can be used to take actions upon data update.


## Breaking Changes
- 2.0.0 - Item configuration is now handled via the UI. YAML configurations are no longer supported.
- 1.5.0 - All dividend values are controlled by the new setting `include_dividend_values`. The fifty_day, post, pre, two_hundred and dividend attributes are now `excluded` by default.
- As of version [1.2.5](https://github.com/iprak/yahoofinance/releases/), `scan_interval` can be `manual` to suppress automatic update.

- As of version [1.1.0](https://github.com/iprak/yahoofinance/releases/), the entity id has changed from `yahoofinance.symbol` to `sensor.yahoofinance_symbol`.
- As of version 1.0.0, all the configuration is now under `yahoofinance`. If you are upgrading from an older version, then you would need to adjust the configuration.
- As of version 1.0.1, the minimum `scan_interval` is 30 seconds.