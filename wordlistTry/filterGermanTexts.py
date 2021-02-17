import csv
import re


def createsPatternFromFile(fileName):
    pattern = ""
    with open(fileName, "r", encoding="utf-8") as mostCommonWordsFile:
        for word in mostCommonWordsFile.readlines():
            word = word.strip()
            pattern += '(([ \\.\\",]' + word + ')|(^' + word + '))' + '[ \\.,\\"]|'
    if pattern[-1] == "|":
        pattern = pattern[:-1]
    return pattern


def containsTopGermanWords(text):
    pattern = createsPatternFromFile("1000mostCommonGermanWords")
    patternMatcher = re.compile(pattern, re.IGNORECASE)
    if patternMatcher.search(text) is not None:
        return True
    return False


def containsTopEnglishWords(text):
    pattern = createsPatternFromFile("1000mostCommonEnglishWords")
    patternMatcher = re.compile(pattern, re.IGNORECASE)
    res = patternMatcher.search(text)
    if res is not None:
        return True
    return False


if __name__ == '__main__':
    with open("../langidTry/filteredDe_data.csv", "w", encoding="utf-8", newline="") as writeFile:
        csvWriter = csv.writer(writeFile, delimiter=",")
        for i in range(0, 1026):
            with open("./csvs/booksDataFiltered_" + str(i) + ".csv", "r", encoding="utf-8") as file:
                reader = csv.reader((line.replace('\0', '') for line in file), delimiter=",")
                for line in reader:
                    if containsTopGermanWords(line[2]):
                        csvWriter.writerow([line[1], line[2]])
