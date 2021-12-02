# Media Lexicometer

This repository contains a Python Django application and some scripts to:
- capture the audio streams from DVB-T channels thanks to DVB-T adapters,
- perform live speech to text on the channel audio streams,
- record the recognized words to a database,
- allow an user to query the database from a Web page and generate graphs as results.

## Setup

### Install the dependancies

```
sudo apt install ffmpeg w-scan dvb-tools virtualenv tmux
```

### Create the channel file

To scan the channels available in your location:
```
w_scan -f t -c FR -X > channels.conf
```

To convert the `channels.conf` file to the v5 format:
```
dvb-format-convert -I ZAP -O DVBV5 -s dvb-t channels.conf channels_v5.conf
```

### Create and setup your Python virtual environment

```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Get the models

Download the spacy model from [here](https://github.com/explosion/spacy-models/releases/tag/fr_core_news_sm-3.1.0)
and decompress it in the main application folder.

Download the Vosk model from [here](https://alphacephei.com/nsh/2020/10/21/french.html) and decompress the content
of the `vosk-model-fr-0.6-linto` directory in the archive in a `model` directory in the main application folder.


### Add the channels to the database

```
cd mediaAnalysis
python3 manage.py syncdb
python3 manage.py createsuperuser
python3 manage.py runserver
```

Go to the Django administration interface and log in with the admin credentials you've just created.
Then, create your channel records.

### Create your channel scripts

Look at the example scripts in the `script` directory to create your own channel capture and analysis scripts.
The example scripts use two tmux sessions per multiplex to start `dvbv5-zap` and the `liveSpeechToText.py` script.
You are of course free to use a more appropriate way to run them in the background.

## Usage

Per multiplex, you must run a `dvbv5-zap` instance and a `liveSpeechToText.py` instance (see previous section).
To run the query Web interface, use:
```
python3 manage.py runserver
```
Then, go to http://localhost:8000.
