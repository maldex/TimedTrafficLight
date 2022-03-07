# TimedTrafficLight
Raspi based Traffic light indicating the bed-time for the kids.

### installation
```bash
# install dependencies
sudo apt-get update
sudo apt-get install -y python3-pip git
sudo pip3 install flask yattag simplejson sortedcontainers

# clone this project
git clone https://github.com/maldex/TimedTrafficLight.git

# ensure service will be started at bootup
sudo  systemctl enable --now ${PWD}/TimedTrafficLight/TimedTrafficLight.service
sudo systemctl daemon-reload
```
access the web-fontend via _http://<ip>:2400_