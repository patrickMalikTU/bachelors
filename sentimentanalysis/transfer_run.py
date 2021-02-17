from statistics import median

import util
from randomizeFromFiles import K_fold_data_picker_mixed, K_fold_style_data_picker_specific_tests_on_base, \
    K_fold_parallel_file_reader
from standard_run import RunData


def handle_f1_prints(f1_list):
    accuracy_list = [x.accuracy for x in f1_list]
    print("accuracy-average: " + str(sum(accuracy_list) / len(f1_list)))
    print("accuracy-median: " + str(median(accuracy_list)))
    print("accuracy-min: " + str(min(accuracy_list)))
    print("accuracy-max: " + str(max(accuracy_list)))


if __name__ == '__main__':
    util.time_log("starting...")

    filenames_originally_english = ["../reviews/originally_english/1_star_reviews_orig_english.txt",
                                    "../reviews/originally_english/2_star_reviews_orig_english.txt",
                                    "../reviews/originally_english/4_star_reviews_orig_english.txt",
                                    "../reviews/originally_english/5_star_reviews_orig_english.txt"]
    filenames_english_uncorrected = ["../reviews/original/1-star_translated_mapped.txt",
                                     "../reviews/original/2-star_translated_mapped.txt",
                                     "../reviews/original/4-star_translated_mapped.txt",
                                     "../reviews/original/5-star_translated_mapped.txt"]

    """
    2k, 4k and 6k as base relevant base learning data. In this case from the originally english set of data.
    A,B,C and D represent the partitions of the translated data. each partition is therefore 1k set of data.
    
    we want the translated data represented equally, so every relevant combination is created.
    case 1:
        only originally english learning data (2k, 4k and 6k) tested against every partition of the translated data
    case 2:
        all the native/originally english base options combined with 1k (one partition) of the translated data
        tested against every unused partition. e.g.:
            2k + A -> B, 2k + A -> C, 2k + A -> D, 2k + B -> A, ...
            4k + A -> B, ...
    case 3:
        all the native options + 3k of unused translated data tested against the 1k translated data. e.g.:
            2k + B + C + D -> A, 2k + A + C + D -> B, ...
            4k + B + C + D -> A. ...
        
    
    learning_native = ["2k", "4k", "6k"]
    test_partitions = ["A", "B", "C", "D"]
    partition_combinations = [([x for x in test_partitions if x != test], test) for test in test_partitions]
    base_only_tests = [(base, test[1]) for base in learning_native for test in partition_combinations]
    base_plus_1k = [(base + " " + test_learn, test[1]) for base in learning_native for test in partition_combinations
                    for test_learn in test[0]]
    base_plus_3k = [(base + " " + "".join([x for x in test[0]]), test[1]) for base in learning_native for test in
                    partition_combinations]
    print(len(base_only_tests) + len(base_plus_1k) + len(base_plus_3k))
    """

    #   run_data_dict = {"english_uncorrected": filenames_english_uncorrected,
    #                   "originally_english": filenames_originally_english}
    languages_dict = {"2k_base": "english",
                      "4k_base": "english",
                      "6k_base": "english"}

    run_configurations = util.RunConfiguration.generate_run_configs(languages_dict.keys())
    run_configs_f1_composite = {x: [] for x in run_configurations}

    partitions = 4

    run_data = RunData(
        K_fold_style_data_picker_specific_tests_on_base(filenames_originally_english, "english",
                                                        filenames_english_uncorrected, "english", partitions,
                                                        [2000, 4000, 6000], list(languages_dict.keys())),
        (2*partitions+(partitions*(partitions-1)))*len(languages_dict), languages_dict)

    for run_config in run_configurations:
        predictions = []
        if run_config.implementation == "svm":
            predictions = run_data.run_svm(run_config.run_name)
        if run_config.implementation == "nb":
            predictions = run_data.run_naive_bayes(run_config.run_name)
        run_config.print()
        i = 0
        print("base only")
        f1_list = []
        while i < partitions:
            f1_list.append(util.F1Composite(run_data.test_data_rating(run_config.run_name, i), predictions[i]))
            i += 1
        handle_f1_prints(f1_list)

        print("base plus 1")
        f1_list = []
        while i < partitions + (partitions * (partitions - 1)):
            f1_list.append(util.F1Composite(run_data.test_data_rating(run_config.run_name, i), predictions[i]))
            i += 1
        handle_f1_prints(f1_list)

        print("base plus (n-1)")
        f1_list = []
        while i < partitions + (partitions * (partitions - 1)) + partitions:
            f1_list.append(util.F1Composite(run_data.test_data_rating(run_config.run_name, i), predictions[i]))
            i += 1
        handle_f1_prints(f1_list)