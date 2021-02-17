import ast

if __name__ == '__main__':
    with open("original/translations/5-star_translated.txt", "r", encoding="utf-8") as readFile:
        lines = readFile.readlines()

    splitString = "}]}]"
    linesSplit = (lines[0].split(splitString))
    linesSplit = linesSplit[:-1]

    texts = []
    for line in linesSplit:
        line = line + splitString
        #        print(ast.literal_eval(line)[0])
        texts.append(ast.literal_eval(line)[0].get('translations')[0].get("text"))

    with open("original/translations/5-star_translated_mapped.txt", "w", encoding="utf-8") as writeFile:
        writeFile.writelines(texts)
