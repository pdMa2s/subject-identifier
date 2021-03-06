import argparse
import re
from ImageFile import ImageFile
from NCD import NCD
from NCCD import NCCD
import os
from Subject import Subject
import matplotlib.pyplot as plt
import numpy as np
import Compressors


def is_directory(directory):
    if not os.path.isdir(directory):
        parser.error("The directory %s does not exist!" % directory)
    return directory


def create_refs_and_subjects(directory_in_str, compressor, compressor_type, nr_refs_files):
    refs = {}
    subjects = []
    general_directory = os.fsencode(directory_in_str)

    list_dir = os.listdir(general_directory)
    list_dir.sort()

    for dir in list_dir:
        dir_name = os.fsdecode(dir)
        sub_dir = os.path.join(directory_in_str, dir_name)
        if os.path.isdir(sub_dir):
            imgs = os.listdir(sub_dir)
            imgs.sort()
            image_files = []
            new_subject = Subject(dir_name)

            for i in imgs:
                img_dir = os.path.join(sub_dir, i)
                file = ImageFile(img_dir, compressor, compressor_type)
                if len(image_files) < nr_refs_files:
                    image_files.append(file)
                else:
                    new_subject.add_test_file(file)
            refs[dir_name] = image_files
            subjects.append(new_subject)
    return refs, subjects


def make_matrix_confusion(subjects, dic_min, ncd=False):
    matrix_confusion = [[0 for i in range(len(subjects))] for j in range(len(subjects))]
    for sub in subjects:
        if ncd:
            all_test_file_of_subject = [list_subject_min[0] for image, list_subject_min in dic_min.items()
                                    if image in sub.test_files]
        else:
            all_test_file_of_subject = dic_min[str(sub)]
        for candidate in all_test_file_of_subject:
            sub.add_candidate(candidate)
            subject_predicted_id = int(re.search(r'\d+', candidate).group())
            subject_real_id = int(re.search(r'\d+', sub.id_subject).group())
            matrix_confusion[subject_predicted_id - 1][subject_real_id - 1] += 1
    return matrix_confusion


def plot_matrix(matrix, header):
    H = np.array(matrix)
    fig = plt.figure(figsize=(10, 6), dpi=90)

    ax = fig.add_subplot(111)
    ax.set_title('confusion matrix' + header)
    plt.imshow(H)
    ax.set_aspect('equal')

    cax = fig.add_axes([0.12, 0.1, 0.78, 0.8])
    cax.get_xaxis().set_visible(False)
    cax.get_yaxis().set_visible(False)
    cax.patch.set_alpha(0)
    cax.set_frame_on(False)
    plt.colorbar(orientation='vertical')
    plt.show()


def calculate_metrics(matrix_confusion, subjects):
    total = sum([sum(f) for f in matrix_confusion])
    avg_accuracy = 0
    avg_recall = 0
    for i in range(len(subjects)):
        tp = matrix_confusion[i][i]
        fp = sum(matrix_confusion[i]) - tp
        fn = sum([d[0] for d in matrix_confusion]) - tp
        tn = total - (tp + fp + fn)
        accuracy_subject = ((tp + tn) / total) * 100
        recall_subject = (tp / (tp + fn)) * 100 if tp + fn != 0 else 0
        subjects[i].set_accuracy(accuracy_subject)
        subjects[i].set_recall(recall_subject)
        print(subjects[i].print_statistics())
        avg_accuracy += accuracy_subject
        avg_recall += recall_subject
    print("Average recall: " + str.format('%.2f' % float(avg_recall / len(subjects))) + "%")
    print("Average accuracy: " + str.format('%.2f' % float(avg_accuracy / len(subjects))) + "%\n")


def check_nr_ref_files(nr_refs):
    if nr_refs > 9 or nr_refs < 1:
        print("Invalid number of reference files!")
        exit(1)


def parse_args():
    parser.add_argument("directory", help="directory that contains the image files", type=is_directory)
    parser.add_argument("compressor", help="compressor to be used",
                        choices=['gzip', 'bzip2', 'lzma', 'zlib', 'jpeg', 'png'])
    parser.add_argument("-nr", "--nrReferenceFiles", help="number of reference files to be used", default=3)
    parser.add_argument("-sct", "--subjectClassificationType", help="type of subject classification to be used",
                            choices=['mean',"superImage"], default='mean')

    args = parser.parse_args()

    check_nr_ref_files(int(args.nrReferenceFiles))
    return args


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parse_args()
    compressor = Compressors.parse_compressor(args.compressor)
    nr_reference_files = int(args.nrReferenceFiles)
    classification_type = args.subjectClassificationType
    references, subjects = create_refs_and_subjects(args.directory, compressor, args.compressor, nr_reference_files)

    test_results = {}
    for ref in references:
        test_results[ref] = []
        for sub in subjects:
            means = NCD(sub.test_files, references[ref], compressor, args.compressor, classification_type).compute_ncd()
            test_results[ref] += means
    # print(test_results)

    dic_min = {}
    for subject, list_results in test_results.items():
        for image, ncd in list_results:
            if image in dic_min.keys():
                value = dic_min[image][1]
                if value > ncd:
                    dic_min[image] = (subject, ncd)
            else:
                dic_min[image] = (subject, ncd)
    #print(dic_min)

    print('NCD')
    print('Number of reference files:', args.nrReferenceFiles)
    matrix_confusion_ncd = make_matrix_confusion(subjects, dic_min, True)
    calculate_metrics(matrix_confusion_ncd, subjects)
    plot_matrix(matrix_confusion_ncd, "\nNCD")

    nccd = NCCD('results_NCCD.txt')
    print('NCCD')
    matrix_confusion_nccd = make_matrix_confusion(nccd.subjects, nccd.dict)
    calculate_metrics(matrix_confusion_nccd, nccd.subjects)
    plot_matrix(matrix_confusion_nccd, "\nNCCD")


