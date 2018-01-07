# Puppet Bot

PuppetBot is a cloud powered chatter robot (chatbot) written in python. It is a robot which can have conversations with the end users. PuppetBot has a camera and is capable of staring conversation when it detects a human face in front of it. It is an actual robot which can make voice appropriate lip movements. PuppetBot uses AWS Lex as its chatbot engine. AWS Rekognition for face detection. AWS Polly for converting conversations into visemes, which are used as an input to control lip movements. [Here](https://www.youtube.com/watch?v=JvpXXcilbNg) is a video of the PuppetBot in action.   

<!---
Thanks to 
-->

[![PuppetBot](https://img.youtube.com/vi/JvpXXcilbNg/0.jpg)](https://www.youtube.com/watch?v=JvpXXcilbNg)

## Getting Started:

### Basic Voice Based Chatbot:

Voice based chatbot is a stripped down version of PuppetBot. This setup just needs a Raspberry Pi, USB microphone and speaker. Before starting the chatbot we need to configure the Raspberry Pi and build a cloud backend. Instructions to configure the Raspberry Pi are [here](./docs/parts/install_software.md) and to build a cloud backend are [here](./docs/parts/configure_chatbot.md) and [here](./docs/parts/configure_cognito.md).


```
cd PuppetBot
sudo python bot.py audiobot start
```

### PuppetBot:

Before starting the PuppetBot follow the instructions from [hardware](), [configure raspberry pi]() and [cloud backend]() pages. 
 
```
cd PuppetBot
sudo python bot.py puppetbot start 
```
