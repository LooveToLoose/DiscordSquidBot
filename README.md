# Squidbot
This is the repository for the Squidbot used in the [Will You Snail?](https://store.steampowered.com/app/1115050/Will_You_Snail/) [discord server.](https://discord.gg/WkvqV3mxdQ)

## Development/Hosting
To host your own version of Squidbot, whether for your own server or to help improve Squidbot, you'll need to do a few things.

#### Prerequisites
Before you start, you'll need to have some things installed:
1. Python 3.9 or later. (https://www.python.org/downloads/) (It is hosted with python 3.9)
2. If you want to contribute, you'll need Git. (https://git-scm.com/downloads)
3. An code editor. Visual Studio Code is recommended, Notepad is not, but whatever you usually use should work fine.
4. **FFmpeg** – required for voice/audio playback:  
   - **Windows:** [Download FFmpeg](https://ffmpeg.org/download.html) and add the `bin` folder to your system PATH.  
   - **macOS:** `brew install ffmpeg`  
   - **Linux (Debian/Ubuntu):** `sudo apt install ffmpeg`


#### 1. Get the code
If you have git installed, you can clone this repo by running `git clone git@github.com:LooveToLoose/DiscordSquidBot.git`

If you do not have git installed, you can get the code by clicking the Code dropdown at the top of this page and selecting "Download ZIP"

Once you've done that, open a terminal and editor into the folder where you have the code for the next few steps.

#### 2. Copy `.env.example` to `.env`
The .env file is used to keep the bot token and the database connection URI. Neither of these should be public, so an example file is included that doesn't contain any of these. You should never put your tokens in the .env.example, nor should you ever commit your .env file, as that may let someone take control of your bot or database.

To get started, copy the .env.example file to .env to start editing it.

#### 3. Get your Discord Bot Token
You can follow the first step only of [these instructions](https://discord.com/developers/docs/quick-start/getting-started) to create your bot and get it's token. When creating the bot, give it all intents, and when adding it to your server it's easiest to give it Administrator perms, unless you know exactly what it needs.

Once you have your discord bot token, put it inside the double quotes for TOKEN in your .env file, e.x. `TOKEN="YOUR_BOT_TOKEN_GOES_HERE"`

#### 4. Sign up for mongodb atlas free plan
Please note, if you already have another MongoDB database you can use, you don't need this step, just get the connection URI from it and put it in your .env file.

Otherwise, you can sign up for a free MongoDB database by going [to this website](https://www.mongodb.com/cloud/atlas/register), signing up for an account, and getting your connection string.

Once you have your connection string, put it in your .env file for `MONGO_DB_URI`.

#### 5. Get your "Ai Overlords" role ID.
In your server, you'll need to get the ID of the role for your Ai Overlords. Once you have it, put it in the .env file as `AIRole`

#### 6. Install Dependencies
These next few parts will all be done in your terminal. Make sure you're in the folder with the bot's code in it for them.

Create Virtual Environment

This is done to make sure none of the dependencies mess with anything else on your system.
To create the virtual environment, run `python -m venv ./venv`.
This will create a new folder, `venv`, that contains your virtual environment.

Next, you need to activate the virtual environment. You'll need to do this every time you enter the shell to start the bot, so it always uses the right dependencies.
To do this, run `./venv/Scripts/activate`. Once it finishes, you should see your prompt change to include `(venv)` at the start of it.

Once you are in the virtual environment the first time, you'll need to install the requirements. To do this, just run `pip install -r requirements.txt`. Again, you'll only need to do this the first time when setting everything up, not every time you want to start the bot, unlike activating the virtual environment.

Once you've done all that, you're ready to start the bot!

To start the bot, just run `python main.py`, and you should be on your way! Do keep in mind, with the free MongoDB database, it can take a while to start and may be very slow sometimes when running commands, but that's not an issue. If you have an ssl handshake failed issue with mongodb, make sure you've allowed your ip to access the database in mongo's security options.


## Contributing

If you've made any changes to your Squidbot and think they would be good to include in the base Squidbot, feel free to make a pull request!
If you want to help make Squidbot better but don't know what to add, look at the issues to see what people want!
And if you have any suggestions but don't have the time or knowledge to code them, or have seen a bug and would like to report it, please make an issue so it can be fixed! 

## Credits

Many thanks to txshiro, the original developer of this Squidbot.
