# Moode TFT Adafruit 1.3" Color TFT Bonnet for Raspberry Pi

-------------------------------------------------------


Based on TFT-MoodeCoverArt (https://github.com/rusconi/TFT-MoodeCoverArt).

Works with Adafruit 1.3" Color TFT Bonnet with 240*240 TFT (ST7789), buttons and a joystick.

### Features.

The script will display cover art (where available) for the moode library or radio stations.

* For the moode library, embedded art will be displayed first, then folder or cover images if there is no embedded art.
* For radio stations, the moode images are used.
* If no artwork is found a default image is displayed.

Metadata displayed:
* Artist
* Album/Radio Station
* Title

Basic controls:
* Play/Pause
* Volume up/down
* Next/Previous Song
* Load and Play "default" playlist (config.yml) 

The script has a built in test to see if the mpd service is running. This should allow enough delay when 
used as a service. If a running mpd service is not found after around 30 seconds the script displays the following and stops.

```
   MPD not Active!
Ensure MPD is running
 Then restart script
```

**Limitations**

Metadata will only be displayed for Radio Stations and the Library.

For the `Airplay`, `Spotify` and `Bluetooth` renderers, different backgrounds will display.

The overlay colours adjust for light and dark artwork, but can be hard to read with some artwork.

The script does not search online for artwork

### Assumptions.

**You can SSH into your RPI, enter commands at the shell prompt, and use the nano editor.**

**Your moode installation works and produces audio**

### Preparation.

**Enable SPI pn your RPI**

see [**Configuring SPI**](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-spi)

Install these pre-requisites:
```
sudo apt-get update
sudo apt-get install python3-rpi.gpio python3-spidev python3-pip python3-pil python3-numpy
sudo pip3 install pyyaml
```
Install the TFT driver.

```
sudo pip3 install adafruit-circuitpython-rgb-display
```

***Ensure 'Metadata file' is turned on in Moode System Configuration***

### Install the TFT-MoodeCoverArt script

```
cd /home/pi
git clone https://github.com/ror77gh/moodeAdafruitTFTBonnet.git
```

### Config File

The config.yml file can be edited to:

* display background (cover / color)
* position and color (volumebar / progressbar / ...)
* display the text with a shadow
* default Playlist

All colors 

### Button

* Joystick Up: Increase volume
* Joystick Down: Decrease volume
* Joystick Left: Skip back to last song of Playlist
* Joystick Right: Skip to next song
* Button A: Toggle Play/Pause
* Button B: Clear current playlist and load and play default playlist (defines in config.yaml)
* Button A and Button B at the same time: Show system information

The comments in 'config.yml' should be self explanatory


**Make the shell scripts executable:**

```
chmod 777 *.sh
```

Test the script:

```
python3 /home/pi/moodeAdafruitTFTBonnet/moodeAdafruitTFTBonnet.py


Ctrl-c to quit
```

**If the script works, you may want to start the display at boot:**

### Install as a service.

```
cd /home/pi/moodeAdafruitTFTBonnet
./install_service.sh
```

Follow the prompts.

If you wish to remove the script as a service:

```
cd /home/pi/moodeAdafruitTFTBonnet
./remove_service.sh
```

