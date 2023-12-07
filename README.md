# ChatBot
## Code for my ChatGPT powered bot on Lichess. Play against it [here](https://lichess.org/@/chat_bot/)

A Lichess bot powered by ChatGPT, using my [ChatChess Python package](https://github.com/Tmate6/ChatChess).

### This bot uses [BotLi](https://github.com/Torom/BotLi) to connect to Lichess. Some files need to be changed to use ChatGPT. Please don't sue me.

## Installation 

1. Download or clone BotLi and ChatBot
```
git clone https://github.com/Torom/BotLi.git && git clone https://github.com/Tmate6/Lichess_ChatGPT_ChatBot.git
```
2. Move all files from `Lichess_ChatGPT_ChatBot` to `BotLi` folder (replacing the existing files)
3. Install requirements
```
python -m pip install -r requirements.txt
```
4. Insert Lichess API token and OpenAI API key into `config.yml.default`, then save the file as `config.yml`

The settings can be found in the `config.yml` file. It includes both the settings of [ChatChess](https://github.com/Tmate6/ChatChess) and [BotLi](https://github.com/Torom/BotLi).
