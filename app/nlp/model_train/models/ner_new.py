# 导入相应的包
import torch
import torch.autograd as autograd
import torch.nn as nn
import torch.optim as optim
from app.dataAPI.model_train import *

# 设置随机种子
torch.manual_seed(1)


# 返回vec中每一行最大的那个元素的下标
def argmax(vec):
    _, idx = torch.max(vec, 1)
    return idx.item()  # 注：tensor只有一个元素才能调用item方法


def prepare_sequence(seq, to_ix):  # 单词转为索引
    idxs = [to_ix[w] for w in seq]
    return torch.tensor(idxs, dtype=torch.long)


def log_sum_exp(vec):  # 计算一维向量vec与其最大值的log_sum_exp
    max_score = vec[0, argmax(vec)]
    max_score_broadcast = max_score.view(1, -1).expand(1, vec.size()[1])
    # 减去最大值是为了防止数值溢出
    return max_score + torch.log(torch.sum(torch.exp(vec - max_score_broadcast)))


# 读取训练语料
def read_corpus(corpus_path, vocab2idx, label2idx):
    datas, labels = [], []
    with open(corpus_path, encoding='utf-8') as fr:
        lines = fr.readlines()
    sent_, tag_ = [], []
    for line in lines:
        if line != '\n':
            [char, label] = line.strip().split()
            sent_.append(char)
            tag_.append(label)
        else:
            sent_ids = [vocab2idx[char] if char in vocab2idx else vocab2idx['<UNK>'] for char in sent_]
            tag_ids = [label2idx[label] if label in label2idx else 0 for label in tag_]
            datas.append(sent_ids)
            labels.append(tag_ids)
            sent_, tag_ = [], []
    return datas, labels


