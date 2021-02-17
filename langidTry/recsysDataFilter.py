import csv

from langid import langid

if __name__ == '__main__':
    with open("Electronics.txt", "r", encoding="utf-8") as readFile:
        with open("electronics_filtered.csv", "w", encoding="utf-8", newline="") as writeFile:
            csvWriter = csv.writer(writeFile)
            currRow = ["", ""]
            for line in readFile.readlines():
                if line[-1] == "\n":
                    line = line[:-1]
                if line.startswith("review/score"):
                    currRow[0] = line[13:].strip()
                if line.startswith("review/text"):
                    currRow[1] = line[12:].strip()
                    csvWriter.writerow(currRow)
                    currRow = ["", ""]

    with open("electronics_filtered.csv", "r", encoding="utf-8") as filteredReadFile:
        with open("electronics_filtered_and_smaller.csv", "w", encoding="utf-8", newline="") as filteredWriteFile:
            csvReader = csv.reader(filteredReadFile)
            csvWriter = csv.writer(filteredWriteFile)
            for row in csvReader:
                if row[0] == 3.0:
                    continue
                language, score = langid.classify(row[1])
                newRow = ["", "", ""]
                newRow[0] = language
                newRow[1] = row[0]
                newRow[2] = row[1]
                csvWriter.writerow(newRow)
