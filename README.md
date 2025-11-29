# Meteocat Discord Bot

A Discord bot providing real-time weather information and rain alerts for municipalities in **Catalonia**.

## Key Features

* **Current Weather:** Check the climate for any municipality (`!temps [location]`).
* **Rain Alerts:** Daily automatic alert (7:00 AM) if rain is expected.
* **Smart Search:** Automatically corrects spelling mistakes in locations (fuzzy search).

---

## Quick Installation

### 1. Prerequisites

* Python 3.8+
* Discord Bot Token
* WeatherAPI Key

### 2. Setup

1.  **Clone the repository** and install dependencies:
    ```bash
    git clone [repository-url]
    cd bot-meteorologic
    pip install -r requirements.txt
    ```
2.  **Create a `.env` file** with your credentials in the root directory:
    ```env
    DISCORD_TOKEN_METEOCAT=your_token
    WEATHERAPI_KEY=your_key
    DISCORD_CHANNEL_ID=channel_id_for_alerts
    ```

---

## Commands

| Command | Function | Example |
| :--- | :--- | :--- |
| **`!temps [location]`** | Shows the weather for the specified location. | `!temps Girona` |
| **`!pronostic`** | Link to the Meteocat mobile forecast website. | `!pronostic` |
| **`!ajuda`** | Shows the list of available commands (Help). | `!ajuda` |