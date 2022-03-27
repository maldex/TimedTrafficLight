# Using your Rapsi as network camera

## using [v4l2rtspserver](https://github.com/mpromonet/v4l2rtspserver.git)
```bash
# install build utils
sudo apt-get install -y git cmake liblog4cpp5-dev libv4l-dev libasound2-dev libalsaplayer-dev libclalsadrv-dev libdssialsacompat-dev

# clone 
git clone https://github.com/mpromonet/v4l2rtspserver.git

# compile
pushd v4l2rtspserver/
cmake .
make
sudo make install
popd
```
vi /etc/rc.local
```bash
...
# start v4l2rtspserver
amixer -c 1 sset Mic 100%
v4l2-ctl --set-ctrl rotate=90 --set-ctrl vertical_flip=0 --set-ctrl horizontal_flip=0 --set-ctrl color_effects=0
su - pi -c 'v4l2rtspserver -W 1280 -H 720 -t 3 /dev/video0,hw:1,0 -C 1 -a S16_LE' &
```
---
## using [UV4l](https://www.linux-projects.org/uv4l/) 
[like here](https://pramod-atre.medium.com/live-streaming-video-audio-on-raspberry-pi-using-usb-camera-and-microphone-d19ece13eff0)
```

```
## using [Motion](motion-project.github.io) (todo)
```bash
sudo apt-get install motion -y
v4l2-ctl -V
sudo sed -i 's/\(daemon\).*/\1 on/g' /etc/motion/motion.conf
sudo sed -i 's/\(stream_localhost\).*/\1 off/g' /etc/motion/motion.conf
sudo sed -i 's/\(width\).*/\1 1024/g' /etc/motion/motion.conf
sudo sed -i 's/\(height\).*/\1 768/g' /etc/motion/motion.conf
sudo sed -i 's/\(framerate\).*/\1 30/g' /etc/motion/motion.conf
sudo sed -i 's/\(text_left \).*/\1 cam-'$(hostname -s)'/g' /etc/motion/motion.conf

sudo mkdir /var/log/motion
sudo chown motion:motion /var/log/motion
```

## using VLC (todo)
```bash

vlc v4l2:///dev/video0:width=1024:height=768:chroma=mjpg:fps=30 --sout "#std{access=http,mux=mpjpeg,dst=:8088}"


        d=$1; cd /dev
        d_num=${d:5}
        port=$((8899 - ${d_num}))
        marq_string="`hostname -s`:${d} - %d.%m.%Y %H:%M:%S"
        dst_http="http{dst=:${port}/}"
        dst_rtp="rtp{port=${port},sdp=rtsp://:${port}/stream.sdp}"

        url="v4l2://${d}:width=${hres}:height=${vres}:chroma=mjpg:fps=${fps}:input-slave=alsa://hw:${d_num},0"
        so="${tc}:duplicate{dst=${dst_http}:dst=${dst_rtp}}"

----

vlc "v4l2://video0:width=1024:height=768:chroma=mjpg:fps=30:input-slave=alsa://hw:1,0"
vlc v4l2:///dev/video0:width=1024:height=768:chroma=mjpg:fps=30 --sout "#std{access=http,mux=mpjpeg,dst=:8088}"

```

---

## analyze video and audio capabilities (notes)
```bash
v4l2-ctl --list-devices
v4l2-ctl -d /dev/video0 --list-formats-ext

#### 

grep "Format:" /proc/asound/card*/stream*
for each in $(ls /proc/asound/card*/stream*); do 
    echo $each
    device=$(echo $each| tr -cd '[[:punct:][:digit:]]' | awk -F/ '{print "HW:"$(NF-1)","$NF}')
    channels=$(grep -Po 'Channels:\s\K.*' ${each})
    format=$(grep -Po 'Format:\s\K.*' ${each})
    
    echo $device  - $channels - $format
done
```
