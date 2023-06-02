# eWeLink

This is a node server to interface with eWeLink devices and make it available to a Universal Devices Polyglot v3 running on EISY or Polisy

Curently supports eWeLink WiFi module (Will add more modules upon request):
* SONOFF DS18B20

#### Installation

1. Backup Your ISY!
2. Go to the Polyglot Store in the UI and install.
3. From the Polyglot dashboard, select the eWeLink node server and install into an open slot.
4. Enter the username, password, app_id, and app_secret into the custom parameters
3. Restart the Admin Console to properly display the new node server nodes.

#### Configuration
1. Enter the username, password, app_id, and app_secret into the custom parameters

#### Requirements

Here is what is required to use this poly:<BR>
<b>aiohttp ~3.8.4</b>
