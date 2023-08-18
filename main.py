import random
import spacy
import gensim
from gensim.models import Word2Vec
from human_vs_ai import *
from ai_vs_ai import game_for_ai_ai

nlp = spacy.load('en_core_web_lg')

def clean_codenames_dataset(words):
    codenames_cleaned_word_list = []
    for word in words:
        formatted_word = word.split(", ")
        codenames_cleaned_word_list.append(formatted_word[0].replace("\n", ""))
    return codenames_cleaned_word_list

def get_codenames_words():
    with open("words_list\codenames_word_list.txt", "r") as words_list:
        words = words_list.readlines()
        codenames_word_list = clean_codenames_dataset(words)
        return codenames_word_list

def display_statements():
    print("===================")
    print("Welcome to the Codenames Game!!")
    print("Here are some basic rules of the game:")
    print("**************")
    print("1) There are 2 teams: Red and Blue")
    print("2) Each team has 1 spymaster and agents")
    print("3) There are 25 words out of which 8 words belong to red team, 8 to blue team, 8 white words and 1 black word ")
    print("4) Only the spymaster can know which words belong to their team, the agents cannot see their team's words")
    print("5) The spymaster should give one word hints along with a number so that the agents can guess that many number of words based on the hint")
    print("6) The team to find out their words the fastest, wins the game")
    print("7) White word cards are neutral cards, which means they don't belong to any team")
    print("8) Black word card is the assasin card, which means any team that guesses this word immediately looses.\n")
    print("**************\n")
    print("Now lets begin the game!!!")

def dataset_creation():
    display_statements()
    list_of_words = get_codenames_words()  
    return list_of_words 

def select_25_words(word_dataset):
    number_of_words = 25
    return random.sample(word_dataset,number_of_words)

def arranged_board(words):
    board = []
    for col in range(5):
        row_list = []
        for row in range(5):
            row_list.append(words[5*col+row])
        board.append(row_list)
    return board



def set_colors_in_keycard():
    default_colors = ['RED','BLUE','BLACK','WHITE']
    keycard_colors = []
    color_count_dict = {'RED':0,'BLUE':0,'BLACK':0,'WHITE':0}
    color_limit_dict = {'RED':8,'BLUE':8,'BLACK':1,'WHITE':8}
    while len(keycard_colors) < 25:
       if len(color_count_dict) == 0:
           break
       chosen_color = random.choice(default_colors)
       if chosen_color in color_count_dict:
           color_count_dict[chosen_color] += 1
           if color_count_dict[chosen_color] > color_limit_dict[chosen_color]:
               del color_count_dict[chosen_color]
           else:
               keycard_colors.append(chosen_color)
    color_count_check = {'RED':0,'BLUE':0,'BLACK':0,'WHITE':0}
    for color in keycard_colors:
        color_count_check[color] += 1
    
    return keycard_colors

def associate_word_color(words,colors):
    dict_store = {"RED":[], "BLUE":[], "WHITE":[], "BLACK":[]}
    for row in range(5):
        for column in range(5):
            dict_store[colors[row][column]].append(words[row][column])
    return dict_store


def get_hint(team_going_first):
    while True:
        hint = input(f"\n{team_going_first} team spymaster, enter a hint: ")
        if not hint.isalpha() or len(hint) == 0:
            print("Incorrect Input, Please enter Valid input.")
            continue
        else:
            break
    return hint

def get_number_of_words(team_going_first,dict_with_word_color):
    while True:
        number_of_words = input(f"{team_going_first} team spymaster, enter a number of words: ")
        if not number_of_words.isnumeric() or len(number_of_words) == 0 or int(number_of_words) == 0:
            print("Incorrect Input, Please enter Valid input")
            continue
        else:
            if int(number_of_words) > 4:
                print("Maximum number of words that can be given is 4. Please enter input again")
                continue
            elif int(number_of_words) > len(dict_with_word_color[team_going_first]):
                print("Spymaster should give number of words lesser than the number of available words for the team")
                continue
            break
    return number_of_words


def check_word_present_in_board(dict_with_word_color,team_guess_word):
    for color in dict_with_word_color:
        for words in dict_with_word_color[color]:
            if team_guess_word == words:
                return True
    return False

def team_status_display(current,team_going_first,opposing_team,dict_store_team_words):
    if current == 1:
        print(f"{team_going_first} guessed words are: {dict_store_team_words[team_going_first]}")
        print(f"{opposing_team} guessed words are: {dict_store_team_words[opposing_team]}")
    elif current == 0:
        print(f"{opposing_team} guessed words are: {dict_store_team_words[opposing_team]}")
        print(f"{team_going_first} guessed words are: {dict_store_team_words[team_going_first]}")
    print(f"White words are: {dict_store_team_words['WHITE']}")


