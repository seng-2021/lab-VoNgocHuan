"""
This file compiles modules and defines functions that run the Minesweeper.
state = stores important game-related values for global access.
player_stats = stored important player-related info.
game_choices, scoreboard_choices = choices for user input and for 
scoreboard browsing.
buttons = assigns mouse clicks.

Made by: Huan
some ideas were borrowed from my friend, Hieu, and chatgpt.
"""

import sys
import math
import random
import datetime as dt
import csv
import os
import sweeperlib as sw

game_choices = ["n", "s", "q"]
scoreboard_choices = ["1", "2", "m"]

buttons = {
    sw.MOUSE_LEFT: "left",
    sw.MOUSE_MIDDLE: "middle",
    sw.MOUSE_RIGHT: "right"
}

state = {
    "true_field": [],
    "player_field": [],
    "available_tiles": [],
    "first_click": False,
    "winning": False,
    "mines_count": 0,
    "remaining": 0,
    "mines": 0,
}

player_stats = {
    "time": 0,
    "move": 0,
    "date": "",
    "player_name": ""
}


def place_mines(true_field, avail_tile, no_mines):
    """
    Places N mines to a field in random tiles.
    """
    for _ in range(no_mines):
        (col, row) = random.choice(avail_tile)
        true_field[row][col] = "x"
        avail_tile.remove((col, row))
    return true_field

def show_score():
    """
    Prints the result of game, date and time, time taken
    and number of moves
    """
    os.system('cls')
    if state["winning"]:
        print("You win!")
    else:
        print("You lose!")
    player_stats["date"] = player_stats["date"].strftime('%d.%m.%Y %H:%M:%S')
    date, time, move, count = player_stats['date'], player_stats['time'], player_stats['move'], state['mines_count']
    print(f"Date: {date}, Time Elapsed: {time} seconds, Moves: {move}, Unflagged mines: {count}")
    add_score("C:\\Users\\Admin\\Downloads\\school_work\\minesweeper_course_project\\scoreboard.csv")

def count_mines(_x, _y, field):
    """
    Counts the number of mines around a tile
    """
    row = len(field)
    column = len(field[0])
    counter = 0
    for j in range(row):
        for i in range(column):
            if i in (_x-1, _x, _x+1) and j in (_y-1, _y, _y+1) and field[j][i] == "x":
                counter += 1
    return counter

def floodfill(player_field, true_field, start_x, start_y):
    """
    Marks previously unknown connected areas as safe, starting from the given
    x, y coordinates.
    """
    player_stats["move"] += 1
    if true_field[start_y][start_x] == "x":
        sw.close()
        player_stats["date"] = dt.datetime.now()
        show_score()
        return
    
    state["remaining"] -= 1
    safe = [(start_x, start_y)]
    moves = [(-1, 0), (0, -1), (1, 0), (0, 1)]
    safe_values = ["0", "1", "2", "3", "4", "5", "6", "7", "8"]
    
    while safe:
        col, row = safe.pop(-1)
        true_field[row][col] = str(count_mines(col, row, true_field))
        player_field[row][col] = true_field[row][col]
        for move in moves:
            offset_rows = move[1]+row
            offset_cols = move[0]+col
            if 0 <= offset_cols < len(true_field[0]) and 0 <= offset_rows < len(true_field):
                if true_field[offset_rows][offset_cols] in safe_values:
                    pass
                elif true_field[offset_rows][offset_cols] != "x":
                    true_field[offset_rows][offset_cols]=str(count_mines(offset_cols,offset_rows,true_field))
                    player_field[offset_rows][offset_cols] = true_field[offset_rows][offset_cols]
                    safe.append((offset_cols, offset_rows))
                    state["remaining"] -= 1

    if state["remaining"] == state["mines"]:
        state["winning"] = True
        sw.close()
        player_stats["date"] = dt.datetime.now()
        show_score()
        return

def first_click_handler(col, row):
    """
    Prevents the player from landing on a mine on the first click.
    Also the function starts the timer function upon the player's first click.
    """
    while not state["first_click"]:
        sw.set_interval_handler(timer, 1)
        state["available_tiles"].remove((col, row))
        state["true_field"] = place_mines(state["true_field"], state["available_tiles"], state["mines"])
        floodfill(state["player_field"], state["true_field"], col, row)
        state["first_click"] = True

def click_handle(_x, _y, button, modifiers):
    """
    This function is called when a mouse button is clicked inside the game window.
    Prints the position and clicked button of the mouse to the terminal.
    """

    col = _x // 40
    row = _y // 40

    if buttons[button] == "right":
        if state["player_field"][row][col] == " ":
            state["player_field"][row][col] = "f"
            state["mines_count"] -= 1
        elif state["player_field"][row][col] == "f":
            state["player_field"][row][col] = " "
            state["mines_count"] += 1
    else:
        if state["player_field"][row][col] == " ":
            first_click_handler(col, row)
            floodfill(state["player_field"], state["true_field"], col, row)

def draw_field():
    """
    A handler function that draws a field represented by a two-dimensional list
    into a game window. This function is called whenever the game engine requests
    a screen update.
    """
    field_to_draw = state["player_field"]
    sw.clear_window()
    sw.draw_background()
    sw.begin_sprite_draw()
    for row_num, row_content in enumerate(field_to_draw):
        for column_num, cell_content in enumerate(row_content):
            key = cell_content
            sw.prepare_sprite(key, column_num*40, row_num*40)
    sw.draw_sprites()

