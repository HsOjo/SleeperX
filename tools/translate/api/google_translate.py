import re
import time
from traceback import print_exc

import requests
from execjs import eval as js_eval


class GoogleTranslate:
    lang = {
        'cn': 'zh-cn',
        'jp': 'ja',
    }

    def __init__(self):
        self.buffer = {}

    def _translate(self, content, lang_from, lang_to):
        if content.strip() == '':
            return content

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
        }
        session = requests.session()

        resp = session.get('https://translate.google.cn/', headers=headers)
        [tkk] = re.findall(r"tkk:'([\d\\.]*)'", resp.text)

        tk = js_eval('''
function _(a,TKK) {
var b = function (a, b) {
  for (var d = 0; d < b.length - 2; d += 3) {
    var c = b.charAt(d + 2),
      c = "a" <= c ? c.charCodeAt(0) - 87 : Number(c),
      c = "+" === b.charAt(d + 1) ? a >>> c : a << c;
    a = "+" === b.charAt(d) ? a + c & 4294967295 : a ^ c
  }
  return a
};
  for (var e = TKK.split("."), h = Number(e[0]) || 0, g = [], d = 0, f = 0; f < a.length; f++) {
    var c = a.charCodeAt(f);
    128 > c ? g[d++] = c : (2048 > c ? g[d++] = c >> 6 | 192 : (55296 === (c & 64512) && f + 1 < a.length && 56320 === (a.charCodeAt(f + 1) & 64512) ? (c = 65536 + ((c & 1023) << 10) + (a.charCodeAt(++f) & 1023), g[d++] = c >> 18 | 240, g[d++] = c >> 12 & 63 | 128) : g[d++] = c >> 12 | 224, g[d++] = c >> 6 & 63 | 128), g[d++] = c & 63 | 128)
  }
  a = h;
  for (d = 0; d < g.length; d++) a += g[d], a = b(a, "+-a^+6");
  a = b(a, "+-3^+b+-f");
  a ^= Number(e[1]) || 0;
  0 > a && (a = (a & 2147483647) + 2147483648);
  a %= 1E6;
  return a.toString() + "." + (a ^ h)
} 
''' + '("%s","%s")' % (content.replace('\n', '\\n').replace('"', '\\"'), tkk))

        params = {
            'client': 'webapp',
            'sl': lang_from,
            'tl': lang_to,
            'hl': lang_to,
            'q': content,
            'tk': tk,
            'otf': 2,
            'ssel': 0,
            'tsel': 0,
            'kc': 1,
        }

        result = None
        for i in range(5):
            try:
                resp = session.get(
                    'https://translate.google.cn/translate_a/single?dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&ie=UTF-8&oe=UTF-8',
                    params=params, headers=headers, timeout=10)
                result = resp.json()[0][0][0]
                break
            except:
                time.sleep(1)

        if result is None:
            raise Exception('Translate failed.')

        return result

    def translate(self, content, lang_from, lang_to='zh-cn', buffer=True):
        lang_from = self.lang.get(lang_from, lang_from)
        lang_to = self.lang.get(lang_to, lang_to)

        if buffer:
            if self.buffer.get(lang_from) is not None:
                gt_buf_lf = self.buffer[lang_from]
                if gt_buf_lf.get(lang_to) is not None:
                    gt_buf_lf_lt = gt_buf_lf[lang_to]
                    res = gt_buf_lf_lt.get(content)
                    if res is not None:
                        return res

        lines = content.split('\n')
        ret = ''

        for line in lines:
            while True:
                try:
                    t = self._translate(line, lang_from, lang_to)
                    if ret != '':
                        ret += '\n'
                    ret += t
                    break
                except:
                    print_exc()
                    time.sleep(3)

        if buffer:
            if self.buffer.get(lang_from) is None:
                self.buffer[lang_from] = {}
                gt_buf_lf = self.buffer[lang_from]
                if gt_buf_lf.get(lang_to) is None:
                    gt_buf_lf[lang_to] = {}
                    gt_buf_lf_lt = gt_buf_lf[lang_to]
                    gt_buf_lf_lt[content] = ret

        return ret


if __name__ == '__main__':
    gt = GoogleTranslate()
    print(gt.translate('服を赤く染めている。', 'ja', 'cn'))
    print(gt.translate('かんぱーい！', 'ja', 'cn'))
