# Mean Well XDR

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![Open your Home Assistant instance and show the repository in HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=kulisau&repository=meanwell_xdr-hacs&category=integration)
[![Validate](https://github.com/kulisau/meanwell_xdr-hacs/actions/workflows/validate.yml/badge.svg)](https://github.com/kulisau/meanwell_xdr-hacs/actions/workflows/validate.yml)
[![Lint](https://github.com/kulisau/meanwell_xdr-hacs/actions/workflows/lint.yml/badge.svg)](https://github.com/kulisau/meanwell_xdr-hacs/actions/workflows/lint.yml)
[![License](https://img.shields.io/github/license/kulisau/meanwell_xdr-hacs)](LICENSE)

Home Assistant custom integration for
[Mean Well XDR series](https://www.meanwell.com) DIN-rail power supplies
(XDR-240 / XDR-480 / XDR-960 in 12/24/36/48 V variants) over Modbus.

The device model comes from the [`xdr-modbus`](../xdr-modbus) Python library,
which is **vendored** into this repository (`custom_components/meanwell_xdr/vendor/`),
so installing this integration needs no extra PyPI package beyond the
[`modbus-connection`](https://github.com/home-assistant-libs/modbus-connection)
framework.

> **Prerequisite:** Home Assistant **2026.9.0 or newer**. This integration
> borrows its Modbus connection through Home Assistant's shared-connection
> support in the built-in `modbus` integration: integrations that ask for the
> same link with the same settings share one connection, each talking to its
> own slave address. No `modbus:` YAML is needed.

## Installation (HACS)

1. Click the **"Open in HACS"** badge at the top of this page (or in HACS:
   **⋮ (top-right menu) → Custom repositories**, paste
   `https://github.com/kulisau/meanwell_xdr-hacs`, category *Integration*).
2. Install **Mean Well XDR**.
3. Restart Home Assistant.
4. Add the integration (*Settings → Devices & services → Add integration →
   Mean Well XDR*) and enter the host and port of the Modbus TCP gateway the
   power supply is attached to, plus its slave address (factory default
   **131** = 0x83).

Repeat the last step for every power supply on the bus (e.g. a second unit
at 132 = 0x84); entries with the same host and port share one connection.

## Entities

| Platform | Entities |
|---|---|
| Sensor | Input/output voltage, output current, internal temperature, output power; total/session runtime; OVP/OLP/OTP/ACUVP/ACOVP trigger counters; 3-deep fault event log; live scaling factors |
| Binary sensor | OTP, OVP, OLP, AC fail, high temperature, back-EMF, overload pre-alarm, EEPROM error (PROBLEM); DC OK; output state |
| Switch | Output power; Modbus control source (MOD_CTRL) |
| Number | Voltage/current setpoints (model-aware limits); AC failover/recovery thresholds; DC OK threshold; peak current limit; overload alarm level |
| Select | Baud rate, frame format, power-on behavior, overload protection mode, EEPROM mode |

> **Note:** the output switch and the voltage/current setpoints only take
> effect when the *Modbus control* switch is on (SYSTEM_CONFIG.MOD_CTRL),
> followed by an AC power cycle of the supply — the device defaults to
> potentiometer (SVR) control.

## Development

The devcontainer (or `scripts/setup` + `scripts/develop`) starts Home
Assistant with this integration loaded from `custom_components/`. The
vendored library has its own test-suite; see the
[`xdr-modbus` repository](https://github.com/kulisau/xdr-modbus).

## Disclaimer

This integration is a community project and is not affiliated with Mean Well
Enterprises Co., Ltd. Use at your own risk; writing setpoints or configuration
to a power supply affects the hardware it feeds.

## License

[Apache-2.0](LICENSE)
