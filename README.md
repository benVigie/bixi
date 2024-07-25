# Bixi

[![GitHub Release][releases-shield]][releases]
[![License][license-shield]](LICENSE)

![Project Maintenance][maintenance-shield]

This integration will monitor the bixi stations you want to keep track of, their remaining bikes and docks.

## Installation

### From HACS
1. On your HACS page, click the 3 dots on top right corner, then choose _"Personal repositories"_
2. Add `https://github.com/benVigie/bixi` as Depot and `Integration` as category
3. You should be able to see the integration listed and install it !

### Manual
1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `bixi`.
1. Download _all_ the files from the `custom_components/bixi/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for _"Bixi"_

Configuration is done in the UI

[integration_blueprint]: https://github.com/benVigie/bixi

[commits-shield]: https://img.shields.io/github/commit-activity/y/benVigie/bixi.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/benVigie/bixi.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Benjamin%20Vigié%20%40benVigie-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/benVigie/bixi.svg?style=for-the-badge
[releases]: https://github.com/benVigie/bixi/releases
