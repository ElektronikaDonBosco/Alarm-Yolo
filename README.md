# Jetson Nano People detection alarm

Procedure to make inference in Jetson Nano.

Jetson-inference will be used to detect people in a house for example. Specifically, it ensures the alarm system is only activated upon detecting people, distinguishing them from pets. This reliable feature makes it an ideal choice for home security. Whenever a person is detected, Jetson-inference promptly dispatches a notification via Telegram.


## Set up Jetson Nano

Go to [this](https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-devkit#intro) step by step tutorial.

## Install dependecies and download packages

Firs of all we will have to install python dependecies. For that open a terminal an execute the following commands.

```bash
sudo apt-get update
sudo apt-get install python3-pip -y
sudo apt-get install dialog -y
sudo apt-get install v4l2loopback-dkms
sudo modprobe v4l2loopback
sudo apt-get install nano 
```

## Prepare the docker container

First of all we need to clone the repository of jetson inference and go to the folder jetson_inference.

```bash
git clone https://github.com/ElektronikaDonBosco/Alarm-Yolo.git

```

Clone jetson-inference repository

```bash
git clone https://github.com/dusty-nv/jetson-inference.git

```

Change the file jetson-inference/docker/tag.sh line 25 CONTAINER_IMAGE="jetson-inference:r32.5.0" to:

```bash
#line 25 CONTAINER_IMAGE="jetson-inference:r32.5.0" to:
CONTAINER_IMAGE="ElektronikaDonBosco/jetson-inference:donbosco"
```

Each time to run the container follow the next steps:

```bash
cd jetson-inference
docker/run.sh --volume path_to/Alarm-Yolo:/Alarm-Yolo
```

## Telegram bot creation

* Search for @botfather in Telegram.

![](assets/20230412_120813_Screenshot-2022-12-16-092357.png)

* Start a conversation with BotFather by clicking on the Start button.

![](assets/20230412_121259_image.png)

* Type `/newbot`, and follow the prompts to set up a new bot. The BotFather will give you a token that you will use to authenticate bot and grant it access to the Telegram API.

![](assets/20230412_121528_image.png)

## Before running the inference

In the file Alarm-Yolo/main.py we need to change the line 17 with our token.

![](assets/20230412_121807_image.png)

Once having done all the steps, run this in the docker terminal.

```bash
python3 -m pip install pyTelegramBotAPI==3.8.3
```

## Run the inference

Once everything is set and installed we can run the inference. This are the steps in our case:

1 - Make sure you have your own Telegram API key at main.py (see instructions above)

2 - Run docker
```bash
cd jetson-inference
docker/run.sh --volume home/donbosco/Alarm-Yolo:/Alarm-Yolo
```
It will ask for the password you created in the Operating System: "donbosco" in our case

3 - Run the python code
```bash
cd /Alarm-Yolo/
python3 main.py
```

4 - The code will wait until you activate the inference at Telegram. Go to Telegram bot you created and write:
```bash
/start
```
After you can turn on and turn off the alarm from the Telegram:
```bash
/turn_on
/turn_off
```


5 - When a person is detected you will receive a message in the chat
