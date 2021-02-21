from statistics import median

import util

from nltk import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
from nltk.classify.naivebayes import NaiveBayesClassifier
from nltk.sentiment.vader import SentimentIntensityAnalyzer as Vader_EN
from nltk.parse.corenlp import CoreNLPParser
from polyglot.text import Text
from sklearn import svm
from textblob import TextBlob as TextBlob_EN
from textblob_de import TextBlobDE as TextBlob_DE

from randomizeFromFiles import K_fold_style_data_picker, K_fold_data_picker_mixed, K_fold_parallel_file_reader
from util import RunConfiguration, F1Composite
from vaderSentimentGER import SentimentIntensityAnalyzer as Vader_DE


class Review:
    def __init__(self, rating, text, to_lower_case=True, make_binary_class=True, language="english", stemming=True,
                 stopword_removal=True):
        if make_binary_class:
            self.rating = self.__categories_to_binary(rating)
        else:
            self.rating = rating

        if to_lower_case:
            self.text = text.lower()
        else:
            self.text = text

        # tokenizing
        self.tokenized_text = word_tokenize(text)

        # stop-word removal
        if stopword_removal:
            stop_words = set(stopwords.words(language))
            self.tokenized_text = [x for x in self.tokenized_text if x not in stop_words]

        # stemming
        if stemming:
            stemmed_text = []
            stemmer = SnowballStemmer(language=language)
            for token in self.tokenized_text:
                stemmed_text.append(stemmer.stem(token))
            self.tokenized_text = stemmed_text

        self.vectorized_data = {}

    @staticmethod
    def __categories_to_binary(rating):
        if int(rating) < 3:
            return 0
        return 1

    def bag_of_words(self, matrix_key_list: list):
        vectorized_data = {x: 0 for x in matrix_key_list}
        for token in self.tokenized_text:
            vectorized_data[token] += 1
        return vectorized_data

    def get_vector_representation(self, matrix_key_list):
        return list(self.bag_of_words(matrix_key_list).values())  # since memory restrictions dont allow
        #                                                           to vectorize them all at once

    def get_vector_representation_for_nb(self, matrix_key_list):
        dict = self.bag_of_words(matrix_key_list)
        # {"this":2, "hello":3}
        # for key in list.keys()
        ret_dict = {}
        for key in dict.keys():
            if dict[key] == 0:
                ret_dict[key] = False
            else:
                ret_dict[key] = True

        return ret_dict


def create_review_list_from_file(filename, language):
    if filename == None:
        return
    data = []
    lang_filename = filename
    if language == "english":
        lang_filename = filename + "_en"
    elif language == "german":
        lang_filename = filename + "_de"

    with open(lang_filename, "r", encoding="utf-8") as readFile:
        lines = readFile.readlines()
        for line in lines:
            data.append(Review(line[0], line[2:], language=language))

    return data


