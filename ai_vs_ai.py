import openai
import random
import gensim
import operator
from gensim.models import Word2Vec

openai.api_key = "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"

message_history = []
similarity_level = 0.5

def chat(inp, role="user"):
    message_history.append({"role": role, "content": f"{inp}"})
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message_history
    )
    reply_content = completion.choices[0].message.content
    message_history.append({"role": "assistant", "content": f"{reply_content}"})
    return reply_content

model = gensim.models.KeyedVectors.load_word2vec_format('./GoogleNews-vectors-negative300.bin', binary=True)

def ask_gpt(longest_list):
    ask_gpt_input = "In Codenames, find a hint to associate the words " + str(longest_list) + " Give one word answer as a string"
    check_ans_from_gpt = chat(ask_gpt_input).upper()
    return check_ans_from_gpt

def get_hint(dict_with_word_color,current_team,similarity_level):
    count = 0
    while True:
        dict_similar_words_for_team = find_semantic_similarities(dict_with_word_color[current_team],similarity_level)
        if len(dict_similar_words_for_team) == 0:
            similarity_level -= 0.03
            count += 1
            continue
        elif count == 3:
            break
        else:
            break
    if len(dict_similar_words_for_team) == 0:
        dict_similar_words_for_team[dict_with_word_color[current_team][0]] = dict_with_word_color[current_team][0]
    list_of_current_team_related_words = [[key, *value] if isinstance(value, list) else [key, value] for key, value in dict_similar_words_for_team.items()]
    longest_list = max(list_of_current_team_related_words, key=len)
    list_of_current_team_related_words.remove(longest_list)
    longest_list_copy = longest_list.copy()
    opposite_team = 'RED' if current_team == 'BLUE' else 'BLUE'
    for word in longest_list_copy:
        for other_team_word in dict_with_word_color[opposite_team]:
            if any(item in model for item in [word, word.capitalize(), word.lower().capitalize()]) and any(string in model for string in [other_team_word, other_team_word.capitalize(), other_team_word.lower().capitalize()]):
                similarity = model.similarity(word, other_team_word)
            if similarity > similarity_level and word in longest_list:
                longest_list.remove(word)
        black_team_word = dict_with_word_color['BLACK'][0]
        if any(item in model for item in [word, word.capitalize(), word.lower().capitalize()]) and any(string in model for string in [black_team_word, black_team_word.capitalize(), black_team_word.lower().capitalize()]):
            similarity_with_black = model.similarity(word, black_team_word)
        if similarity_with_black > similarity_level and word in longest_list:
                longest_list.remove(word)

    if len(longest_list) == 0:
        longest_list.append(longest_list_copy[0])

    hint = ask_gpt(longest_list)
    return hint, len(longest_list)




def find_semantic_similarities(word_list,similarity_level):
    semantic_similarities = {}
    for word1 in word_list:
        for word2 in word_list:
            if word1 == word2:
                continue
            if any(item in model for item in [word1, word1.capitalize(), word1.lower().capitalize()]) and any(string in model for string in [word2, word2.capitalize(), word2.lower().capitalize()]):
                similarity = model.similarity(word1, word2)
                if similarity > similarity_level:  
                    if word1 in semantic_similarities:
                        semantic_similarities[word1].append(word2)
                    else:
                        semantic_similarities[word1] = [word2]

    return semantic_similarities

def clean_dict(dict_similar_words_for_team,main_dict):
    check_if_word_present = {}
    for word1, word2 in dict_similar_words_for_team.copy().items():
        if word1 in check_if_word_present:
            dict_similar_words_for_team.pop(word1)
            continue
        else:
            check_if_word_present[word1] = 1
        for word in word2:
            check_if_word_present[word] = 1
    return dict_similar_words_for_team

def get_list_current_team_words_related(cleaned_dict_similar_words_for_team):
    related_words = [next(iter(cleaned_dict_similar_words_for_team))]
    for word in cleaned_dict_similar_words_for_team[related_words[0]]:
        related_words.append(word)
    return related_words

def check_hint_already_given(hint,dict_prev_hint_check,color):
    if hint in dict_prev_hint_check[color]:
        print("\nSpymaster cannot give the same hint again\n")
        return True
    else:
        return False

