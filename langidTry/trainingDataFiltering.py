import csv
import langid

if __name__ == '__main__':
    with open("train.csv", "r", encoding="utf-8") as readFile:
        with open("trainDataFilteredAndLanguage.csv", "w", encoding="utf-8", newline="") as writeFile:
            # writeFileTempString = "testDataFiltered_"
            # csvConst = ".csv"
            # writeFile = open("testDataFiltered.csv", "w", encoding="utf-8", newline='')
            csvReader = csv.reader(readFile)
            csvWriter = csv.writer(writeFile)
            # languages = {}
            for row in csvReader:
                if row[0] != 3:
                    content = row[2]
                    try:
                        language, score = langid.classify(content)
                    except:
                        language = "noLang"

                    if int(row[0]) < 3:
                        csvWriter.writerow([language, "-1", content])
                    else:
                        csvWriter.writerow([language, "1", content])
