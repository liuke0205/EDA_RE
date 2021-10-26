#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json

from eda_re_chinese import eda_re


ap = argparse.ArgumentParser()
ap.add_argument("--input", required=True, type=str, help="原始数据的输入文件目录")
ap.add_argument("--output", required=False, type=str, help="增强数据后的输出文件目录")
ap.add_argument("--num_aug", required=False, type=int, help="每条原始语句增强的语句数")
ap.add_argument("--alpha", required=False, type=float, help="每条语句中将会被改变的单词数占比")
args = ap.parse_args()

# 输出文件
output = None
if args.output:
    output = args.output
else:
    from os.path import dirname, basename, join

    output = join(dirname(args.input), 'eda_re' + basename(args.input))

# 每个原始句子的增广句子数，默认是4个
num_aug = 4
if args.num_aug:
    num_aug = args.num_aug

# 每条语句中将会被改变的单词数占比
alpha = 0.1
if args.alpha is not None:
    alpha = args.alpha

def load_data(filename):
    """加载数据
    单条格式：{'text': text, 'spo_list': [(s, p, o), (s, p, o)...]}
    """
    D = []
    with open(filename, "r", encoding='utf-8') as f:
        for l in f:
            l = json.loads(l)
            D.append({
                "text": l["text"],
                "spo_list": [[spo["subject"], spo["predicate"], spo["object"]]
                             for spo in l["spo_list"]]
            })
    return D


def gen_eda(train_orig, output_file, alpha, num_aug):

    origin_data = load_data(train_orig)
    writer = open(output_file, 'w', encoding='utf-8')
    for data in origin_data:
        sentence = data["text"]
        spo_list = data['spo_list']

        #aug_sentences 是一个list，每个元素是一个dict
        aug_sentences, spo_lists = eda_re(sentence, spo_list, alpha_sr=alpha, alpha_ri=alpha, alpha_rs=alpha, p_rd=alpha, num_aug=num_aug)
        print(aug_sentences)
        print(spo_lists)
        # for aug_sentence in aug_sentences:
        #     s = json.dumps(
        #         {
        #             "text": aug_sentence['text'],
        #             "spo_list": aug_sentence['spo_list']
        #         },
        #         ensure_ascii=False,
        #         indent=4
        #     )
        #     writer.write(s + "\n")
    writer.close()


if __name__ == "__main__":
    # generate augmented sentences and output into a new file
    gen_eda(args.input, output, alpha=alpha, num_aug=num_aug)