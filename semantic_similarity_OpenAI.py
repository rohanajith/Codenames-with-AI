import openai
import time

openai.api_key = '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'

def get_similar_words_for_spymaster(team_words):
    message = [{
        "role": "user",
        "content": f"Find one group of words that are semantically similar from the list: {team_words}. Print just the words without any other statements"
    }]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message
    )
    similar_words = response.choices[0].message.content.split(", ")
    return similar_words

def get_hint(words):
    message = [{
        "role": "user",
        "content": f"Give a one word noun hint without fullstop that connects: {words}"
    }]
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message
    )
    return response.choices[0].message.content.strip()

def guess_words_from_hint(hint, team_words):
    message = [{
        "role": "user",
        "content": f"Based on the hint '{hint}', which words from the list {team_words} are semantically similar?  Return just those 3 words without any other statements, seperated by comma"
    }]
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message
    )
    guessed_words = response.choices[0].message.content.split(", ")
    return guessed_words

dict_with_word_color = {'RED': ['GAME', 'FOREST', 'HOOD', 'BRUSH', 'SCIENTIST', 'WEB', 'WHALE', 'PASS'], 'BLUE': ['PIE', 'PUMPKIN', 'CENTAUR', 'MUG', 'RACKET', 'PLANE', 'NOTE', 'ENGLAND'], 'WHITE': ['ARM', 'SMUGGLER', 'NET', 'BILL', 'FENCE', 'CHICK', 'GLOVE', 'LINK'], 'BLACK': ['PASTE']}
team_words =  dict_with_word_color['RED']
words_guessed_by_team = {"RED":[],"BLUE":[],"WHITE":[]}


choose_model = int(input("Press 1 for using Word2vec for semantic similarity. Press 2 for using OpenAI for semantic similarity: "))
if choose_model == 1:
    print("Using Word2vec model")
elif choose_model == 2:
    print("Using OpenAI model")

print("===============")

is_team1_turn = True

def check_team_guess_correct(word,team_words):

    if word in team_words:
        team_words.remove(word)
        words_guessed_by_team['RED'].append(word)
        print(f"\nCorrect! {len(team_words)} words left.\n")
        if len(team_words) != 0:
            return team_words

start_time = time.time()

def display_words():
    print(f"RED guessed words are: {words_guessed_by_team['RED']}")
    print(f"BLUE team guessed words are: {words_guessed_by_team['BLUE']}")
    print(f"White words are: {words_guessed_by_team['WHITE']}")

count = 0
while True:
    if is_team1_turn:
        print("\nRED Team's Turn:")
        similar_words_for_spymaster = get_similar_words_for_spymaster(team_words)
        hint_for_team = get_hint(similar_words_for_spymaster)
        guessed_words_for_team = guess_words_from_hint(hint_for_team, team_words)
        print(f"\nRED team spymaster gives Hint: {hint_for_team} {len(guessed_words_for_team)}")
        for word in guessed_words_for_team:
            print(f"\n{count+1} guessed word is : {word}")
            check_team_guess_correct(word,team_words)
            display_words()
    
    is_team1_turn = not is_team1_turn
    if not is_team1_turn:
        break

end_time = time.time()

print("\nTotal time taken for execution for OpenAI is ", round(end_time-start_time, 2), " seconds")
print("\nBLUE Team's Turn:")