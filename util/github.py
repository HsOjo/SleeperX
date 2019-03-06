import html
import re

import requests

import common


def html_to_plain_text(content):
    content = html.unescape(content)

    reg_br = re.compile('</?br/?>')
    for i in reg_br.findall(content):
        content = content.replace(i, '\n')

    reg_tags = re.compile('</?.*?/?>')
    for t in reg_tags.findall(content):
        content = content.replace(t, '')

    p_content = ''
    while p_content != content:
        p_content = content
        content = content.replace('\n\n', '\n')
    content = content.strip()

    return content


def url_jump(url: str, link):
    if '://' in link:
        return link
    elif link[0] == '/':
        p = url.find('/', url.find('://') + 3)
        return '%s%s' % (url[:p], link)
    else:
        return '%s/%s' % (url, link)


def get_releases(url):
    resp = requests.get(url)
    resp_str = resp.content.decode('utf8')

    reg = re.compile('<div class="release-entry">[\s\S]*?<!-- /.release -->\s*</div>')
    releases = reg.findall(resp_str)

    reg_head = re.compile('<div class="d-flex flex-items-start">[\s\S]*?<a href="(.*)">(.*)</a>')
    reg_date_time = re.compile('<relative-time datetime="(.*?)T(.*?)Z">.*</relative-time>')
    reg_content = re.compile('<div class="markdown-body">([\s\S]*?)</div>')

    result = []
    for r in releases:
        link, title = common.reg_find_one(reg_head, r)
        date, time = common.reg_find_one(reg_date_time, r)
        item = {
            'url': url_jump(resp.url, link),
            'title': title,
            'datetime': '%s %s' % (date, time),
            'description': html_to_plain_text(common.reg_find_one(reg_content, r)),
        }
        result.append(item)

    return result
