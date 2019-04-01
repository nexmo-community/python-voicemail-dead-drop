# Record A Message With Python

This repository contains a sample Python project, "Oleg's Pizzeria" which demonstrates how to create a Voicemail application in Python & Flask, with a spy theme. It was written to accompany the blog post
"Build a Voicemail Dead-Drop With Python & Flask".

## What Does It Do?

This service responds to incoming calls by reading out a greeting and recording an audio message, which
is then copied into a local `recordings` folder. It also contains a view that will list all recordings
that have been stored.

## Running This Code

You'll need Python 3.6+ to run this.
We recommend you create a virtualenv, and then install the dependencies by running:

```bash
python3 -m pip install -r requirements.txt
```

Once you've done that, copy `env.template` to `.env` and change the contents to match your
configuration (you should only need to provide Nexmo credentials).

You'll need to store your Nexmo Voice application key file in the path specified in `.env` -
by default this is `private.key` in your working directory.

Once you've done that you can run `make run` if you have Make installed,
otherwise run:

```bash
FLASK_ENV=development FLASK_APP=answerphone flask run
```

You must configure your Nexmo Voice application to point to `https://your-server:port/answer` and `https://your-server:port/event` - call a number associated with your Nexmo Voice application and you're done!
