# EDA-RE
中文EDA实现。本工具是论文[《EDA: Easy Data Augmentation Techniques for Boosting Performance on Text Classification Tasks》](https://arxiv.org/abs/1901.11196)的中文版本实现。  
原作者虽给出了针对英文语料数据增强的代码实现，但不适合中文语料。我经过对原论文附上的代码的修改，现在推出这个适合中文语料的数据增强EDA的实现。
### 数据格式
    {
        "text": "《离开》是由张宇谱曲，演唱", 
        "spo_list": [
            {
                "predicate": "歌手", 
                "object_type": "人物", 
                "subject_type": "歌曲", 
                "object": "张宇", 
                "subject": "离开"
            }, 
            {
                "predicate": "作曲", 
                "object_type": "人物", 
                "subject_type": "歌曲", 
                "object": "张宇", 
                "subject": "离开"
            }
        ]
    }
    {
    ...
    }
    .
    .
    .

### 命令运行

    python augment.py --input=data/test.json --output=output/augmented.txt --num_aug=4 --alpha=0.1
    
input参数：需要进行增强的语料文件

output参数：输出文件

num_aug参数：每一条语料将增强的个数

alpha参数：每一条语料中改动的词所占的比例

### Chinese stopwords

| 词表名                         | 词表文件            |
| ------------------------------ | ------------------- |
| 中文停用词表                   | cn_stopwords.txt    |
| 哈工大停用词表                 | hit_stopwords.txt   |
| 百度停用词表                   | baidu_stopwords.txt |
| 四川大学机器智能实验室停用词库 | scu_stopwords.txt   |


### REFERENCES
- 原仓库：[eda_nlp](https://github.com/jasonwei20/eda_nlp)。感谢原作者的付出。Thanks to the author of the paper.
- 中文改写仓库：[eda_nlp_chinese](https://github.com/zhanlaoban/eda_nlp_for_Chinese)。感谢原作者的付出。Thanks to the author of the paper.

### Acknowledgments

- [jieba分词](https://github.com/fxsjy/jieba)
- [Synonyms](https://github.com/huyingxi/Synonyms)
- [stopwords](https://github.com/goto456/stopwords)

### 原论文阅读笔记  

[《EDA: Easy Data Augmentation Techniques for Boosting Performance on Text Classification Tasks》](https://arxiv.org/abs/1901.11196)


### 简介


在这篇论文中，作者提出所谓的EDA，即简单数据增强(easy data augmentation)，包括了四种方法：**同义词替换、随机插入、随机交换、随机删除**。作者使用了CNN和RNN分别在五种不同的文本分类任务中做了实验，实验表明，EDA提升了分类效果。作者也表示，平均情况下，仅使用50%的原始数据，再使用EDA进行数据增强，能取得和使用所有数据情况下训练得到的准确率。 