def guess_word(hint,words_belonging_to_team,similarity_level,number_of_words):
    result_list = []
    dict_with_word_similarity_to_hint = {}
    for word in words_belonging_to_team:
        if any(item in model for item in [hint, hint.capitalize(), hint.lower().capitalize()]) and any(string in model for string in [word, word.capitalize(), word.lower().capitalize()]):
            similarity = model.similarity(hint, word)
        dict_with_word_similarity_to_hint[word] = similarity
        if similarity > similarity_level:
            result_list.append(word)
    ordered_dict_with_word_similarity_to_hint= sorted_d = dict( sorted(dict_with_word_similarity_to_hint.items(), key=operator.itemgetter(1),reverse=True))
    final_result_list = []
    counter_to_check_number_of_words = 0
    for key in ordered_dict_with_word_similarity_to_hint:
        final_result_list.append(key)
        counter_to_check_number_of_words += 1
        if counter_to_check_number_of_words == number_of_words:
            break
    return final_result_list


def check_team_guess_correct(team_guess_word,dict_with_word_color,team_going_first):
    opposing_team = "BLUE" if team_going_first=="RED" else "RED"
    if team_guess_word in dict_with_word_color[team_going_first]:
        dict_with_word_color[team_going_first].remove(team_guess_word)
        print(f"\nCorrect! {len(dict_with_word_color[team_going_first])} words left.\n")
        if len(dict_with_word_color[team_going_first]) != 0:
            return team_going_first
    elif team_guess_word in dict_with_word_color[opposing_team]:
        dict_with_word_color[opposing_team].remove(team_guess_word)
        print("\nOops, that's the other team's word!\n")
        if len(dict_with_word_color[opposing_team]) != 0:
            return opposing_team
    elif team_guess_word in dict_with_word_color["BLACK"]:
        dict_with_word_color["BLACK"].remove(team_guess_word)
        print(f"\nOh no! You guessed the assassin. {team_going_first} team loses!\n")
        print(f"\n{opposing_team} wins!!")
        return None
    elif team_guess_word in dict_with_word_color["WHITE"]:
        dict_with_word_color["WHITE"].remove(team_guess_word)
        print(f"\nIt is a neutral word. Switching turns to the {opposing_team} team.\n")
        if len(dict_with_word_color["WHITE"]) != 0:
            return opposing_team
    if len(dict_with_word_color["RED"]) == 0:
        print("\nRed team wins!\n")
        return None
    elif len(dict_with_word_color["BLUE"]) == 0:
        print("\nBlue team wins!\n")
        return None
    
    return None


def begin_ai_vs_ai_game(dict_with_word_color):
    team_going_first = random.choice(['RED','BLUE'])
    dict_prev_hint_check = {"RED":[],"BLUE":[]}
    print(team_going_first," team is going first\n")
    whose_turn = team_going_first
    opposite_team = "BLUE" if whose_turn=="RED" else "RED"
    
    while whose_turn:
        hint,number_of_words = get_hint(dict_with_word_color,whose_turn,similarity_level)
        print(f"{whose_turn} team's turn. Hint: {hint} {number_of_words}\n")
        want_to_continue = 1
        team_guess_word  = guess_word(hint,dict_with_word_color[whose_turn],similarity_level,number_of_words)
        print("team_guess_word ", team_guess_word)
        for guess_turn in range(len(team_guess_word)):
            print(f"{whose_turn} team, made {guess_turn+1} guess as : ",team_guess_word[guess_turn])
            turn_of_team = check_team_guess_correct(team_guess_word[guess_turn],dict_with_word_color,whose_turn)
            print(dict_with_word_color)
            if guess_turn == number_of_words-1 and turn_of_team != None:
                turn_of_team = "BLUE" if whose_turn=="RED" else "RED"
                break
            if turn_of_team is None:
                break
            elif turn_of_team != whose_turn:
                break
        whose_turn = turn_of_team

def game_for_ai_ai(dict_with_word_color):
    begin_ai_vs_ai_game(dict_with_word_color)
    return dict_with_word_color

