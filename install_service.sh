#!/bin/bash

echo -e "Install moodeAdafruitTFTBonnet Service. \n"
cd /home/pi/moodeAdafruitTFTBonnet

while true
do
    read -p "Do you wish to install moodeAdafruitTFTBonnet as a service?" yn
    case $yn in
        [Yy]* ) echo -e "Installing Service \n"
                sudo cp moodeAdafruitTFTBonnet.service /lib/systemd/system
                sudo chmod 644 /lib/systemd/system/moodeAdafruitTFTBonnet.service
                sudo systemctl daemon-reload
                sudo systemctl enable moodeAdafruitTFTBonnet.service
				echo -e "\nmoodeAdafruitTFTBonnet installed as a service.\n"
                echo -e "Please reboot the Raspberry Pi.\n"
                break;;
        [Nn]* ) echo -e "Service not installed \n"; break;;
        * ) echo "Please answer yes or no.";;
    esac
done

while true
do
    read -p "Do you wish to reboot now?" yn
    case $yn in
        [Yy]* ) echo -e "Rebooting \n"
                sudo reboot
                break;;
        [Nn]* ) echo -e "Not rebooting \n"
                break;;
        * ) echo "Please answer yes or no.";;
    esac
done

echo "moodeAdafruitTFTBonnet install complete"