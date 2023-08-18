import gensim
import openai
import np
import random
import itertools
import time

openai.api_key = "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"
model = gensim.models.KeyedVectors.load_word2vec_format('./GoogleNews-vectors-negative300.bin', binary=True)

message_history = []

def find_hint_semantic_similarities(target_word, team_words, top_n=5):
    similar_words = []
    for word in team_words:
        if word in model: 
            similar_words.append((word, model.similarity(target_word, word)))
    similar_words.sort(key=lambda x: x[1], reverse=True)
    return [word[0] for word in similar_words[:top_n]]

def get_hint_from_openai(similar_words):
    prompt = f"give a one word noun hint for used to associate words: {similar_words}"
    message_history.append({"role": "user", "content": f"{prompt}"})
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message_history
    )
    hint = completion.choices[0].message.content
    return hint

def guess_word(hint, team_words, top_n=3):
    return find_hint_semantic_similarities(hint, team_words, top_n)


def find_semantic_similarities(team_words, threshold=0.5):
    similar_pairs = []
    for word1, word2 in itertools.combinations(team_words, 2):
        try:
            similarity = model.similarity(word1, word2)
            if similarity > threshold:
                similar_pairs.append((word1, word2, similarity))
        except KeyError:
            continue
    return similar_pairs



choose_model = int(input("Press 1 for using Word2vec for semantic similarity. Press 2 for using OpenAI for semantic similarity: "))
if choose_model == 1:
    print("Using Word2vec model")
elif choose_model == 2:
    print("Using OpenAI model")

print("===============")
team_going_first = random.choice(['RED','BLUE'])
dict_prev_hint_check = {"RED":[],"BLUE":[]}
print(f"\n{team_going_first} team is going first\n")
whose_turn = team_going_first
opposite_team = "BLUE" if whose_turn=="RED" else "RED"

dict_with_word_color = {'RED': ['CHAIR', 'SPIKE', 'LONDON', 'EGYPT', 'PILOT', 'CAT', 'ROUND', 'DOCTOR'], 'BLUE': ['BUFFALO', 'GLOVE', 'THIEF', 'TRIP', 'TRAIN', 'CHURCH', 'MINT', 'ROBIN'], 'WHITE': ['EUROPE', 'ROSE', 'DOG', 'AMERICA', 'SATELLITE', 'MEXICO', 'GREEN', 'BOW'], 'BLACK': ['PUMPKIN']}
team_words =  dict_with_word_color['BLUE']

start_time = time.time()
similar_words = find_semantic_similarities(team_words)

hint = get_hint_from_openai(similar_words)
print(f"\n{team_going_first} spymaster gives Hint: {hint} {len(similar_words)}")

words_guessed_by_team = {"RED":[],"BLUE":[],"WHITE":[]}

def check_team_guess_correct(guessed_word,team_words):
    if guessed_word in team_words:
        dict_with_word_color['BLUE'].remove(guessed_word)
        words_guessed_by_team['BLUE'].append(guessed_word)
        print(f"Correct! {len(dict_with_word_color[team_going_first])} words left.\n")
        if len(dict_with_word_color[team_going_first]) != 0:
            return team_going_first

def display_words():
    print(f"BLUE team guessed words are: {words_guessed_by_team['BLUE']}")
    print(f"RED guessed words are: {words_guessed_by_team['RED']}")
    print(f"White words are: {words_guessed_by_team['WHITE']}")

guessed_words = guess_word(hint, team_words)
for count in range(len(guessed_words)):
    print(f"\n{count+1} guessed word is : {guessed_words[count]}")
    check_team_guess_correct(guessed_words[count],team_words)
    display_words()

end_time = time.time()

print("\nTotal time taken for execution for Word2vec is ", round(end_time-start_time, 2), " seconds\n")

print(f'{opposite_team} team"s turn!!')