class RunData:

    def __init__(self, data_picker: K_fold_style_data_picker, combinations_num, languages=None):
        """

        :param data_picker: The data picker employed
        :param combinations_num: the number of combinations, usually that would be k
        :param languages: a dict that has the language a given dataset is in, where the key is the datasets name.
        This dataset and the corresponding name is handed over within the data picker.
        """

        if languages is None:
            languages = {"german": "german", "english": "english"}
            # later ["german":"german", "english":"english", "original_german":"german", "original_english":"english"]

        self.languages = languages
        self.k = combinations_num

        # self.gen = gen

        # gen.create_training_validation_test_files()

        # returns: learn_test_lists_dict = {lang: [[[] for learn_and_test in range(0, 2)]
        #                                         for k in range(0, len(tuple_list))]
        #                                  for lang in line_dict.keys()}
        self.file_reader = data_picker

        # self.training_data_reviews = {x: [learn_test_list_dict[x][i][0] for i in range(0, k)] for x in languages.keys()}
        # self.test_data_reviews = {x: [learn_test_list_dict[x][i][1] for i in range(0, k)] for x in languages.keys()}

        self.current_language_type_accessed = None
        self.current_language_type_data = ([], [])
        self.bow_matrix = [[] for i in range(0, combinations_num)]

    def __access_training_data_reviews(self, language):
        self.__access_data_reviews(language)
        return self.current_language_type_data[0]

    def __access_test_data_reviews(self, language):
        self.__access_data_reviews(language)
        return self.current_language_type_data[1]

    def load_data_reviews(self, language):
        self.__access_data_reviews(language)

    def __access_data_reviews(self, language):
        if self.current_language_type_accessed is None or self.current_language_type_accessed != language:
            util.time_log("vectorizing for " + language + " ...")
            self.current_language_type_accessed = language
            learn_test_tuple = self.file_reader.create_training_test_reviews(self.languages, language)
            self.k = len(learn_test_tuple)
            self.current_language_type_data = (
                [learn_test_tuple[i][0] for i in
                 range(0, self.k)],
                [learn_test_tuple[i][1] for i in
                 range(0, self.k)])
            self.__create_bow_matrix(language)
            # self.__vectorize_reviews_with_bow(language)
            util.time_log("done vectorizing...")

    def training_data_text(self, language, k_iter):
        self.__check_language(language)
        return [x.text for x in self.__access_training_data_reviews(language)[k_iter]]

    def test_data_text(self, language, k_iter):
        self.__check_language(language)
        return [x.text for x in self.__access_test_data_reviews(language)[k_iter]]

    def training_data_text_tokenized(self, language, k_iter):
        self.__check_language(language)
        return [x.tokenized_text for x in self.__access_training_data_reviews(language)[k_iter]]

    def test_data_text_tokenized(self, language, k_iter):
        self.__check_language(language)
        return [x.tokenized_text for x in self.__access_test_data_reviews(language)[k_iter]]

    def training_data_rating(self, language, k_iter):
        self.__check_language(language)
        return [x.rating for x in self.__access_training_data_reviews(language)[k_iter]]

    def test_data_rating(self, language, k_iter):
        self.__check_language(language)
        return [x.rating for x in self.__access_test_data_reviews(language)[k_iter]]

    def __create_bow_matrix(self, language):
        for i in range(0, self.k):
            matrix_key_list = []
            for sent in self.training_data_text_tokenized(language, i) + self.test_data_text_tokenized(language, i):
                for token in sent:
                    if token not in matrix_key_list:
                        matrix_key_list.append(token)
            self.bow_matrix[i] = matrix_key_list

    def bow_size(self, language, k_iter):
        self.__check_language(language)
        return len(self.bow_matrix[k_iter])

    def __vectorize_reviews_with_bow(self, language):
        for i in range(0, self.k):
            for entry in self.__access_training_data_reviews(language)[i] + \
                         self.__access_test_data_reviews(language)[i]:
                entry.bag_of_words(self.bow_matrix[i])

    def training_data_text_vectorized_bow(self, language, k_iter):
        self.__check_language(language)
        return [x.get_vector_representation(self.bow_matrix[k_iter]) for x in
                self.__access_training_data_reviews(language)[k_iter]]

    def test_data_text_vectorized_bow(self, language, k_iter):
        self.__check_language(language)
        return [x.get_vector_representation(self.bow_matrix[k_iter]) for x in
                self.__access_test_data_reviews(language)[k_iter]]

    def training_data_text_vectorized_nb(self, language, k_iter):
        self.__check_language(language)
        return [(x.get_vector_representation_for_nb(self.bow_matrix[k_iter]), x.rating) for x in
                self.__access_training_data_reviews(language)[k_iter]]

    def test_data_text_vectorized_nb(self, language, k_iter):
        self.__check_language(language)
        return [x.get_vector_representation_for_nb(self.bow_matrix[k_iter]) for x in
                self.__access_test_data_reviews(language)[k_iter]]

    def run_svm(self, language):
        self.__check_language(language)
        util.time_log("starting svm...")
        ret_list = []
        self.load_data_reviews(language)
        for k_iter in range(0, self.k):
            classifier = svm.SVC(kernel="linear")
            util.time_log("learning...")
            vectorized = self.training_data_text_vectorized_bow(language, k_iter)
            classifier.fit(vectorized, self.training_data_rating(language, k_iter))
            util.time_log("classifying")
            ret_list.append(classifier.predict(self.test_data_text_vectorized_bow(language, k_iter)))
            #print(language + "," + str(k_iter) +": " + str(self.bow_size(language, k_iter)))
        return ret_list

    def run_naive_bayes(self, language):
        self.__check_language(language)
        util.time_log("starting nb...")
        ret_list = []
        self.load_data_reviews(language)
        for k_iter in range(0, self.k):
            util.time_log("learning...")
            classifier = NaiveBayesClassifier.train(self.training_data_text_vectorized_nb(language, k_iter))
            util.time_log("classifying")
            ret_list.append([classifier.classify(x) for x in self.test_data_text_vectorized_nb(language, k_iter)])
        return ret_list

    def run_polyglot(self, language):
        self.__check_language(language)
        util.time_log("starting polyglot...")
        lang_code = "en" if self.languages[language] == "english" else "de"

        ret_list = []

        for k_iter in range(0, self.k):
            if self.languages[language] == "english":
                ret_list.append([1 if Text(x, lang_code).polarity > 0 else 0 for x in
                                 self.test_data_text(language, k_iter)])
            else:
                ret_list.append([1 if Text(x, lang_code).polarity >= 0 else 0 for x in
                                 self.test_data_text(language, k_iter)])
        return ret_list

    def run_textblob(self, language):
        self.__check_language(language)
        util.time_log("starting textblob...")
        ret_list = []
        for k_iter in range(0, self.k):
            if self.languages[language] == "english":
                ret_list.append(
                    [1 if TextBlob_EN(w).polarity > 0 else 0 for w in self.test_data_text(language, k_iter)])
            else:
                ret_list.append(
                    [1 if TextBlob_DE(w).polarity > 0 else 0 for w in self.test_data_text(language, k_iter)])
        return ret_list

    def run_vader(self, language):
        self.__check_language(language)
        util.time_log("starting VADER...")

        ret_list = []

        for k_iter in range(0, self.k):
            if self.languages[language] == "english":
                classifier = Vader_EN()
                ret_list.append([1 if classifier.polarity_scores(w)["compound"] >= 0 else 0 for w in
                                 self.test_data_text(language, k_iter)])
            else:
                classifier = Vader_DE()
                ret_list.append([1 if classifier.polarity_scores(w)["compound"] >= 0 else 0 for w in
                                 self.test_data_text(language, k_iter)])
        return ret_list

    def run_nlp(self, language):
        # Make sure server is running properly (as explained in https://github.com/nltk/nltk/wiki/Stanford-CoreNLP-API-in-NLTK) :
        # might need root
        # english: java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -preload tokenize,ssplit,pos,lemma,ner,parse,depparse,sentiment -status_port 9000 -port 9000 -timeout 15000
        # the german implementation cannot do sentiment analysis, the predictions do not bear any relevance, keeping the code like that just makes it easier to maybe add seom sentiment analysis of the parsed german text in the future
        # if the service times out increasing the timeout helps. This usually happens when a sentence is too long to be handled within the given period.
        self.__check_language(language)
        util.time_log("starting NLP...")
        annotator_dict = {"annotators": "sentiment"}
        classifier = CoreNLPParser("http://localhost:9000")

        ret_list = []

        for k_iter in range(0, self.k):
            prediction = []
            for review in self.test_data_text(language, k_iter):
                response_dict = classifier.api_call(review, properties=annotator_dict, timeout=500)
                count = 0
                sentiment = 0.0
                for sentence in response_dict["sentences"]:
                    count += 1
                    sentiment += float(sentence["sentimentValue"])

                avg_sentiment = sentiment / count
                # a lot better results with >=2
                prediction.append(1 if avg_sentiment >= 2 else 0)
            ret_list.append(prediction)
        return ret_list

    def __check_language(self, language):
        if language not in self.languages:
            raise ValueError