class BiLSTM_CRF(nn.Module):

    def __init__(self, vocab_size, tag_to_ix, embedding_dim, hidden_dim):
        super(BiLSTM_CRF, self).__init__()
        self.embedding_dim = embedding_dim  # 嵌入维度
        self.hidden_dim = hidden_dim  # 隐藏层维度
        self.vocab_size = vocab_size  # 词汇大小
        self.tag_to_ix = tag_to_ix  # 标签转为下标
        self.tagset_size = len(tag_to_ix)  # 目标取值范围大小

        self.word_embeds = nn.Embedding(vocab_size, embedding_dim)  # 嵌入层
        self.lstm = nn.LSTM(embedding_dim, hidden_dim // 2,
                            num_layers=1, bidirectional=True)  # 双向LSTM

        self.hidden2tag = nn.Linear(hidden_dim, self.tagset_size)  # LSTM的输出映射到标签空间

        # 转移矩阵的参数tag-->tag
        self.transitions = nn.Parameter(torch.randn(self.tagset_size, self.tagset_size))

        # 限制不能转移到start，end不能转移到其他
        self.transitions.data[tag_to_ix[START_TAG], :] = -10000
        self.transitions.data[:, tag_to_ix[STOP_TAG]] = -10000

        self.hidden = self.init_hidden()  # 初始化隐藏层参数

    def init_hidden(self):
        return (torch.randn(2, 1, self.hidden_dim // 2),
                torch.randn(2, 1, self.hidden_dim // 2))

    def _forward_alg(self, feats):  # 前向算法，feats是LSTM所有时间步的输出
        init_alphas = torch.full((1, self.tagset_size), -10000.)  # alpha初始为-10000
        init_alphas[0][self.tag_to_ix[START_TAG]] = 0.  # start位置的alpha为0

        forward_var = init_alphas  # 包装进forward_var变量，以便于自动反向传播

        for feat in feats:  # 对于每个时间步，进行前向计算
            alphas_t = []  # 当前时间步i的前向tensor
            for next_tag in range(self.tagset_size):  # next_tag有target_size个可能的取值
                # 无论之前的tag是什么，发射分数总是一样的
                emit_score = feat[next_tag].view(1, -1).expand(1, self.tagset_size)
                # 转换分数的第i项是从i转向next_tag的分数
                trans_score = self.transitions[next_tag].view(1, -1)
                # next_tag_var第i项的值是在做log-sum-exp之前的边（i-->next_tag）的值
                next_tag_var = forward_var + trans_score + emit_score
                # tag的前向变量就是所有分数的log-sum-exp
                alphas_t.append(log_sum_exp(next_tag_var).view(1))
            forward_var = torch.cat(alphas_t).view(1, -1)
        terminal_var = forward_var + self.transitions[self.tag_to_ix[STOP_TAG]]  # 添加stop_tag
        alpha = log_sum_exp(terminal_var)
        return alpha  # 每个时间步的得分（预测分数）

    def _get_lstm_features(self, sentence):  # LSTM的输出---即发射分数
        self.hidden = self.init_hidden()
        embeds = self.word_embeds(sentence).view(len(sentence), 1, -1)
        lstm_out, self.hidden = self.lstm(embeds, self.hidden)
        lstm_out = lstm_out.view(len(sentence), self.hidden_dim)
        lstm_feats = self.hidden2tag(lstm_out)
        return lstm_feats

    def _score_sentence(self, feats, tags):
        # 计算给定标签序列的分数---发射分数+转移分数（真实分数）
        score = torch.zeros(1)
        tags = torch.cat([torch.tensor([self.tag_to_ix[START_TAG]], dtype=torch.long), tags])
        for i, feat in enumerate(feats):
            score = score + self.transitions[tags[i + 1], tags[i]] + feat[tags[i + 1]]
        score = score + self.transitions[self.tag_to_ix[STOP_TAG], tags[-1]]
        return score

    def _viterbi_decode(self, feats):  # viterbi算法
        backpointers = []

        # 在log空间初始化维特比变量
        init_vvars = torch.full((1, self.tagset_size), -10000.)
        init_vvars[0][self.tag_to_ix[START_TAG]] = 0

        # 时间步i的forward_var拥有时间步i-1的维特比变量
        forward_var = init_vvars
        for feat in feats:  # 对于每个时间步
            bptrs_t = []  # 存放当前步的backpointer
            viterbivars_t = []  # 存放当前步的维特比变量

            for next_tag in range(self.tagset_size):
                # next_tag_var[i]包含之前时间步tag i的维特比变量和tag i 到next_tag的转移分数
                # 没有包含发射分数是因为最大值不取决于它（之后添加了它们）
                next_tag_var = forward_var + self.transitions[next_tag]
                best_tag_id = argmax(next_tag_var)
                bptrs_t.append(best_tag_id)
                viterbivars_t.append(next_tag_var[0][best_tag_id].view(1))
            # 现在添加发射分数，并将forward_var作为刚刚计算的维特比变量的集合
            forward_var = (torch.cat(viterbivars_t) + feat).view(1, -1)
            backpointers.append(bptrs_t)  # backpointer存放前一步最好的取值

        # 转移到STOP_TAG
        terminal_var = forward_var + self.transitions[self.tag_to_ix[STOP_TAG]]
        best_tag_id = argmax(terminal_var)
        path_score = terminal_var[0][best_tag_id]

        # 根据back pointers解码最好的路径
        best_path = [best_tag_id]
        for bptrs_t in reversed(backpointers):
            best_tag_id = bptrs_t[best_tag_id]
            best_path.append(best_tag_id)
        # 删除start tag
        start = best_path.pop()
        assert start == self.tag_to_ix[START_TAG]  # 断言检查
        best_path.reverse()
        return path_score, best_path

    def neg_log_likelihood(self, sentence, tags):
        feats = self._get_lstm_features(sentence)  # LSTM输出
        forward_score = self._forward_alg(feats)  # 前向计算分数
        gold_score = self._score_sentence(feats, tags)  # 真实分数
        # logP(y|x) = gold_score - forward_score，最大化logP(y|x)即最小化forward_score - gold_score
        return forward_score - gold_score

    def forward(self, sentence):  # 注：与上面的前向计算不同
        lstm_feats = self._get_lstm_features(sentence)  # 获得BiLSTM的发射分数
        score, tag_seq = self._viterbi_decode(lstm_feats)  # 给定特征，寻找最好的路径
        return score, tag_seq


START_TAG = "<START>"
STOP_TAG = "<STOP>"
EMBEDDING_DIM = 5
HIDDEN_DIM = 4


# 训练数据
# training_data = [(
#     "the wall street journal reported today that apple corporation made money".split(),
#     "B I I I O O O B I O O".split()
# ), (
#     "georgia tech is a university in georgia".split(),
#     "B I O O O O B".split()
# )]

# word_to_ix = {}
# for sentence, tags in training_data:
#     for word in sentence:
#         if word not in word_to_ix:
#             word_to_ix[word] = len(word_to_ix)


class TrainModel():
    def train(self):
        data = getAllData()
        special_words = ['<PAD>', '<UNK>']  # 特殊词表示
        tag_to_ix = {"O": 0,
                     "B-PER": 1, "I-PER": 2,
                     "B-LOC": 3, "I-LOC": 4,
                     "B-ORG": 5, "I-ORG": 6,
                     "<START>": 7, "<STOP>": 8
                     }

        # 读取字符词典文件
        with open(data['vocabs'], "r", encoding="utf8") as fo:
            char_vocabs = [line.strip() for line in fo]
        char_vocabs = special_words + char_vocabs

        # 字符和索引编号对应
        idx2vocab = {idx: char for idx, char in enumerate(char_vocabs)}
        word_to_ix = {char: idx for idx, char in idx2vocab.items()}
        train_datas, train_labels = read_corpus(data['feature'], word_to_ix, tag_to_ix)
        train_datas=train_datas[1:100]
        train_labels=train_labels[1:100]

        model = BiLSTM_CRF(len(word_to_ix), tag_to_ix, EMBEDDING_DIM, HIDDEN_DIM)  # 建立模型
        optimizer = optim.SGD(model.parameters(), lr=0.01, weight_decay=1e-4)  # SGD优化器


        # 检查训练之前的数据
        # with torch.no_grad():
        #     precheck_sent = prepare_sequence(training_data[0][0], word_to_ix)
        #     precheck_tags = torch.tensor([tag_to_ix[t] for t in training_data[0][1]], dtype=torch.long)
        #     print(model(precheck_sent))

        for epoch in range(300):  # 300epochs只是一个示例
            for i,sentence in enumerate(train_datas):
                # 梯度清零
                model.zero_grad()

                # 将数据转化为下标
                # sentence_in = prepare_sequence(sentence, word_to_ix)
                # targets = torch.tensor([tag_to_ix[t] for t in train_labels[i]], dtype=torch.long)

                # 前向传播
                loss = model.neg_log_likelihood(torch.tensor(sentence, dtype=torch.long), torch.tensor(train_labels[i],dtype=torch.long))

                # 反向传播，梯度更新
                loss.backward()
                optimizer.step()

        # 检查训练之后的数据
        with torch.no_grad():
            precheck_sent = torch.tensor(train_datas[3],dtype=torch.long)
            print(model(precheck_sent))

    def hyperparameters(self):
        return {}
