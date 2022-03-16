# TimedTrafficLight
Raspi based Traffic light indicating the bed-time for the kids.
This project fetures a timer based, european semaphore system. e.g.

- at 19:00 - yellow only (warn): time to prepare for bed
- at 20:00 - red only (stop): bed time
- at 06:00 - red and yellow (ready): wake up time
- at 07:00 - green (go): allowed to leave the bed
- turn off any led between 23 and 4

![screenshot](doc/Screenshot1.png "screenshot")

additionally, you can fast-forward or postopone the schedule, in case tonight is 'different' with the family.

### requirements
any Raspberry Pi should work. Required are three leds, green (pin37/BCM 26), yellow (pin35/BCM 19) and green (pin 33/BCM 13).
![wire-schematic](doc/README.Wiring2.jpg "schematic") ![wire-breadboard](doc/README.Wiring1.jpg "breadboard")

### installation    
```bash
# install dependencies
sudo apt-get update
sudo apt-get install -y python3-pip git
sudo pip3 install flask yattag simplejson sortedcontainers

# clone this project
git clone https://github.com/maldex/TimedTrafficLight.git

# ensure service will be started at bootup
sudo systemctl enable --now ${PWD}/TimedTrafficLight/TimedTrafficLight.service
sudo systemctl daemon-reload
```
access the web-fontend via _http://ip:2400_


# test the LED's

```bash
sudo su - 

echo 13 > /sys/class/gpio/export
echo 19 > /sys/class/gpio/export
echo 26 > /sys/class/gpio/export

echo out > /sys/class/gpio/gpio13/direction
echo out > /sys/class/gpio/gpio19/direction
echo out > /sys/class/gpio/gpio26/direction

while [ 1 ]; do
  echo 1 > /sys/class/gpio/gpio13/value
  echo 1 > /sys/class/gpio/gpio19/value
  echo 1 > /sys/class/gpio/gpio26/value
  sleep 1
  echo 0 > /sys/class/gpio/gpio13/value
  echo 0 > /sys/class/gpio/gpio19/value
  echo 0 > /sys/class/gpio/gpio26/value
  sleep 1
done
echo 13 > /sys/class/gpio/unexport
echo 19 > /sys/class/gpio/unexport
echo 26 > /sys/class/gpio/unexport
```