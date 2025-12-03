# Energy Price Level

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Een Home Assistant integratie die energieprijsniveaus berekent op basis van een bestaande prijssensor (zoals ENTSO-e, Nordpool, etc.).

A Home Assistant integration that calculates energy price levels based on an existing price sensor (such as ENTSO-e, Nordpool, etc.).

## Doel / Purpose

🇳🇱 **Nederlands:**
Energieprijzen zijn publiek beschikbaar via bestaande integraties (b.v. ENTSO-e, Nordpool, etc.). Deze integraties voorzien veelal niet in het beschikbaar stellen van een logisch prijsniveau welke gebruikt kan worden voor automatiseringen. Deze integratie berekent prijsniveaus op basis van een bestaande prijssensor en stelt deze beschikbaar in een nieuwe sensor.

🇬🇧 **English:**
Energy prices are publicly available through existing integrations (e.g., ENTSO-e, Nordpool, etc.). These integrations often don't provide a logical price level that can be used for automations. This integration calculates price levels based on an existing price sensor and makes them available in a new sensor.

## Methodiek / Methodology

De integratie werkt als volgt:
1. Selecteer een sensor die de gemiddelde dagprijs bevat met als attributen de uurprijzen
2. Bereken per uurprijs het prijsniveau door de uurprijs te vergelijken met het daggemiddelde
3. Stel het huidige prijsniveau beschikbaar als sensor state
4. Stel alle prijsniveaus beschikbaar als sensor attributen

The integration works as follows:
1. Select a sensor containing the average daily price with hourly prices as attributes
2. Calculate the price level for each hourly price by comparing it to the daily average
3. Provide the current price level as sensor state
4. Provide all price levels as sensor attributes

### Prijsniveaus / Price Levels

| Niveau / Level | Drempel / Threshold | Nederlands | English |
|----------------|---------------------|------------|---------|
| `zeer_goedkoop` | ≤ 60% | Zeer Goedkoop | Very Cheap |
| `goedkoop` | > 60% en ≤ 90% | Goedkoop | Cheap |
| `normaal` | > 90% en < 115% | Normaal | Normal |
| `duur` | ≥ 115% en < 140% | Duur | Expensive |
| `zeer_duur` | ≥ 140% | Zeer Duur | Very Expensive |

## Installatie / Installation

### Via HACS (aanbevolen / recommended)

1. Open HACS in Home Assistant
2. Ga naar "Integrations"
3. Klik op de drie puntjes rechtsboven
4. Selecteer "Custom repositories"
5. Voeg deze repository toe: `https://github.com/tRoOlos/ha-energy-price-level`
6. Categorie: Integration
7. Klik op "Download"
8. Herstart Home Assistant

### Handmatig / Manual

1. Kopieer de `custom_components/energy_price_level` folder naar je Home Assistant `custom_components` folder
2. Herstart Home Assistant

## Configuratie / Configuration

De integratie wordt geconfigureerd via de UI (geen YAML nodig):

1. Ga naar Instellingen → Apparaten & Diensten
2. Klik op "+ Integratie toevoegen"
3. Zoek naar "Energy Price Level"
4. Selecteer de bron prijssensor (bijvoorbeeld je ENTSO-e of Nordpool sensor)
5. Klik op "Verzenden"

The integration is configured via the UI (no YAML needed):

1. Go to Settings → Devices & Services
2. Click "+ Add Integration"
3. Search for "Energy Price Level"
4. Select the source price sensor (e.g., your ENTSO-e or Nordpool sensor)
5. Click "Submit"

## Gebruik / Usage

### Sensor State

De sensor state bevat het huidige prijsniveau:
- `zeer_goedkoop` / Very Cheap
- `goedkoop` / Cheap
- `normaal` / Normal
- `duur` / Expensive
- `zeer_duur` / Very Expensive

### Sensor Attributen / Sensor Attributes

De sensor heeft de volgende attributen:

```yaml
source_sensor: sensor.energy_price
daily_average: 0.25
current_hour: 14
price_levels:
  "00:00":
    level: goedkoop
    price: 0.20
    percentage: 80.0
  "01:00":
    level: zeer_goedkoop
    price: 0.15
    percentage: 60.0
  # ... etc voor alle uren
```

### Automatisering Voorbeeld / Automation Example

🇳🇱 **Nederlands - Start wasmachine bij goedkope prijzen:**

```yaml
automation:
  - alias: "Start wasmachine bij lage energieprijs"
    trigger:
      - platform: state
        entity_id: sensor.price_level
        to:
          - "zeer_goedkoop"
          - "goedkoop"
    condition:
      - condition: time
        after: "08:00:00"
        before: "22:00:00"
    action:
      - service: notify.mobile_app
        data:
          message: "Energieprijs is nu laag! Goed moment om de wasmachine te starten."
```

🇬🇧 **English - Start washing machine during cheap prices:**

```yaml
automation:
  - alias: "Start washing machine at low energy price"
    trigger:
      - platform: state
        entity_id: sensor.price_level
        to:
          - "zeer_goedkoop"
          - "goedkoop"
    condition:
      - condition: time
        after: "08:00:00"
        before: "22:00:00"
    action:
      - service: notify.mobile_app
        data:
          message: "Energy price is now low! Good time to start the washing machine."
```

## Ondersteunde Bronnen / Supported Sources

Deze integratie werkt met elke sensor die:
- Een numerieke state heeft (het daggemiddelde)
- Uurprijzen als attributen heeft

Voorbeelden van compatibele integraties:
- ENTSO-e (via `raw_today` attribuut)
- Nordpool (via `today` attribuut)
- Andere energieprijzen integraties met vergelijkbare structuur

This integration works with any sensor that:
- Has a numeric state (the daily average)
- Has hourly prices as attributes

Examples of compatible integrations:
- ENTSO-e (via `raw_today` attribute)
- Nordpool (via `today` attribute)
- Other energy price integrations with similar structure

## Licentie / License

MIT License

## Ondersteuning / Support

Voor vragen, problemen of feature requests, open een issue op GitHub.

For questions, issues, or feature requests, please open an issue on GitHub.
