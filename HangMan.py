import random

#Wordlist / counter, constant variables. Wordlist can be modified to add/remove
WORDLIST = 'tobi bram charlie pip dexter pip jenna sjakie milo'.split()
COUNTER = ['oooooooo', 'xooooooo', 'xxoooooo', 'xxxooooo', 'xxxxoooo', 'xxxxxooo', 'xxxxxxoo', 'xxxxxxxo', 'xxxxxxxx']

#Variables pertainting to word characteristics
listLength = len(WORDLIST)
wordChoice = WORDLIST[random.randint(0,(listLength-1))]
wordLength = len(wordChoice)

#Guess counters
gameIsDone = False
guessAmount = 0
guess = ''
guessedLetters = ['']
wordList = wordChoice.split()

#Preamble
print('Welcome to Hangman!')
print()

#Game loop
while gameIsDone == False:
    displayLijst = list(range(0,wordLength))
    for x in range(wordLength):
        if wordChoice[x] in guessedLetters:
            displayLijst[x] = wordChoice[x]
        else:
            displayLijst[x] = "_"
    print()
    print('Current word: (underscores represent characters not guessed yet)')
    print(*displayLijst, sep=' ')
    print()
    print('Amount of guesses left:')
    print(COUNTER[guessAmount])
    print()
    print('Please input a guess letter to make a new guess, or alternatively input the full word.')
    print()
    guess = str(input())
    if len(guess) == 1:
        print()
        while guess in guessedLetters:
            print('You have already entered that letter! Please input a new letter.')
            guess = str(input())
        if guess in wordChoice:
            print('That letter is in the secret word.')
            guessedLetters.append(guess)
        else:
            print('Nope, not in the secret word!')
            guessAmount = guessAmount + 1
            guessedLetters.append(guess)
        print()
    if len(guess) > 1:
        if guess==wordChoice:
            print('Correct! You win.')
            gameIsDone = True
        else:
            print('Wrong guess!')
            print()
            guessAmount = guessAmount + 1
    if guessAmount == 8:
        print('You are out of guesses! The word was ' + wordChoice)
        gameIsDone = True
