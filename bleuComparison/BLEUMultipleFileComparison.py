from itertools import repeat

from nltk import word_tokenize
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction


def check_if_linenumbers_match(lines):
    length = -1
    for line in lines:
        if length == -1:
            length = len(line)
        else:
            if length != len(line):
                return False
    return True


if __name__ == '__main__':
    # First file hase to be starting language, second file corresponding translation,
    # all the following files are the ones to be tested
    fileNames = ["deutsch.txt", "englisch.txt", "google.txt", "deepL.txt", "microsoft.txt", "aws.txt"]
    # Number of hypothesis, since the first 2 are references
    hypNo = len(fileNames) - 2
    fileLines = []

    if hypNo < 1:
        print("Not enough files")
        exit(1)

    for filename in fileNames:
        f = open(filename, "r", encoding="utf-8")
        fileLines.append(f.readlines())
        f.close()

    if not check_if_linenumbers_match(fileLines):
        print("all the files must have the same amount of lines, the files are compared line by line")
        exit(1)

    sampleSize = len(fileLines[0])
    # Starts at 0, will be summed up and divided by samplesize
    bleuScores = list(repeat(0, hypNo))
    for i in range(0, sampleSize):
        sentence = word_tokenize(fileLines[0][i])
        reference = word_tokenize(fileLines[1][i])
        for f in range(2, hypNo + 2):
            bleuScores[f - 2] += sentence_bleu([reference], word_tokenize(fileLines[f][i]),
                                               smoothing_function=SmoothingFunction().method4)

    print(sampleSize)
    for i in range(0, hypNo):
        print(fileNames[i + 2] + ":")
        print(bleuScores[i] / sampleSize)
