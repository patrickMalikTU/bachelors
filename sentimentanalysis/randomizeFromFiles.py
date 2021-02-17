import copy
import random
import util

from abc import ABC, abstractmethod
from deprecated import deprecated


class K_fold_file_reader(ABC):

    @abstractmethod
    def read_files(self):
        pass


class K_fold_parallel_file_reader(K_fold_file_reader):
    def __init__(self, filename_dict: dict):
        """
           :param filename_dict: a list of filenames split after language and stars e.g.:
               {"german" : [1-star-german, 2-star-german, 4-star-german, 5-star-german],
                "english": [1-star-english, 2-star-english, ...],
                "original_english" : ...
               }
        """
        self.filename_dict = filename_dict

    def read_files(self):
        ret_dict = {j: [[] for i in range(0, 4)] for j in self.filename_dict.keys()}

        for filename in self.filename_dict.keys():  # looping through language types
            for j in range(0, 4):  # looping through categories
                with open(self.filename_dict[filename][j], "r", encoding="utf-8") as readFile:
                    ret_dict[filename][j] = readFile.readlines()

        return ret_dict


class K_fold_composite_file_reader(K_fold_file_reader):
    def __init__(self, filename_dict: dict, composition_list, result_list_names: list):
        """

        :param filename_dict: a list of filenames split after language type and stars e.g.:
               {"german" : [1-star-german, 2-star-german, 4-star-german, 5-star-german],
                "english": [1-star-english, 2-star-english, ...],
                "original_english" : ...
               }
        :param composition_list: a list of dictionaries where each contains the language types from the filename_dict
                (its keys) as keys and an absolute number as value. The absolute number represents how many entries
                from this particular language type should be in the newly created composite dictionary. For each
                dictionary a separate dict will be created when read_files() is being called. e.g.:

                    [{"german": 1500, "english": 500, "original_english":500, "original_german":300},
                    {"german": 2000, "english": 0, "original_english": 0, "original_german": 500}]

                    the first dict will create one return dict entry consistign of 1500 reviews from the german files,
                    500 from the english, etc.. the second dict will add another dict entry to the dictionary that will
                    be returned, this time with 2500 entries, 2000 of which are "german", whereas the other 500 are
                    "original_german". Every used absolute number has to be divisible by 4, since every category should
                    contain as many reviews as every other category.
        """
        self.filename_dict = filename_dict
        self.composition_list = composition_list
        self.result_list_names = result_list_names
        if len(result_list_names) != len(composition_list):
            raise ValueError()
        for comp_dict in composition_list:
            for key in comp_dict.keys():
                if comp_dict[key] % 4 != 0:
                    raise ValueError()

    def read_files(self):
        ret_dict = {name: [[] for _ in range(0, 4)] for name in self.result_list_names}

        file_holder_dict = {name: [[] for _ in range(0, 4)] for name in self.filename_dict.keys()}
        for filename in self.filename_dict.keys():  # looping through language types
            for j in range(0, 4):  # looping through categories
                with open(self.filename_dict[filename][j], "r", encoding="utf-8") as readFile:
                    file_holder_dict[filename][j] = readFile.readlines()

        for name_index in range(0, len(self.result_list_names)):
            curr_dict = self.composition_list[name_index]
            for key in curr_dict.keys():
                curr_file_copy = copy.deepcopy(
                    file_holder_dict[key])  # copies the category lists of the current contents
                curr_len = sum([len(curr_file_copy[i]) for i in range(0, 4)])
                while curr_len > curr_dict[key]:
                    for cat in range(0, 4):
                        del_index = random.randint(0, len(curr_file_copy[cat]) - 1)
                        del curr_file_copy[cat][del_index]
                    curr_len = sum([len(curr_file_copy[i]) for i in range(0, 4)])
                for i in range(0, 4):
                    ret_dict[self.result_list_names[name_index]][i] += curr_file_copy[i]

        return ret_dict


