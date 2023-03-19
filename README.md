# ChatBot
A Lichess bot powered by ChatGPT

### This version is not stable. Use https://github.com/Tmate6/Lichess_ChatGPT_ChatBot/tree/5ca0e3b9f7d265bc57705d1c71c69e4668cb0d95.

### This bot uses BotLi (https://github.com/Torom/BotLi) to connect to Lichess. Some files need to be changed to use ChatGPT. Please dont sue me.

## Installation 

1. Download or clone BotLi and ChatBot
```
git clone https://github.com/Torom/BotLi.git && git clone https://github.com/Tmate6/Lichess_ChatGPT_ChatBot.git
```
2. Move all files from `Lichess_ChatGPT_ChatBot` to `BotLi` folder
3. Install requirements
```
python -m pip install -r requirements.txt
```
4. Insert Lichess API token into `config.yml` and OpenAI api key into `lichess_game.py` replacing `INSERT_API_KEY` (fix soon)

The rest of the settings can be found in the `config.yml` file. For the documentation of BotLi, go to https://github.com/Torom/BotLi.
