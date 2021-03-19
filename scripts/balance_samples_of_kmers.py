import random
import math
import argparse


# same as functions in deepsignal_plant/utils/process_utils.py ==========================
# for balancing kmer distri in training samples ===
def _count_kmers_of_feafile(feafile):
    kmer_count = {}
    kmers = set()
    with open(feafile, "r") as rf:
        for line in rf:
            words = line.strip().split("\t")
            kmer = words[6]
            if kmer not in kmers:
                kmers.add(kmer)
                kmer_count[kmer] = 0
            kmer_count[kmer] += 1
    return kmer_count


# for balancing kmer distri in training samples ===
def _get_kmer2ratio_n_totalline(kmer_count):
    total_cnt = sum(list(kmer_count.values()))
    kmer_ratios = dict()
    for kmer in kmer_count.keys():
        kmer_ratios[kmer] = float(kmer_count[kmer])/total_cnt
    return kmer_ratios, total_cnt


# for balancing kmer distri in training samples ===
def _get_kmer2lines(feafile):
    kmer2lines = {}
    kmers = set()
    with open(feafile, "r") as rf:
        lcnt = 0
        for line in rf:
            words = line.strip().split("\t")
            kmer = words[6]
            if kmer not in kmers:
                kmers.add(kmer)
                kmer2lines[kmer] = []
            kmer2lines[kmer].append(lcnt)
            lcnt += 1
    return kmer2lines


# for balancing kmer distri in training samples ===
def _rand_select_by_kmer_ratio(kmer2lines, kmer2ratios, totalline):
    selected_lines = []
    unratioed_kmers = set()
    cnts = 0
    for kmer in kmer2lines.keys():
        if kmer in kmer2ratios.keys():
            linenum = int(math.ceil(totalline * kmer2ratios[kmer]))
            lines = kmer2lines[kmer]
            if len(lines) <= linenum:
                selected_lines += lines
                cnts += (linenum - len(lines))
            else:
                selected_lines += random.sample(lines, linenum)
        else:
            unratioed_kmers.add(kmer)
    print("for {} common kmers, fill {} samples, "
          "{} samples that can't filled".format(len(kmer2lines.keys()) - len(unratioed_kmers),
                                                len(selected_lines),
                                                cnts))
    unfilled_cnt = totalline - len(selected_lines)
    print("totalline: {}, need to fill: {}".format(totalline, unfilled_cnt))
    if len(unratioed_kmers) > 0:
        minlinenum = int(math.ceil(float(unfilled_cnt)/len(unratioed_kmers)))
        cnts = 0
        for kmer in unratioed_kmers:
            lines = kmer2lines[kmer]
            if len(lines) <= minlinenum:
                selected_lines += lines
                cnts += len(lines)
            else:
                selected_lines += random.sample(lines, minlinenum)
                cnts += minlinenum
        print("extract {} samples from {} diff kmers".format(cnts, len(unratioed_kmers)))
    selected_lines = sorted(selected_lines)
    selected_lines = [-1] + selected_lines
    return selected_lines


# for balancing kmer distri in training samples ===
def _write_randsel_lines(feafile, wfile, seled_lines):
    wf = open(wfile, 'w')
    with open(feafile) as rf:
        for i in range(1, len(seled_lines)):
            chosen_line = ''
            for j in range(0, seled_lines[i] - seled_lines[i - 1]):
                # print(j)
                chosen_line = next(rf)
            wf.write(chosen_line)
    wf.close()
    print('_write_randsel_lines finished..')


# balance kmer distri in neg_training file as pos_training file
def select_negsamples_asposkmer(pos_file, totalneg_file, seled_neg_file):
    kmer_count = _count_kmers_of_feafile(pos_file)
    kmer2ratio, totalline = _get_kmer2ratio_n_totalline(kmer_count)

    print("{} kmers from kmer2ratio file:{}".format(len(kmer2ratio), pos_file))
    kmer2lines = _get_kmer2lines(totalneg_file)
    sel_lines = _rand_select_by_kmer_ratio(kmer2lines, kmer2ratio, totalline)
    _write_randsel_lines(totalneg_file, seled_neg_file, sel_lines)
# =======================================================================================


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--feafile", type=str, required=True, help="file in which the samples need to be balanced")
    parser.add_argument("--kmer_feafile", type=str, required=True, help="file where the kmer2samples be learned from")
    parser.add_argument("--wfile", type=str, required=True, help="filepath for saving new feafile containing balanced "
                                                                 "samples of --feafile")

    args = parser.parse_args()
    select_negsamples_asposkmer(args.kmer_feafile, args.feafile, args.wfile)


if __name__ == '__main__':
    main()