class K_fold_list_generator():
    def generate_list_of_index_tuples(self, input_data_child_length, k):
        """

        :param input_data: Is expected to have 4 sets of text reviews, ordered like [[1-stars,...],[2-stars, ...],...]
        :param test_size: absolute size of the expected test_set
        :param learn_size: absolute size of the expected learn_set
        :return: a list of tuples of lists for the indices of learn and test_set, which too are tuples. e.g.:
                 learn_set_1                  test_set_1             learn_set_2                 test_set_2
             [([(1,3), (3,2), (2,2), (0,1)], [(1,2), (0,2), ...]), ([(1,2), (3,2), (2,2), (0,2)], [(3,2), (2,2), ...]), ...]
             where the index_tuples represent the list as follows:
                 (list_index = star_rating , index within that list)
                 (1, 3) --> in the list of 2-star-reviews, the review with index 3, so the 4th review
        """
        test_size = round((input_data_child_length * 4) / k)
        test_items_per_category = round(test_size / 4)

        tuple_index_list = [[(i, j) for j in range(0, input_data_child_length)] for i in range(0, 4)]
        k_tuple_index_list = [list(tuple_index_list) for i in range(0, k)]
        k_ret_list = [([], []) for i in range(0, k)]

        # first generate test for all
        for i in range(0, k):
            test_items_per_category_list = [0, 0, 0, 0]
            for j in range(0, test_size):
                rand_category = self.__pick_random_category(test_items_per_category_list, test_items_per_category)
                rand_index = random.randint(0, len(k_tuple_index_list[i][rand_category]) - 1)
                k_ret_list[i][1].append(
                    k_tuple_index_list[i][rand_category][rand_index])  # add it as test to the one list we want it in
                for f in range(0, k):
                    if f == i:
                        continue
                    k_ret_list[f][0].append(
                        k_tuple_index_list[i][rand_category][rand_index])  # add it as learn in all the other lists
                del k_tuple_index_list[i][rand_category][rand_index]

        # randomize test and learn
        for i in range(0, k):
            random.shuffle(k_ret_list[i][0])  # shuffle learn
            random.shuffle(k_ret_list[i][1])  # shuffle test

        return k_ret_list

    def __pick_random_category(self, categories_picked, items_per_category):
        while True:
            randCategory = random.randint(0, 3)
            if categories_picked[randCategory] < items_per_category:
                categories_picked[randCategory] += 1
                return randCategory


class K_fold_style_data_picker(ABC):

    @abstractmethod
    def create_training_test_reviews(self, languages_dict: dict, run_name):
        pass


class K_fold_data_picker_mixed(K_fold_style_data_picker):

    def __init__(self, k, file_reader: K_fold_file_reader):
        self.index_gen = K_fold_list_generator()
        self.file_reader = file_reader
        self.line_dict = self.file_reader.read_files()
        size = len(self.line_dict[list(self.line_dict.keys())[0]][0])
        self.tuple_list = self.index_gen.generate_list_of_index_tuples(size, k)

    def create_training_test_reviews(self, languages_dict: dict, run_name):
        return self.__tuple_line_lists_to_learn_test_lists(languages_dict, run_name)

    def __tuple_line_lists_to_learn_test_lists(self, languages_dict, run_name):
        from standard_run import Review  # circular dep

        learn_test_list = [[[] for learn_and_test in range(0, 2)]
                           for k in range(0, len(self.tuple_list))]
        for k in range(0, len(self.tuple_list)):
            for learn_and_test in range(0, 2):  # iterating through learn and test
                for cat, index in self.tuple_list[k][learn_and_test]:
                    learn_test_list[k][learn_and_test].append(
                        Review(self.__fix_category(cat), self.line_dict[run_name][cat][index],
                               language=languages_dict[run_name]))
        return learn_test_list

    def __fix_category(self, category):
        category = category + 1
        if category >= 3:
            category += 1
        return category


