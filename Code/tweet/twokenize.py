import re, sys
import emoticons


def regex_or(*items):
  r = '|'.join(items)
  r = '(' + r + ')'
  return r


def optional(r):
  return '(%s)?' % r
 

def mycompile(r):
  return re.compile(r, re.UNICODE)


def pla(r):				#positive lookahead
  return '(?=' + r + ')'


def abbr_regex(a):
  chars = list(a)
  icase = ["[%s%s]" % (c, c.upper()) for c in chars]
  dotted = [r'%s\.' % x for x in icase]
  return "".join(dotted)
  

punct_chars = r'''['“".?!,:;]'''
punct = '%s+' % punct_chars
entity = '&(amp|lt|gt|quot);'

#URL variables
start1 = regex_or('https?://', r'www\.')
common = regex_or('com','co\\.uk','org','net','info','ca')
start2 = r'[a-z0-9\.-]+?' + r'\.' + common + pla(r'[/ \W\b]')
body = r'[^ \t\r\n<>]*?'
extra = '%s+?' % regex_or(punct_chars, entity)
end = regex_or( r'\.\.+', r'[<>]', r'\s', '$')
url = (r'\b' + 
    regex_or(start1, start2) + 
    body + 
    pla(optional(extra) + end))

Url_RE = re.compile("(%s)" % url, re.U|re.I)

timelike = r'\d+:\d+'
num = r'\d+\.\d+'
number = r'(\d+,)+?\d{3}' + pla(regex_or('[^,]','$'))

abbrev = ['am','pm','us','usa','ie','eg']
  
abbr = [abbr_regex(a) for a in abbrev]
  
boundary = regex_or(r'\s', '[“"?!,:;]', entity)
a1 = r'''([A-Za-z]\.){2,}''' + pla(boundary)
a2 = r'''([A-Za-z]\.){1,}[A-Za-z]''' + pla(boundary)
random_abbr = regex_or(a1, a2)
  
assert '-' != '―'
separators = regex_or('--+', '―')
decorations = r' [  ♫   ]+ '.replace(' ','')

apostrophe = r"\S+'\S+"

protect = [
    emoticons.Emoticon,
    url,
    entity,
    timelike,
    num,
    number,
    punct,
    random_abbr,
    separators,
    decorations,
    apostrophe,
]
protect_RE = mycompile(regex_or(*protect))

apos = mycompile(r"(\S+)('s)$")

WS_RE = mycompile(r'\s+')

edge_punct = r"""[  ' " “ ” ‘ ’ < > « » { } ( \) [ \]  ]""".replace(' ','')
not_edge_punct = r"""[a-zA-Z0-9]"""
edge_punct_left = r"""(\s|^)(%s+)(%s)""" % (edge_punct, not_edge_punct)
edge_punct_right = r"""(%s)(%s+)(\s|$)""" % (not_edge_punct, edge_punct)
edge_punct_left_RE = mycompile(edge_punct_left)
edge_punct_right_RE = mycompile(edge_punct_right)


class Tokenize(list):
  
  def __init__(self):
    self.text = ""
    self.alignment = []
  
  def subset(self, ind):
    new = Tokenize()
    new += [self[i] for i in ind]
    new.alignment = [self.alignment[i] for i in ind]
    new.text = self.text
    return new
  
  def assert_consistent(t):
    assert len(t) == len(t.alignment)
    assert [t.text[t.alignment[i] : (t.alignment[i] + len(t[i]))] for i in range(len(t))] == list(t)


class AlignmentFailed(Exception): pass


def align(tok, orig):
  s = 0
  alignment = [None] * len(tok)
  
  for i in range(len(tok)):
    while True:
      l = len(tok[i])
      
      if orig[s:(s + l)] == tok[i]:
        alignment[i] = s
        s += l
        break
      
      s += 1
      
      if s >= len(orig):
        raise AlignmentFailed((orig, tok, alignment))
  
  if any(a is None for a in alignment):
    raise AlignmentFailed((orig, tok, alignment))

  return alignment


def convert(s, encoding='utf8', *args):
  if isinstance(s, unicode):
    return s
  if isinstance(s, str):
    return s.decode(encoding, *args)
  return unicode(s)


def squeeze_whitespace(s):
  new_string = WS_RE.sub(" ", s)
  return new_string.strip()


def edge_punct_munge(s):
  s = edge_punct_left_RE.sub(r"\1\2 \3", s)
  s = edge_punct_right_RE.sub(r"\1 \2\3", s)
  return s


def unprotected_tokenize(s):
  return s.split()


def post_process(tok):
  final_tok = []
  for i in tok:
    m = apos.search(i)
    if m:
      final_tok += m.groups()
    else:
      final_tok.append(i)
  return final_tok


def simple_tokenize(text):
  s = edge_punct_munge(text)

  good = []
  bad = []
  i = 0
  
  if Protect_RE.search(s):
    for m in Protect_RE.finditer(s):
      good.append((i, m.start()))
      bad.append(m.span())
      i = m.end()
    good.append((m.end(), len(s)))
  
  else:
    good = [(0, len(s))]
  
  assert len(bad) + 1 == len(good)

  good = [s[i:j] for i, j in good]
  bad  = [s[i:j] for i, j in bad]
  good = [unprotected_tokenize(x) for x in good]
  res = []
  
  for i in range(len(bad)):
    res += good[i]
    res.append(bad[i])
  res += good[-1]

  res = post_process(res)
  return res


def tokenize(tweet):
  text = convert(tweet)
  text = squeeze_whitespace(text)
  t = Tokenize()
  t += simple_tokenize(text)
  t.text = text
  t.alignment = align(t, text)
  return t


if __name__=='__main__':
  for line in sys.stdin:
    print u" ".join(tokenize(line[:-1])).encode('utf-8')

