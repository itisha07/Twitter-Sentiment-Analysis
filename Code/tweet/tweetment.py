import itertools
from sklearn import svm
import string
import twokenize
import emoticons
import pickle


class SentimentClassifier:
  '''
    This class contains a sentiment classifier for tweets.
  '''
  def __init__(self):

    self.w_ngram_counts = {}
    self.c_ngram_counts = {}
    self.n_ngram_counts = {}

    with open("./model.pkl", 'rb') as savefile:
        self.model = pickle.load(savefile)
        self.classifier = self.model['classifier']

  def classify(self, tweet):
    features = self.generate_features(tweet, self.model['w2c'], self.model['cids'], self.model['word_ngrams'], self.model['nonc_ngrams'], self.model['char_ngrams'])
    features += [0]*108
    predictions = self.classifier.predict([features])
    return self.model['int_to_label'][predictions[0]]

  def generate_features(self, tweet, w2c, cids, corpus_word_ng,  corpus_nonc_ng, corpus_char_ng):
    '''
      Takes in a tweet and generates a feature vector.
    '''
    words = self._tokenize(tweet)
    num_hashtags = self.hash(words)
    num_elongated = self.el(words)
    num_allcaps = self._word_is_all_caps(words)

    last_is_question_or_exclaim = 1 if self._contains_question_or_exclaim(words[-1]) else 0
    num_seq_question, num_seq_exclaim, num_seq_both = self._num_contiguous_question_exclaim(tweet)
    cluster_mem_vec = self._get_cluster_mem_vec(cids, w2c, words)

    ngram_w_vec, ngram_n_vec, ngram_c_vec = self._get_ngram_vec(tweet, corpus_word_ng,
        corpus_nonc_ng, corpus_char_ng)

    emoticon_vec = self._get_emoticon_vec(tweet, words[-1])

    features = [num_allcaps, num_hashtags, num_elongated,
        last_is_question_or_exclaim, num_seq_question, num_seq_exclaim,
        num_seq_both] + cluster_mem_vec + ngram_w_vec + ngram_n_vec +\
        ngram_c_vec + emoticon_vec
    return features

  def _contains_question_or_exclaim(self, token):
    for c in token:
      if c == '?' or c == '!':
        return True
    return False

  def _num_contiguous_question_exclaim(self, tweet):
    num_q = 0
    num_e = 0
    num_qe = 0
    entered_seq = False
    mixed = False
    last_was = ''
    for c in tweet + ' ': # add an extra space for an extra iteration (hack)
      if entered_seq:
        if c != '!' and c != '?':
          if mixed:
            num_qe += 1
          elif last_was == '!':
            num_e += 1
          else:
            num_q += 1
          entered_seq = False
          mixed = False
        elif c != last_was:
          mixed = True
      else:
        if c == '!' or c == '?':
          entered_seq = True
      last_was = c
    return num_q, num_e, num_qe

  def _get_cluster_mem_vec(self, cids, w2c, words):
    vec = [0]*len(cids)
    for word in words:
      if word in w2c:
        vec[cids[w2c[word]]] = 1
    return vec

  def hash(self, words ):
    h = 0
    for word in words :
      if word[0] == '#' :
      	h += 1
    return h
    
  def el( self, words ):
    r = 0
    for word in words :
      if self._is_elongated(word) :
      	r += 1
    return r
  
  def _get_ngram_vec(self, tweet, corpus_word_ng, corpus_nonc_ng, corpus_char_ng):
    word_vec = [0] * len(corpus_word_ng)
    nonc_vec = [0] * len(corpus_nonc_ng)
    char_vec = [0] * len(corpus_char_ng)

    word_lengths = [1,2,3,4]
    char_lengths = [1,2,3]

    for length in char_lengths:
      for idx in range(0, len(tweet) - length + 1):
        ng = tweet[idx : idx+length]
        if ng in corpus_char_ng:
          char_vec[corpus_char_ng[ng]] = 1

    words = self._tokenize(tweet)
    for length in word_lengths:
      for idx in range(0, len(words) - length + 1):
        ng = words[idx : idx+length]
        if tuple(ng) in corpus_word_ng:
          word_vec[corpus_word_ng[tuple(ng)]] = 1
        for j in range(0, length):
          tmp = list(ng)
          tmp[j] = '*' 
          if tuple(tmp) in corpus_nonc_ng:
            nonc_vec[corpus_nonc_ng[tuple(tmp)]] = 1

    return word_vec, nonc_vec, char_vec


  def _get_emoticon_vec(self, original_tweet, last_token):
    '''
      Checks if the passed-in string contains any emoticons.
    '''
    positive_in_tweet = 1 if emoticons.Happy_RE.search(original_tweet) else 0
    negative_in_tweet = 1 if emoticons.Sad_RE.search(original_tweet) else 0
    positive_ends_tweet = 1 if emoticons.Happy_RE.search(last_token) else 0
    negative_ends_tweet = 1 if emoticons.Sad_RE.search(last_token) else 0
    return [positive_in_tweet, negative_in_tweet, positive_ends_tweet,
        negative_ends_tweet]

  def _tokenize(self, tweet):
    t = twokenize.tokenize(tweet)
    return t


  def _word_is_all_caps(self, words):
    co = 0
    t = 1
    for word in words :
      t = 1
      for c in word:
        if c not in string.ascii_uppercase:
          t = 0
          break
      if t == 1 :
        co += 1    
    return co

  def _is_elongated(self, word):
    elong_len = 3
    for idx in range(len(word) - elong_len + 1):
      if word[idx] == word[idx+1] and word[idx] == word[idx+2]:
        return True
    return False


