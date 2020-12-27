from app.dataAPI.model_train import *
from tensorflow.keras.preprocessing import sequence
from tensorflow.keras.models import Sequential
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Masking, Embedding, Bidirectional, LSTM, Dense, Input, TimeDistributed, Activation
from tensorflow.keras import backend as K
import tensorflow.compat.v1 as tf
import tensorflow.keras as keras
from tensorflow_addons.layers.crf import CRF
from tensorflow_addons.text.crf import crf_multitag_sequence_score
from tensorflow_addons.text.crf import crf_log_likelihood




class TrainModel():

    def train(self):
        data = getAllData()
        special_words = ['<PAD>', '<UNK>']  # 特殊词表示

        # "BIO"标记的标签
        label2idx = {"O": 0,
                     "B-PER": 1, "I-PER": 2,
                     "B-LOC": 3, "I-LOC": 4,
                     "B-ORG": 5, "I-ORG": 6
                     }
        # 索引和BIO标签对应
        idx2label = {idx: label for label, idx in label2idx.items()}

        # 读取字符词典文件
        with open(data['vocabs'], "r", encoding="utf8") as fo:
            char_vocabs = [line.strip() for line in fo]
        char_vocabs = special_words + char_vocabs

        # 字符和索引编号对应
        idx2vocab = {idx: char for idx, char in enumerate(char_vocabs)}
        vocab2idx = {char: idx for idx, char in idx2vocab.items()}

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

        # 加载训练集
        train_datas, train_labels = read_corpus(data['feature'], vocab2idx, label2idx)
        train_datas = train_datas[1:5000]
        train_labels = train_labels[1:5000]
        # 加载测试集
        test_datas, test_labels = read_corpus(data['label'], vocab2idx, label2idx)


        MAX_LEN = 100
        VOCAB_SIZE = len(vocab2idx)
        CLASS_NUMS = len(label2idx)

        # padding data
        train_datas = sequence.pad_sequences(train_datas, maxlen=MAX_LEN)
        train_labels = sequence.pad_sequences(train_labels, maxlen=MAX_LEN)
        test_datas = sequence.pad_sequences(test_datas, maxlen=MAX_LEN)
        test_labels = sequence.pad_sequences(test_labels, maxlen=MAX_LEN)
        print('x_train shape:', train_datas.shape)
        print('x_test shape:', test_datas.shape)
        # encoder one-hot
        train_labels = keras.utils.to_categorical(train_labels, CLASS_NUMS)
        test_labels = keras.utils.to_categorical(test_labels, CLASS_NUMS)
        print('trainlabels shape:', train_labels.shape)
        print('testlabels shape:', test_labels.shape)

        EPOCHS = 3
        BATCH_SIZE = 64
        EMBED_DIM = 128
        HIDDEN_SIZE = 64
        MAX_LEN = 100
        VOCAB_SIZE = len(vocab2idx)
        CLASS_NUMS = len(label2idx)

        # Input输入层
        inputs = Input(shape=(MAX_LEN,), dtype='int32')
        # masking屏蔽层
        x = Masking(mask_value=0)(inputs)
        # Embedding层
        x = Embedding(VOCAB_SIZE, EMBED_DIM, mask_zero=False)(x)
        # Bi-LSTM层
        x = Bidirectional(LSTM(HIDDEN_SIZE, return_sequences=True))(x)
        # Bi-LSTM展开输出
        x = TimeDistributed(Dense(CLASS_NUMS))(x)
        # CRF模型层
        outputs = CRF(CLASS_NUMS)(x)

        model = Model(inputs=inputs, outputs=outputs)
        model.summary()
        log_likelihood, self.transition = crf_log_likelihood(outputs, self.Y, self.X_len)
        cost = tf.reduce_mean(-log_likelihood)
        model.compile(loss=crf_log_likelihood, optimizer='adam')
        # 训练模型
        model.fit(train_datas, train_labels, epochs=EPOCHS, verbose=1, validation_split=0.1)

        score = model.evaluate(test_datas, test_labels, batch_size=BATCH_SIZE)
        print(model.metrics_names)
        print(score)

        return

    def hyperparameters(self):
        return {}
