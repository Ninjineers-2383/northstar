# Northstar

Northstar is a package by FRC 6328, Mechanical Advantage, that they are unable to support. Ninjineers, FRC 2383, have decided to create their own fork to be used by teams that want a lightweight distributed april tag detection system.

The documentation is currently nonexistent but @henrylec on discord would love to help out in our server https://discord.gg/VQ8EJDWKaS

## Setup

In order to setup northstar you need to create the two configuration files described below in their own directory

```sh
mkdir config
```

Then in the new config folder add the following json as `config.json` ensuring you change TEAM to your team number

```json
{
  "camera": "/dev/video0",
  "device_id": "northstar",
  "server_ip": "10.TE.AM.2",
  "stream_port": 8000
}
```

To calibrate your camera we prefer to use https://calibdb.net . You can plug in your camera and then download the calibration in opencv format and save it as `calibration.json` in the config folder

## Docker

We use docker in order to not need to compile opencv with gstreamer on every raspberry pi we want to use. In order to run a prebuilt version of northstar on your raspberry pi run the following command

```sh
docker run --privileged -v ./config:/config -v /dev/video0:/dev/video0 -p 8000:8000 ghcr.io/ninjineers-2383/northstar:1.0.0-rpi
```
