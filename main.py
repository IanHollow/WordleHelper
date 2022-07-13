from sympy import false, nextprime
import string
import pandas as pd
import json


class WordleHelper:
    WORD_LEN = 5
    ALPHABET = list(string.ascii_lowercase)

    def __init__(self, words: list):
        self.alphabet_prime = None
        with open("alphabet_primes.json", "r") as fp:
            self.alphabet_prime = json.load(fp)
        self.prime_words = self.words2Prime(words)
        self.letterPrct = self.letterPrcntGen()

    def alphaLookupGen(self) -> dict:
        self.WORD_LEN += 1
        primes = []
        with open("primes.txt", "r") as fp:
            primes = json.load(fp)

        alpha_prime = dict()
        for i in range(len(self.ALPHABET)):
            alpha_prime[self.ALPHABET[i]] = primes[i*self.WORD_LEN]
            for place in range(1, self.WORD_LEN):
                alpha_prime[self.ALPHABET[i] +
                            str(place)] = primes[(i*self.WORD_LEN)+place]

        with open("alphabet_primes.json", "w") as fp:
            json.dump(alpha_prime, fp)
        return alpha_prime

    def primeNumGen(self, length: int) -> list:
        primes = []
        previous = 2
        for _ in range(length):
            previous = nextprime(previous)
            primes.append(previous)

        with open("primes.txt", "w") as fp:
            json.dump(primes, fp)

        return primes

    def words2Prime(self, words: list) -> list:
        for i in range(len(words)):
            prime_word = 1
            for j in range(len(words[i])):
                prime_word *= self.letter2Prime(words[i][j], j+1)
            words[i] = prime_word

        return words

    def letter2Prime(self, letter: str, position: int) -> int:
        letter = letter.lower()
        return self.alphabet_prime[letter+str(position)] * self.alphabet_prime[letter]

    def letterPrcntGen(self) -> pd.Series:
        prcnts = []
        total = len(self.prime_words)*5
        for letter in self.ALPHABET:
            letter_amount = 0
            for prime_word in self.prime_words:
                prime_letter = self.alphabet_prime[letter]
                original_prime = prime_letter
                for _ in range(5):
                    if prime_word % prime_letter == 0:
                        letter_amount += 1
                        prime_letter *= original_prime
                    else:
                        break
            prcnts.append(int((letter_amount/total)*10000)/100)
        s = pd.Series(prcnts, self.ALPHABET).sort_values(ascending=False)
        return s


wordle_allowed = []
wordle_answers = []

with open("wordle_allowed.txt", "r") as fp:
    wordle_allowed = json.load(fp)

with open("wordle_answers.txt", "r") as fp:
    wordle_answers = json.load(fp)

wordleHelper = WordleHelper(wordle_answers)

print(wordleHelper.letterPrct)
