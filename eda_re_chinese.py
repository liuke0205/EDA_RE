#!/usr/bin/env python
# -*- coding: utf-8 -*-

import jieba
import synonyms
import random
from random import shuffle

random.seed(2021)

#停用词列表，默认使用哈工大停用词表
f = open('stopwords/hit_stopwords.txt', 'r', encoding='utf-8')
stop_words = list()
for stop_word in f.readlines():
    stop_words.append(stop_word[:-1])

#生成实体和类型的映射字典
entity_type = dict()
f = open('data/entity_type.txt', 'r', encoding='utf-8')
for data in f.readlines():
    data_list = data.split("\t")
    entity_type[data_list[0]] = data_list[1][0:-1]


# 计算阶乘
def func(n):
    if n <= 1:
        return 1
    else:
        return (n * func(n - 1))
'''
实体替换：：随机用若干个实体类型相同的实体替代已标数据中的实体
'''
def entity_replace(sentence, n, spo_list, entity_list):
    try:
        new_spo_list = spo_list.copy()
        augmented_sentence = sentence

        for _ in range(n):
            #随机选一个实体
            old_entity = random.choice(entity_list)
            random_entity_list = []
            #获取和old_entity实体类型相同的所有实体
            for key, value in entity_type.items():
                if value == entity_type[old_entity]:
                    random_entity_list.append(key)

            #随机从类型相同实体列表中选择一个实体
            new_entity = random.choice(random_entity_list)

            #更新sentence
            augmented_sentence = augmented_sentence.replace(old_entity, new_entity)

            #更新spo_list
            for spo in new_spo_list:
                if spo[0] == old_entity:
                    new_spo_list[new_spo_list.index(spo)] = [new_entity, spo[1], spo[2], spo[3], spo[4]]
                elif old_entity == spo[2]:
                    new_spo_list[new_spo_list.index(spo)] = [spo[0], spo[1], new_entity, spo[3], spo[4]]

        return augmented_sentence, new_spo_list
    except:
        return "", []
'''
分句换位：随机交换同一个样本之间的两个分句
'''
def clause_transposition(sentence):
    try:
        clause_sentences = str(sentence).split("；")
        global random_idx_1, random_idx_2

        while True:
            random_idx_1 = random.randint(0, len(clause_sentences) - 1)
            random_idx_2 = random.randint(0, len(clause_sentences) - 1)
            if random_idx_1 != random_idx_2:
                break
        clause_sentences[random_idx_1], clause_sentences[random_idx_2] = clause_sentences[random_idx_2], clause_sentences[random_idx_1]

        new_clause_sentence = []
        # 去除原来分句中后面的；和。
        for sentence in clause_sentences:
            sentence = sentence.strip("；")
            sentence = sentence.strip("。")
            new_clause_sentence.append(sentence)

        return "；".join(new_clause_sentence) + "。"
    except:
        return ""
'''
顿号换位
'''
# def get_commd_idx(words):
#     idx_list = set()
#     for i in range(len(words)):
#         word = words[i]
#         if word == "、":
#             idx_list.add(i - 1)
#             idx_list.add(i + 1)
#     return list(idx_list)
#
# def commd_transposition(sentence):
#     words = sentence.split("、")
#     commd_idx_list = get_commd_idx(words)
#
#     global random_idx_1, random_idx_2
#     while True:
#         random_idx_1 = random.choice(commd_idx_list)
#         random_idx_2 = random.choice(commd_idx_list)
#         if random_idx_1 != random_idx_2:
#             break
#     words[random_idx_1], words[random_idx_2] = words[random_idx_2], words[random_idx_1]
#     return words

'''
短句生成
'''
def sentence_generation(sentence, n_sg, spo_list):
    try:
        global j, i
        spo = random.choice(spo_list)
        head_entity_idx = str(sentence).index(spo[0])
        tail_entity_idx = str(sentence).index(spo[2])
        start = min(head_entity_idx, tail_entity_idx)
        end = max(head_entity_idx + len(spo[0]), tail_entity_idx + len(spo[2]))
        for i in range(start, -1, -1):
            if sentence[i] in ['，', '。', '；', '!']:
                break
        for j in range(end, len(sentence), 1):
            if sentence[j] in ['，', '。', '；', '!']:
                break

        if i == 0:
            return sentence[i:j], [spo]
        else:
            return sentence[i+1:j], [spo]
    except:
        return "", []
'''
EDA函数
'''
def eda_re(sentence, spo_list, alpha_sr=0.1, alpha_ri=0.1, alpha_rs=0.1, p_rd=0.1, num_aug=4):
    seg_list = jieba.cut(sentence)
    seg_list = " ".join(seg_list)
    words = list(seg_list.split())
    num_words = len(words)

    augmented_sentences = []
    spo_lists = []

    entity_list = []
    for spo in spo_list:
        entity_list.append(spo[0])
        entity_list.append(spo[2])

    # 实体替换er
    num_new_per_technique = int(num_aug/4)+1
    n_er = max(1, int(alpha_ri * len(spo_list) * 2))
    for _ in range(num_new_per_technique):
        augmented_sentence, spo_list_new = entity_replace(sentence, n_er, spo_list, entity_list)
        if len(augmented_sentence) > 0 and len(spo_list_new) > 0:
            augmented_sentences.append(augmented_sentence)
            spo_lists.append(spo_list_new)

    # 分句换位ct
    cnt = str(sentence).count("；")
    num_new_clause_transposition = func(cnt + 1) - 1
    for _ in range(num_new_clause_transposition):
        augmented_sentence = clause_transposition(sentence)
        if len(augmented_sentence) > 0:
            augmented_sentences.append(augmented_sentence)
            spo_lists.append(spo_list)

    # 顿句换位ct
    # cnt = str(sentence).count("、")
    # num_new_commd_transposition = func(cnt - 1) - 1
    # print(num_new_commd_transposition)
    # print(words)
    # for _ in range(num_new_commd_transposition):
    #     augmented_sentence = commd_transposition(sentence)
    #     augmented_sentences.append(augmented_sentence)
    #     spo_lists.append(spo_list)

    # 短句生成 sg
    num_new_per_technique = int(num_aug / 4) + 1
    n_sg = max(1, len(spo_list))
    for _ in range(num_new_per_technique):
        augmented_sentence, spo_list_new = sentence_generation(sentence, n_sg, spo_list)
        if len(augmented_sentence) > 0 and len(spo_list_new) > 0:
            augmented_sentences.append(augmented_sentence)
            spo_lists.append(spo_list_new)


    # if num_aug >= 1:
    #     augmented_sentences = augmented_sentences[:num_aug]
    # else:
    #     keep_prob = num_aug / len(augmented_sentences)
    #     augmented_sentences = [s for s in augmented_sentences if random.uniform(0, 1) < keep_prob]
    print(len(augmented_sentences))
    print(len(spo_lists))

    # 对数据增强后的样本进行去重
    # sentence_set = set()
    # for _ in range(len(augmented_sentences)):
    #     augmented_sentence = augmented_sentences[_]
    #     spo_list = spo_lists[_]
    #     if augmented_sentence in sentence_set:
    #         spo_lists.remove(spo_list)
    #         augmented_sentences.remove(augmented_sentence)
    #     else:
    #         sentence_set.add(augmented_sentence)

    #返回增强的文本数据augmented_sentences和spo_lists
    return augmented_sentences, spo_lists