if __name__ == '__main__':
    util.time_log("starting...")

    fileNamesGerman = ["../reviews/1-star.txt", "../reviews/2-star.txt", "../reviews/4-star.txt",
                       "../reviews/5-star.txt"]
    fileNamesEnglish = ["../reviews/1-star_en_mapped.txt", "../reviews/2-star_en_mapped.txt",
                        "../reviews/4-star_en_mapped.txt", "../reviews/5-star_en_mapped.txt"]
    fileNamesGermanOriginal = ["../reviews/original/1-star.txt", "../reviews/original/2-star.txt",
                               "../reviews/original/4-star.txt",
                               "../reviews/original/5-star.txt"]
    fileNamesEnglishOriginal = ["../reviews/original/1-star_translated_mapped.txt",
                                "../reviews/original/2-star_translated_mapped.txt",
                                "../reviews/original/4-star_translated_mapped.txt",
                                "../reviews/original/5-star_translated_mapped.txt"]

    k = 20  # 20 so we get 200 per test_set

    # run_data_dict = {"original_german": fileNamesGermanOriginal,
    #                 "original_english": fileNamesEnglishOriginal,
    #                 "german": fileNamesGerman,
    #                 "english": fileNamesEnglish}  # later + "original_german":fileNamesGermanOriginal, ...
    # languages_dict = {"original_german": "german",
    #                  "original_english": "english",
    #                  "german": "german",
    #                  "english": "english"}

    run_data_dict = {"original_german": fileNamesGermanOriginal,
                     "original_english": fileNamesEnglishOriginal,
                     "german": fileNamesGerman,
                     "english": fileNamesEnglish}  # later + "original_german":fileNamesGermanOriginal, ...
    languages_dict = {"original_german": "german",
                      "original_english": "english",
                      "german": "german",
                      "english": "english"}

    run_configurations = RunConfiguration.generate_run_configs(run_data_dict.keys())
    run_configs_f1_composite = {x: [] for x in run_configurations}

    run_data = RunData(K_fold_data_picker_mixed(k, K_fold_parallel_file_reader(
        run_data_dict)), k, languages=languages_dict)

    for run_configuration in run_configurations:
        prediction = []
        if run_configuration.implementation == "svm":
            prediction = run_data.run_svm(run_configuration.run_name)
        elif run_configuration.implementation == "nb":
            prediction = run_data.run_naive_bayes(run_configuration.run_name)
        elif run_configuration.implementation == "polyglot":
            prediction = run_data.run_polyglot(run_configuration.run_name)
        elif run_configuration.implementation == "textblob":
            prediction = run_data.run_textblob(run_configuration.run_name)
        elif run_configuration.implementation == "vader":
            prediction = run_data.run_vader(run_configuration.run_name)
        elif run_configuration.implementation == "nlp":
            prediction = run_data.run_nlp(run_configuration.run_name)

        f1_composite_list = []

        for k_iter in range(0, k):
            f1_composite_list.append(
                F1Composite(run_data.test_data_rating(run_configuration.run_name, k_iter), prediction[k_iter]))

        run_configs_f1_composite[run_configuration] = f1_composite_list

    for key in run_configs_f1_composite.keys():
        f1_composite_lists_list = run_configs_f1_composite[key]
        f1_list = [x.f1 for x in f1_composite_lists_list]
        prec_list = [x.precision for x in f1_composite_lists_list]
        rec_list = [x.recall for x in f1_composite_lists_list]
        acc_list = [x.accuracy for x in f1_composite_lists_list]

        key.print()
        print("accuracy-average: " + str(sum(acc_list) / k))
        print("accuracy-median: " + str(median(acc_list)))
        print("accuracy-min: " + str(min(acc_list)))
        print("accuracy-max: " + str(max(acc_list)))

        print("#######################################################")
