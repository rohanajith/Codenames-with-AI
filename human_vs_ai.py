import gensim
import openai
import random
import itertools

openai.api_key = "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"
model = gensim.models.KeyedVectors.load_word2vec_format('./GoogleNews-vectors-negative300.bin', binary=True)
message_history = []

dict_store_team_words = {"RED":[],"BLUE":[], "WHITE": []}

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

def check_team_guess_correct(team_guess_word,dict_with_word_color,team_going_first,dict_store_team_words):
    opposing_team = "BLUE" if team_going_first=="RED" else "RED"
    if team_guess_word in dict_with_word_color[team_going_first]:
        dict_with_word_color[team_going_first].remove(team_guess_word)
        dict_store_team_words[team_going_first].append(team_guess_word)
        print(f"\nCorrect! {len(dict_with_word_color[team_going_first])} words left.\n")
        if len(dict_with_word_color[team_going_first]) != 0:
            return team_going_first
    elif team_guess_word in dict_with_word_color[opposing_team]:
        dict_with_word_color[opposing_team].remove(team_guess_word)
        dict_store_team_words[opposing_team].append(team_guess_word)
        print(f"\nOops, that's the other team's word! Switching turns to the {opposing_team} team. \n")
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
        if len(dict_with_word_color["WHITE"]) != 0:
            return opposing_team
    if len(dict_with_word_color["RED"]) == 0:
        print("Red team wins!")
        return None
    elif len(dict_with_word_color["BLUE"]) == 0:
        print("Blue team wins!")
        return None

    return None

def play_human_version(dict_with_word_color,colour_of_current_team):
    opposing_team = "BLUE" if colour_of_current_team=="RED" else "RED"
    hint = get_hint(colour_of_current_team)
    number_of_words = int(get_number_of_words(colour_of_current_team,dict_with_word_color))
    print(f"{colour_of_current_team} team's turn. Hint: {hint} {number_of_words}")
    for guess_turn in range(number_of_words):
        team_guess_word  = input(f"{colour_of_current_team} team, make your guess #{guess_turn+1}: ").upper()
        turn_of_team = check_team_guess_correct(team_guess_word,dict_with_word_color,colour_of_current_team,dict_store_team_words)
        display_words()
        if turn_of_team != colour_of_current_team:
            return opposing_team
        if turn_of_team == None:
            return None
    return opposing_team

def find_most_similar_to_average(team_words, threshold=0.5):
    similar_pairs = []
    for word1, word2 in itertools.combinations(team_words, 2):
        try:
            similarity = model.similarity(word1, word2)
            if similarity > threshold:
                similar_pairs.append((word1, word2, similarity))
        except KeyError:
            continue
    return similar_pairs

def get_hint_from_openai(similar_words):
    prompt = f"give a one word noun hint for used to associate words: {similar_words}"
    message_history.append({"role": "user", "content": f"{prompt}"})
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message_history
    )
    hint = completion.choices[0].message.content
    return hint

def display_words():
    print(f"BLUE team guessed words are: {dict_store_team_words['BLUE']}")
    print(f"RED guessed words are: {dict_store_team_words['RED']}")
    print(f"White words are: {dict_store_team_words['WHITE']}")

def find_semantically_similar_words(target_word, team_words, top_n=5):
    similar_words = []
    for word in team_words:
        if word in model:  
            similar_words.append((word, model.similarity(target_word, word)))
    similar_words.sort(key=lambda x: x[1], reverse=True)
    return [word[0] for word in similar_words[:top_n]]

def guess_word(hint, team_words, top_n=3):
    return find_semantically_similar_words(hint, team_words, top_n)

def play_AI_version(dict_with_word_color, whose_turn):
    opposing_team = "BLUE" if whose_turn=="RED" else "RED"
    team_words =  dict_with_word_color[whose_turn]
    similar_words = find_most_similar_to_average(team_words)
    hint = get_hint_from_openai(similar_words)
    print(f"\n{whose_turn} spymaster gives Hint: {hint} {len(similar_words)}")
    guessed_words = guess_word(hint, team_words)
    if len(guessed_words) == 0:
        guessed_words = [dict_with_word_color[whose_turn][0],dict_with_word_color[whose_turn][1]]
    for count in range(len(guessed_words)):
        print(f"\n{count+1} guessed word is : {guessed_words[count]}")
        colour = check_team_guess_correct(guessed_words[count],dict_with_word_color,whose_turn,dict_store_team_words)
        display_words()
        if whose_turn != colour or count == len(similar_words)-1:
            return opposing_team
        if whose_turn == None:
            return None
    return colour

def begin_human_vs_ai_game(dict_with_word_color):

    team_going_first = random.choice(["RED","BLUE"])
    choose_human_or_ai = random.choice(["HUMAN","AI"])
    player_for_team = {}
    player_for_team[team_going_first] = choose_human_or_ai
    whose_turn = team_going_first
    opposite_team = "BLUE" if whose_turn=="RED" else "RED"
    player_for_team[opposite_team] = "AI" if choose_human_or_ai=="HUMAN" else "HUMAN"
    print(f"{team_going_first} is {player_for_team[team_going_first]} and {opposite_team} is {player_for_team[opposite_team]}")
    print(team_going_first," team is going first\n")

    whose_turn = team_going_first
    colour = ""
    while whose_turn:
        if player_for_team[whose_turn] == "HUMAN":
            colour = play_human_version(dict_with_word_color, whose_turn)
        elif player_for_team[whose_turn] == "AI":
            colour = play_AI_version(dict_with_word_color, whose_turn)
        whose_turn = colour
    print("Game over!!")


def game_for_human_ai(dict_with_word_color):
    begin_human_vs_ai_game(dict_with_word_color)
    return dict_with_word_color