# Codenames-with-AI

**Overview:**

An AI system to play Codenames.

**Features:**

1) The board game can be played in 3 configurations: Human vs Human, Human vs AI and AI vs AI
1) AI system can play the board game Codenames autonomously, acting both as the spymaster giving hints and as the player guessing words.
2) The project leverages Word2Vec and  OpenAI's GPT models to understand semantic relations between words, allowing for hints that are contextually relevant.
3) After receiving the hint, the AI analyzes and makes educated guesses on potential words on the board that the hint might be referring to.

**Prequisities required to be installed:**

1) Gensim
2) Spacy
3) OpenAI
4) GoogleNews-vectors-negative300.bin - can be installed from https://www.kaggle.com/datasets/leadbest/googlenewsvectorsnegative300 and should be in the same directory as the other files
