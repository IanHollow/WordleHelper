from sympy import nextprime
import string
import pandas as pd
import json


class WordleHelper:
    WORD_LEN = 5
    ALPHABET = list(string.ascii_lowercase)

    def __init__(self, words: list):
        self.word_list = words

        self.prime_alpha_dict = None
        with open("prime_alpha_dict.json", "r") as fp:
            self.prime_alpha_dict = json.load(fp)

        self.prime_words = self.words2Prime(self.word_list)

        self.letterPrcnts = self.letterPrcntGen()

    def alphaLookupGen(self) -> dict:
        self.WORD_LEN += 1
        primes = []
        with open("primes.txt", "r") as fp:
            primes = json.load(fp)

        alpha_prime = {}
        for i in range(len(self.ALPHABET)):
            alpha_prime[self.ALPHABET[i]] = primes[i*self.WORD_LEN]
            for place in range(1, self.WORD_LEN):
                alpha_prime[self.ALPHABET[i] +
                            str(place)] = primes[(i*self.WORD_LEN)+place]

        with open("prime_alpha_dict.json", "w") as fp:
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
        prime_words = [None]*len(words)
        for i in range(len(words)):
            prime_word = 1
            for j in range(len(words[i])):
                prime_word *= self.letter2Prime(words[i][j], j+1)
            prime_words[i] = prime_word

        return prime_words

    def letter2Prime(self, letter: str, position: int) -> int:
        letter = letter.lower()
        return self.prime_alpha_dict[letter+str(position)] * self.prime_alpha_dict[letter]

    def letterPrcntGen(self) -> list:
        prcnts = {}
        prcnts_arr = []
        total = len(self.word_list)
        whole_prcnts = [0]*26

        for place in range(5):
            partial_prcnts = {}
            for i in range(len(self.ALPHABET)):
                letter_amount = 0
                for word in self.word_list:
                    if word[place] == self.ALPHABET[i]:
                        letter_amount += 1
                whole_prcnts[i] += letter_amount
                partial_prcnts[self.ALPHABET[i]] = (letter_amount/total)*100
            prcnts_arr.append(partial_prcnts)
            prcnts[str(place+1)] = pd.Series(partial_prcnts, self.ALPHABET)

        for i in range(len(whole_prcnts)):
            whole_prcnts[i] = (whole_prcnts[i]/(total*5))*100
        # prcnts["whole"] = pd.Series(whole_prcnts, self.ALPHABET)

        for i in range(len(prcnts_arr)):
            prcnts_arr[i] = prcnts_arr[i]

        df = pd.DataFrame(
            prcnts, self.ALPHABET, columns=["whole", "1", "2", "3", "4", "5"]
        )

        print(f"length: {len(self.word_list)}")
        print(df)
        return prcnts_arr

    def findNextBestWord(self, removeDupes: bool = False):
        best_word = []
        best_score = 0
        best_score_arr = None
        for word in self.word_list:
            new_score = 0
            new_score_arr = []
            letter_arr = []
            for i in range(len(word)):
                new_score += self.letterPrcnts[i][word[i]]
                new_score_arr.append(self.letterPrcnts[i][word[i]])
                letter_arr.append(word[i])

            if removeDupes and len(set(letter_arr)) < 5:
                new_score -= 1000

            if new_score > best_score:
                best_word = [word]
                best_score = new_score
                best_score_arr = new_score_arr
            elif new_score == best_score:
                best_word.append(word)

        return (best_word, round(best_score, 2), best_score_arr)

    def enterGuess(self, word: str, signs: list):
        dupes_multi_max = []
        for _ in range(5):
            dupes_multi_max.append([0, 1, 0])
        for i in range(len(word)):
            for j in range(len(word)):
                if i == j:
                    continue
                elif word[i] == word[j]:
                    dupes_multi_max[i][0] += 1
                    dupes_multi_max[i][2] = dupes_multi_max[i][0]

        for i in range(len(word)):
            for j in range(len(word)):
                if i == j:
                    continue
                elif dupes_multi_max[i][0] >= 1 and word[i] == word[j]:
                    # if either yellow or green
                    if (signs[i] == 1 or signs[i] == 2) and (signs[j] == 1 or signs[j] == 2):
                        dupes_multi_max[i][1] += 1
                    # if i index is yellow or green and j gray
                    elif ((signs[i] == 1 or signs[i] == 2) and signs[j] == 0):
                        signs[j] = 3
                        if signs[i] == 2 and dupes_multi_max[i][2] > 1:
                            dupes_multi_max[i][2] -= 1
                    # if j index is yellow or green and i gray
                    elif (signs[i] == 0 and (signs[j] == 1 or signs[j] == 2)):
                        signs[i] = 3
                        if signs[j] == 2 and dupes_multi_max[i][2] > 1:
                            dupes_multi_max[j][2] -= 1

        for i in range(len(word)):
            prime_letter = self.prime_alpha_dict[word[i]]
            prime_index_letter = self.prime_alpha_dict[word[i]+f"{i+1}"]
            new_word_list = []

            #print(signs)
            #print(dupes_multi_max)

            if signs[i] == 2:  # Green
                for j in range(len(self.prime_words)):
                    cond1 = True
                    if dupes_multi_max[i][1] > 1:

                        cond1 = (self.prime_words[j] % (
                            prime_letter**dupes_multi_max[i][1]) == 0)

                    cond2 = True
                    if dupes_multi_max[i][2] > 0:
                        cond2 = True
                        for k in range(dupes_multi_max[i][2]+1, len(word)):
                            if cond2:
                                cond2 = (self.prime_words[j] % (
                                    prime_letter**k) != 0)

                    if (self.prime_words[j] % prime_index_letter == 0) and (cond1 and cond2):

                        new_word_list.append(self.word_list[j])

            elif signs[i] == 1:  # Yellow
                for j in range(len(self.prime_words)):
                    cond1 = 1
                    if dupes_multi_max[i][1] > 1:
                        cond1 = True
                        cond1 = (self.prime_words[j] % (
                            prime_letter**dupes_multi_max[i][1]) == 0)

                    cond2 = True
                    if dupes_multi_max[i][2] > 0:
                        cond2 = True
                        for k in range(dupes_multi_max[i][2]+1, len(word)):
                            if cond2:
                                cond2 = (self.prime_words[j] % (
                                    prime_letter**k) != 0)

                    if((self.prime_words[j] % prime_letter == 0) and (self.prime_words[j] % prime_index_letter != 0)) and (cond1 and cond2):

                        new_word_list.append(self.word_list[j])

            elif signs[i] == 0:  # Gray
                for j in range(len(self.prime_words)):

                    if (self.prime_words[j] % prime_letter != 0):

                        new_word_list.append(self.word_list[j])

            elif signs[i] == 3:  # Skip
                new_word_list = self.word_list

            else:
                print("Invalid Word State")
                return

            self.regenWordLists(new_word_list)

        # Regen Percentages
        self.letterPrcnts = self.letterPrcntGen()

        print(self.findNextBestWord())

    def regenWordLists(self, new_word_list: list):
        self.word_list = new_word_list
        self.prime_words = self.words2Prime(self.word_list)


wordle_allowed = []
wordle_answers = []

with open("wordle_allowed.txt", "r") as fp:
    wordle_allowed = json.load(fp)

with open("wordle_answers.txt", "r") as fp:
    wordle_answers = json.load(fp)

wordleHelper = WordleHelper(wordle_allowed)

# print(wordleHelper.findNextBestWord(removeDupes=True))

wordleHelper.enterGuess("", [0, 0, 1, 2, 0])

#wordleHelper.enterGuess("", [2, 0, 2, 2, 0])

#wordleHelper.enterGuess("", [2, 2, 2, 2, 0])
