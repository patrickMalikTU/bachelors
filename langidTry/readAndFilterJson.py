import csv

import jsonlines
from langid import langid

if __name__ == '__main__':
    with jsonlines.open("C:/Users/Austr/Desktop/Books.json/Books.json") as reader:
        writeFile = open("../csvs/booksDataFiltered.csv", "w", encoding="utf-8", newline="")
        counter = 0
        fileCounter = 0
        csvWriter = csv.writer(writeFile)
        for line in reader:
            if counter == 50000:
                counter = 0
                writeFile.close()
                writeFile = open("./csvs/booksDataFiltered_" + str(fileCounter) + ".csv", "w", encoding="utf-8", newline="")
                csvWriter = csv.writer(writeFile)
                fileCounter += 1
            counter += 1
            row = ["", "", ""]
            row[1] = line["overall"]
            if float(row[1]) == 3.0 or "reviewText" not in line.keys():
                continue
            row[2] = line["reviewText"]
            language, score = langid.classify(row[2])
            row[0] = language

            csvWriter.writerow(row)
