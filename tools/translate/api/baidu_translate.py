from hashlib import md5
from time import sleep
from traceback import print_exc

import requests


class BaiduTranslate:
    lang = {
        'cn': 'zh',
        'jp': 'jp',
        'ko': 'kor',
    }

    def __init__(self, appid, key):
        self.appid = appid
        self.key = key
        self.buffer = {}

    def _translate(self, content, lang_from, lang_to):
        if content.strip() == '':
            return content

        url = 'http://fanyi-api.baidu.com/api/trans/vip/translate'
        salt = 0
        sign = md5((self.appid + content + str(salt) + self.key).encode('utf-8')).hexdigest()
        param = {
            'q': content,
            'from': lang_from,
            'to': lang_to,
            'appid': self.appid,
            'salt': salt,
            'sign': sign,
        }

        while True:
            try:
                resp = requests.get(url, params=param, timeout=5)
                result = resp.json()['trans_result'][0]['dst']
                break
            except Exception as e:
                sleep(1)

        return result

    def translate(self, content, lang_from='auto', lang_to='zh', buffer=True):
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
                    time.sleep(1)

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
    bt = BaiduTranslate()
    print(bt.translate('服を赤く染めている。', 'jp', 'cn'))
    print(bt.translate('かんぱーい！', 'ja', 'cn'))
