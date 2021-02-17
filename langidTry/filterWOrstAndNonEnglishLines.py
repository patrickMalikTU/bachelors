import csv

if __name__ == '__main__':
    with open("kindleDatafilteredAgain.csv", "r", encoding="utf-8") as readFile:
        with open("kindleDataFilteredAgainWorstNonEnglish", "w", encoding="utf-8", newline="") as writeFile:
            csvReader = csv.reader(readFile)
            csvWriter = csv.writer(writeFile)
            for line in csvReader:
                if line[0] == "en" or float(line[1]) >= 3:
                    continue
                else:
                    csvWriter.writerow(line)