def field_data():
    """
    A function that collects player name, field dimensions and number of mines.
    The function then assigns the inputs into state.
    """
    while True:
        player_name = str(input("Give player name (max 10 characters): "))
        if len(player_name) > 10:
            print("Name must be under 10 characters")
        elif len(player_name) == 0:
            print("Name must have at least 1 character")
        else:
            break

    while True:
        try:
            width = int(input("Give width (between 5-30): "))
        except ValueError:
            print("Invalid input")
            continue
        if width < 5 or width > 30:
            print("Invalid size")
        else:
            break

    while True:
        try:
            height = int(input("Give height (between 5-20): "))
        except ValueError:
            print("Invalid input")
            continue
        if height < 5 or height > 20:
            print("Invalid size")
        else:
            break

    while True:
        try:
            mines = int(input("Give number of mines (10 or more): "))
        except ValueError:
            print("Invalid input")
            continue
        if mines < 10 or mines > width * height - 1:
            print(("Too many or too few mines"))
        else:
            break

    true_field = []
    player_field = []
    for _ in range(height):
        true_field.append([])
        player_field.append([])
        for _ in range(width):
            true_field[-1].append(" ")
            player_field[-1].append(" ")

    available = []
    for _y in range(height):
        for _x in range(width):
            available.append((_x, _y))

    state["true_field"] = true_field
    state["player_field"] = player_field
    state["mines"] = mines
    state["available_tiles"] = available
    state["remaining"] = width * height
    state["mines_count"] = mines
    player_stats["player_name"] = player_name

def timer(elapsed):
    """
    A function that counts the length of a game in seconds
    and assigns the value to state at the end.
    """
    os.system('cls')
    elapsed = player_stats["time"]
    print(f"Time elapsed: {elapsed}")
    player_stats["time"] += 1

def new_game():
    """
    Clears previous data and presents a new game window
    """
    state["winning"] = False
    state["first_click"] = False
    player_stats["time"] = 0
    player_stats["move"] = 0
    player_stats["date"] = 0
    field_data()
    sw.load_sprites("C:\\Users\\Admin\\Downloads\\school_work\\minesweeper_course_project\\sprites")
    sw.create_window(len(state["true_field"][0])*40, len(state["true_field"])*40)
    sw.set_draw_handler(draw_field)
    sw.set_mouse_handler(click_handle)
    sw.start()

def entry_list(file):
    """
    A function that finds the number of rows in current scoreboard entries.
    """
    with open(file, 'r', encoding="utf-8") as data:
        no_rows = 0
        for _ in data:
            no_rows += 1
        return no_rows
    
def prompt_choice(choices):
    """
    Function to input the next action you want to do:
    n: new game
    s: show scoreboard
    q: quit the game 
    """
    print(f"Select one choice: {', '.join(choices)}")
    while True:
        choice = input("Input next choice: ").lower()
        if choice in choices:
            return choice
        print("Invalid input!")

def add_score(file):
    """
    Function that pulls current state values into end_values and then makes
    a new entry to scoreboard.csv as a new row.
    """
    with open(file, 'a', newline='', encoding="utf-8") as data:
        new_entry = entry_list(file) + 1
        end_values = [new_entry, player_stats["player_name"], player_stats["date"]]
        end_values.extend([player_stats["time"],player_stats["move"],state["winning"],state["mines_count"]])
        for i in end_values:
            str(i)
        new_score = csv.writer(data)
        new_score.writerow(end_values)

def show_page(file, page):
    """
    The function reads the scoreboard.csv file and splits the list into pages
    the function also prints the results in a more presentable form.
    """
    os.system('cls')
    first = (page - 1) * 10
    last = page * 10

    with open(file, encoding="utf-8") as data:
        content = data.readlines()
        for elem in range(first, last):
            if elem < entry_list(file):
                line = "".join(content[elem])
                if line.strip() != "":
                    game_no, pl_name, date, time, moves, outcome, left = line.strip().split(",")
                    for value in line:
                        value = value.strip()
                    minute, second = divmod(int(time), 60)
                    time = f'{minute:02}:{second:02}'
                    if outcome == "True":
                        outcome = "WON!"
                    else:
                        outcome = "LOST!"
                    print(f"{game_no}. {pl_name} {outcome}")
                    print(f"Date: {date}, Time: {time}, Moves: {moves}, Unflagged mines: {left}")
                    print()

def scoreboard(file):
    """
    The function allows the user to browse between different pages of the scoreboard
    """
    os.system('cls')
    pages = math.ceil(entry_list(file) / 10)
    current_page = 1
    show_page(file, current_page)

    print(f"Pages: {pages}, current page: {current_page}")
    print()
    print("Previous page(1)")
    print("Next page(2)")
    print("Back to main menu(m)")
    print()
    while True:
        choice = prompt_choice(scoreboard_choices)
        if choice == "1":
            if current_page > 1:
                current_page -= 1
                os.system('cls')
                show_page(file, current_page)
                print(f"Pages: {pages}, current page: {current_page}")
                print()
                print("Previous page(1)")
                print("Next page(2)")
                print("Back to main menu(m)")
                print()
            else:
                print("This is the first page!")
        if choice == "2":
            if current_page < pages:
                current_page += 1
                os.system('cls')
                show_page(file, current_page)
                print(f"Pages: {pages}, current page: {current_page}")
                print()
                print("Previous page(1)")
                print("Next page(2)")
                print("Back to main menu(m)")
                print()
            else:
                print("This is the last page!")
        if choice == "m":
            os.system('cls')
            main()

def main():
    """
    This function provides the starting Main menu interface
    """
    os.system('cls')
    print("New Game(n)")
    print("Scoreboard(s)")
    print("Quit(q)")
    print()
    while True:
        choice = prompt_choice(game_choices)
        if choice == "q":
            os.system('cls')
            sys.exit()
        if choice == "s":
            scoreboard("C:\\Users\\Admin\\Downloads\\school_work\\minesweeper_course_project\\scoreboard.csv")
        if choice == "n":
            new_game()


if __name__ == "__main__":
    main()