class K_fold_style_data_picker_specific_tests_on_base(K_fold_style_data_picker):

    def __init__(self, base_file_names: list, base_file_language, test_file_names: list,
                 test_file_language, partitions, base_composition_list, base_composition_names):  # TODO

        self.base_file_language = base_file_language
        self.test_file_language = test_file_language

        # start generating by k-folding the test_file and getting the partitions, as reviews
        self.test_partitions_reviews = [x[1] for x in K_fold_data_picker_mixed(partitions, K_fold_parallel_file_reader(
            {"test_data": test_file_names})).create_training_test_reviews({"test_data": test_file_language},
                                                                          "test_data")]

        test_partitions_index_choice = [x for x in range(0, partitions)]
        partition_combination_indices = [([x for x in test_partitions_index_choice if x != test], test) for test in
                                         test_partitions_index_choice]

        self.base_lines = K_fold_composite_file_reader({"base_data": base_file_names},
                                                       [{"base_data": line_count} for line_count in
                                                        base_composition_list],
                                                       base_composition_names).read_files()

        base_index_choice = [x for x in range(0, len(self.base_lines))]

        # the following are the 3 cases discussed in "transfer_run.py", all are structured like follows:
        # (learn_list, test_index)
        # learn_list = [base_index, [test-indices]]
        # e.g. -> ([0, [1,2,3]] ,0) =>  0 = index of base_data
        #                               [1,2,3] = indices of test_data thats not being used for testing
        #                               0 = index of test_data
        base_only_tests = [([base, []], test[1]) for base in base_index_choice for test in
                           partition_combination_indices]
        base_plus_1k = [([base, [test_learn]], test[1]) for base in base_index_choice for test in
                        partition_combination_indices for test_learn in test[0]]
        base_plus_3k = [([base, [x for x in test[0]]], test[1]) for base in base_index_choice for test in
                        partition_combination_indices]

        # splitting for bases, so only one has to be in memory and not always revectorized
        self.index_tuples_split_by_base = {base_composition_names[i]: [tup for tup in base_only_tests if tup[0][0] == i]
                                                                      + [tup for tup in base_plus_1k if tup[0][0] == i]
                                                                      + [tup for tup in base_plus_3k if tup[0][0] == i]
                                           for i in range(0, len(base_composition_names))}

    def create_training_test_reviews(self, languages_dict: dict, run_name):
        """
        
        :param languages_dict: irrelevant, only there for compatibility, might be changed
        :param run_name: 
        :return: 
        """
        return self.__tuple_line_lists_to_learn_test_lists(languages_dict, run_name)

    def __tuple_line_lists_to_learn_test_lists(self, languages_dict, run_name):
        from standard_run import Review  # circular dep
        # self.base_lines e.g.: 2k, 4k and 6k accessible through a dict, run_name is in keys
        # self.index_tuples_split_by_base, also accessible through run_name, ([base_index, [learn_trans_ind, ...]], test)
        # should return a list of lists that contain learn and test_data

        learn_test_list = [[[] for learn_and_test in range(0, 2)]
                           for k in range(0, len(self.index_tuples_split_by_base[run_name]))]

        index = 0
        for learn_comp, test_ind in self.index_tuples_split_by_base[
            run_name]:  # rn should be 20, learn_comp == run_name but as name, not index
            learn_test_list[index][1] = self.test_partitions_reviews[test_ind]
            learn_part = []
            learn_part += [y for x in learn_comp[1] for y in
                           self.test_partitions_reviews[x]]  # adds the lists of partitions together

            base_as_reviews = [Review(self.__fix_category(cat), x, language=self.base_file_language) for cat in
                               range(0, 4) for x in self.base_lines[run_name][cat]]
            learn_test_list[index][0] = base_as_reviews + learn_part

            random.shuffle(learn_test_list[index][0])
            random.shuffle(learn_test_list[index][1])

            index += 1

        return learn_test_list

    def __fix_category(self, category):
        category = category + 1
        if category >= 3:
            category += 1
        return category


""" 


Following classes were what was being used in the first place, before introducing k-fold-cross-validation.
Since there are better alternatives implemented, those classes are now deprecated.


"""


@deprecated()
class FileReader(ABC):

    @staticmethod
    def fix_category(category):
        category = category + 1
        if category >= 3:
            category += 1
        return category

    def pick_category(self, file_count, line_count):
        while True:
            randCategory = random.randint(0, 3)
            if self.categoriesPicked[randCategory] < (line_count / file_count):
                self.categoriesPicked[randCategory] += 1
                return randCategory

    @abstractmethod
    def create_training_validation_test_files(self):
        pass


