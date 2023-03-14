## Chess ##
import openai

import chess
import chess.pgn

import yaml

with open('config.yml', 'r') as file:
    config_file = yaml.safe_load(file)

openai.api_key = config_file["API_key"]

noOfFails = 0

def handleChatInput(inputMove, chatBoard):
    global noOfFails
    move = inputMove
    if len(move) > 2:
        move = move[0].capitalize() + move[1:]

    try:
        chatBoard.push_san(move)
        print("move_normal")
        noOfFails = 0
        return move
    except:
        pass

    try:
        ModMove = move[0].lower() + move[1:]
        chatBoard.push_san(ModMove)
        print("move_lower")
        noOfFails = 0
        return ModMove
    except:
        pass

    move = inputMove
    for chars in range(len(move), 0, -1):
        for i in range(len(move)):
            try:
                chatBoard.push_san(move[i:i + chars])
                print(str("move_scan: " + str(move[i:i + chars])))
                noOfFails = 0
                return move[i:i + chars]
            except:
                pass

    print("move_FAIL")

    if not chatBoard.is_checkmate() and noOfFails <= config_file["GPT_Settings"]["Max_fails"]:
        noOfFails += 1
        return handleChatInput(get_gpt_response(inputMove, chatBoard), chatBoard)
    elif noOfFails >= config_file["GPT_Settings"]["Max_fails"]:
        print(f'Max amount of failes reached ({config_file["GPT_Settings"]["Max_fails"]})')
        exit()


def get_gpt_response(illegalMove, chatBoard):
    if chatBoard.turn == chess.WHITE:
        color = "white"
    else:
        color = "black"

    if illegalMove:
        if chatBoard.is_check():
            prompt = f"Reply next chess move as {color}. You are in check. You must play one of these moves: ({str(chatBoard.legal_moves)[36:-2]}). Only say the move. {str(chess.pgn.Game.from_board(chatBoard))[93:-2]}"

        else:
            prompt = f"Reply next chess move as {color}. You must play one of these moves: ({str(chatBoard.legal_moves)[36:-2]}). Only say the move. {str(chess.pgn.Game.from_board(chatBoard))[93:-2]}"
    else:
        prompt = f"Reply next chess move as {color}. Only say the move. {str(chess.pgn.Game.from_board(chatBoard))[93:-2]}"

    print(str("\n" + prompt))

    gptMove = ""

    for i in range(5):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                max_tokens=config_file["GPT_Settings"]["Max_tokens"],
                messages=[{"role": "system", "content": prompt}]
            )
            gptMove = response.choices[0]["message"]["content"].replace("\n", "").replace(".", "").replace(" ", "")
            break
        except:
            print("openai error")

    for i in range(len(gptMove)):
        try:
            placeholder = int(gptMove[i])
        except:
            gptMove = gptMove[i:]
            break

    print(gptMove)
    return gptMove

def makeMove(board):
    move = str(handleChatInput(get_gpt_response("", board), board))
    for i in range(config_file["GPT_Settings"]["Max_fails"]):
        board.pop()
        try:
            print("move", move)
            return board.parse_san(move)
        except:
            pass
