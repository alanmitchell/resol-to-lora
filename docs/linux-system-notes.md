# Notes about Configuration of Linux System to run Script

* Tested on a [Libre Le Potato board](https://libre.computer/products/aml-s905x-cc/) running 
[Armbian 23.02.2 Jammy with Linux 6.1.11-meson64](https://www.armbian.com/lepotato/).

* The [resol-vbus GitHub project](https://github.com/danielwippermann/resol-vbus/tree/master) must be installed in order to
run the [JSON live data server](https://github.com/danielwippermann/resol-vbus/tree/master/examples/json-live-data-server).

* Both this project (resol-to-lora) and the JSON live data server are configured to run
as services through use of systemd.  See the systemd unit files in this repo in the 
`system-files` directory.

* Status information is automatically copied to a file on a USB flash drive
when a USB flash drive is inserted.  See the [status](../status) script in this repo.
Also, see the notes on configuring auto-mounting a USB flash drive in 
this `docs` directory: [automount-usb.md](automount-usb.md).

* The system is configured to reboot nightly through use of the root's
crontab (sudo crontab -e).

* A Resol [VBus/USB Interface Adapter](https://www.resol.de/en/produktdetail/13) is used to interface to the Resol controller.

* A [SEEED Studio LoRa WIO-E5 mini board](https://www.seeedstudio.com/LoRa-E5-mini-STM32WLE5JC-p-4869.html) is used to transmit data via LoRaWAN.  These are available through Digi-Key.