@deprecated()
class ParallelCorpusFileReader(FileReader):

    def __init__(self, train_count, test_count, german_file_names, english_file_names):
        super().__init__()
        self.train_count = train_count
        self.test_count = test_count
        self.german_file_names = german_file_names
        self.english_file_names = english_file_names
        self.linesGerman = self.linesEnglish = []

    def __write_lines_to_files(self, filename, german_lines, english_lines):
        with open(filename + "_de", "w", encoding="utf-8") as germanTrainingFile:
            germanTrainingFile.writelines(german_lines)
        with open(filename + "_en", "w", encoding="utf-8") as englishTrainingFile:
            englishTrainingFile.writelines(english_lines)

    def __read_parallel_files_to_lists(self, german_file_names, english_file_names):
        german_lines = []
        english_lines = []
        for i in range(0, len(german_file_names)):
            german_file = open(german_file_names[i], "r", encoding="utf-8")
            english_file = open(english_file_names[i], "r", encoding="utf-8")
            german_lines.append(german_file.readlines())
            english_lines.append(english_file.readlines())
            german_file.close()
            english_file.close()

        return german_lines, english_lines

    def __pick_and_delete_random_lines_in_ratio(self, count, file_count):
        self.categoriesPicked = [0, 0, 0, 0]

        lines_to_write_german = []
        lines_to_write_english = []

        for i in range(0, count):
            raw_category = self.pick_category(file_count, count)
            randIndex = random.randint(0, len(self.linesGerman[raw_category]) - 1)
            category = self.fix_category(raw_category)
            lines_to_write_german.append(str(category) + "," + self.linesGerman[raw_category][randIndex])
            lines_to_write_english.append(str(category) + "," + self.linesEnglish[raw_category][randIndex])
            del self.linesGerman[raw_category][randIndex]
            del self.linesEnglish[raw_category][randIndex]

        return lines_to_write_german, lines_to_write_english

    def __create_data_files(self, count, file_name):
        self.linesGerman, self.linesEnglish = self.__read_parallel_files_to_lists(self.german_file_names,
                                                                                  self.english_file_names)
        linesToWriteGerman, linesToWriteEnglish = self.__pick_and_delete_random_lines_in_ratio(count,
                                                                                               len(
                                                                                                   self.german_file_names))
        self.__write_lines_to_files(file_name, linesToWriteGerman, linesToWriteEnglish)

    def create_training_validation_test_files(self):
        if self.train_count > 0:
            self.__create_data_files(self.train_count, util.RunConfiguration.training_file_name_base)
        if self.test_count > 0:
            self.__create_data_files(self.test_count, util.RunConfiguration.test_file_name_base)


@deprecated()
class CompositeFileReader(FileReader):

    def __init__(self, train_count_list, test_count_list, file_names):
        """
        Creates a filereader that creates files out of the contents of the inputfiles. Via the params one can specify
        how many lines from the various files should be taken to make up training and test file. This does only produce
        files in one language.

        :param train_count_list: a list of absolute numbers that specifies how many lines are taken from which file to
        create the train-file. A list: [10,20,30] would take 10 lines from the first file in the file_names list, 20
        from the second, etc.
        :param test_count_list: like train_count_list but for the test_file
        :param file_names: a list of file_names that are accessed to make up the training- and testfiles. roughly looking like:
        [[file_type_a_1-star,file_type_b_1-star],[ file_type_a_2-star, file_type_b_2-star], ...]]
        """
        super().__init__()
        self.train_count_list = train_count_list
        self.test_count_list = test_count_list
        self.file_names = file_names

        if not len(train_count_list) == len(test_count_list) or not len(train_count_list) == len(file_names):
            raise ValueError

    def create_training_validation_test_files(self):
        file_contents = self.__read_files_to_list()
        train_list = []
        test_list = []
        for i in range(0, len(self.file_names)):
            self.categoriesPicked = [0, 0, 0, 0]
            for j in range(0, self.train_count_list[i]):
                train_list.extend(
                    self.__create_radomized_list_from_input_lists(file_contents, i, self.train_count_list[i]))

            self.categoriesPicked = [0, 0, 0, 0]
            for j in range(0, self.test_count_list[i]):
                test_list.extend(
                    self.__create_radomized_list_from_input_lists(file_contents, i, self.test_count_list[i]))

        self.__write_lines_to_files(train_list, test_list)

    def __create_radomized_list_from_input_lists(self, input_file_contents, index, length):
        train_list_part = []
        raw_cat = self.pick_category(len(self.file_names[0]), length)
        rand_index = random.randint(0, len(input_file_contents[raw_cat][index]) - 1)
        category = self.fix_category(raw_cat)
        train_list_part.append(str(category) + "," + input_file_contents[raw_cat][index][rand_index])
        del input_file_contents[raw_cat][index][rand_index]
        return train_list_part

    def __read_files_to_list(self):
        ret_list = [[], [], [], []]
        for file_name_stars in self.file_names:
            for i in range(0, 4):
                with open(file_name_stars[i], "r", encoding="utf-8") as read_file:
                    ret_list[i].append(read_file.readlines())

        return ret_list

    def __write_lines_to_files(self, training_lines, test_lines):
        with open(util.RunConfiguration.training_file_name_base + "_en", "w", encoding="utf-8") as write_file:
            write_file.writelines(training_lines)

        with open(util.RunConfiguration.test_file_name_base + "_en", "w", encoding="utf-8") as write_file:
            write_file.writelines(test_lines)