def check_team_guess_correct(team_guess_word,dict_with_word_color,team_going_first,dict_store_team_words):
    opposing_team = "BLUE" if team_going_first=="RED" else "RED"
    if team_guess_word in dict_with_word_color[team_going_first]:
        dict_with_word_color[team_going_first].remove(team_guess_word)
        dict_store_team_words[team_going_first].append(team_guess_word)
        print(f"\nCorrect! {len(dict_with_word_color[team_going_first])} words left.\n")
        team_status_display(1,team_going_first,opposing_team,dict_store_team_words)
        if len(dict_with_word_color[team_going_first]) != 0:
            return team_going_first
    elif team_guess_word in dict_with_word_color[opposing_team]:
        dict_with_word_color[opposing_team].remove(team_guess_word)
        dict_store_team_words[opposing_team].append(team_guess_word)
        print(f"\nOops, that's the other team's word! Switching turns to the {opposing_team} team. \n")
        team_status_display(0,team_going_first,opposing_team,dict_store_team_words)
        if len(dict_with_word_color[opposing_team]) != 0:
            return opposing_team
    elif team_guess_word in dict_with_word_color["BLACK"]:
        dict_with_word_color["BLACK"].remove(team_guess_word)
        print(f"\nOh no! You guessed the assassin. {team_going_first} team loses!\n")
        print(f"{opposing_team} team wins!!")
        return None
    elif team_guess_word in dict_with_word_color["WHITE"]:
        dict_with_word_color["WHITE"].remove(team_guess_word)
        dict_store_team_words["WHITE"].append(team_guess_word)
        print(f"\nIt is a neutral word. Switching turns to the {opposing_team} team.\n")
        team_status_display(1,team_going_first,opposing_team,dict_store_team_words)
        if len(dict_with_word_color["WHITE"]) != 0:
            return opposing_team
    if len(dict_with_word_color["RED"]) == 0:
        print("Red team wins!")
        return None
    elif len(dict_with_word_color["BLUE"]) == 0:
        print("Blue team wins!")
        return None

    return None

def check_hint_already_given(hint,dict_prev_hint_check,color):
    if hint in dict_prev_hint_check[color]:
        print("Spymaster cannot give the same hint again")
        return True
    else:
        return False

def start_game(dict_with_word_color):
    team_going_first = random.choice(['RED','BLUE'])
    dict_prev_hint_check = {"RED":[],"BLUE":[]}
    dict_store_team_words = {"RED":[],"BLUE":[], "WHITE": []}
    print(team_going_first," team is going first")
    whose_turn = team_going_first
    while whose_turn:
        while True:
            hint = get_hint(whose_turn)
            hint_already_given = check_hint_already_given(hint,dict_prev_hint_check,whose_turn)
            if hint_already_given:
                continue
            else:
                dict_prev_hint_check[whose_turn].append(hint)
                break
        number_of_words = int(get_number_of_words(whose_turn,dict_with_word_color))
        print(f"{whose_turn} team's turn. Hint: {hint} {number_of_words}")
        want_to_continue = 1
        for guess_turn in range(number_of_words+1):
            while True:
                team_guess_word  = input(f"{whose_turn} team, make your guess #{guess_turn+1}: ").upper()
                is_word_present_in_board = check_word_present_in_board(dict_with_word_color,team_guess_word)
                if not is_word_present_in_board:
                    print("This word is not part of the board. Please enter a word part of the board")
                    continue
                else:
                    break
            turn_of_team = check_team_guess_correct(team_guess_word,dict_with_word_color,whose_turn,dict_store_team_words)
            if guess_turn == number_of_words and turn_of_team != None:
                turn_of_team = "BLUE" if whose_turn=="RED" else "RED"
                break
            if turn_of_team is None:
                break
            elif turn_of_team != whose_turn:
                break               
            if guess_turn == number_of_words-1:
                print("\nNumber of words given by the ", whose_turn, " spymaster is over. You can guess one more word from the number of words by spymaster or you can pass your turn to the other team.")
                want_to_continue = int(input("Enter 1 if you want to guess 1 more else enter 0 to pass the turn to the other team: "))
                if want_to_continue == 1:
                    end_current_team_turn = 1
                elif want_to_continue == 0: 
                    end_current_team_turn = 0
            elif guess_turn < number_of_words:
                end_current_team_turn = int(input("\nEnter 1 if you want to continue guessing else enter 0 to end your turn: "))
                print("")
            if end_current_team_turn == 0:
                turn_of_team = "BLUE" if whose_turn=="RED" else "RED"
                break
        whose_turn = turn_of_team
    print("Game over!!")

def info_for_spymaster(dict_with_word_color):
    print("\nInformation for the Spymasters\n")
    print("Red Teams Words are: ", dict_with_word_color['RED'])
    print("Blue Teams Words are: ", dict_with_word_color['BLUE'])
    print("White Words are: ", dict_with_word_color['WHITE'])
    print("Black Word is: ", dict_with_word_color['BLACK'])
    print("")

def game_setup(word_dataset):
    words_current_game = select_25_words(word_dataset)
    words_in_board_format = arranged_board(words_current_game)
    colors_keycard_selection = set_colors_in_keycard()
    colors_in_keycard_format = arranged_board(colors_keycard_selection) 
    dict_with_word_color = associate_word_color(words_in_board_format,colors_in_keycard_format)

    print("This is information for only the spymasters to be seen: ")
    while True:
        pass_for_spymaster = input("Enter the pass given to only the spymasters of the groups for accessing this information: ")
        if pass_for_spymaster == 'pass123':
            info_for_spymaster(dict_with_word_color)
            break
        else:
            print("\n Incorrect password. Please enter the password again. \n")
            continue
    print(" ")
    print("There are three types of team configurations used for playing this version of Codenames. Choose them from the below options.")
    team_configuration = int(input("Press 1 for playing human vs human. Press 2 for playing human vs AI. Press 3 for playing AI vs AI: "))
    if team_configuration == 1:
        print("\nYou have selected the Human vs Human Gameplay option where both the teams has Human spymaster and Human agents\n")
        start_game(dict_with_word_color)
    elif team_configuration == 2:
        print("\nYou have selected the Human vs AI Gameplay option where one team has Human spymaster and Human agents and the other has AI spymaster and AI agents\n")
        game_for_human_ai(dict_with_word_color)
    elif team_configuration == 3:
        print("\nYou have selected the AI vs AI Gameplay option where both the teams have AI spymaster and AI agents\n")
        game_for_ai_ai(dict_with_word_color)

    

def main():
    word_dataset = dataset_creation()
    game_setup(word_dataset)

if __name__ == "__main__":
    main()



