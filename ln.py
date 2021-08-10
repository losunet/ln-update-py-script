import json
import os
import re
import time
from abc import ABCMeta, abstractmethod
from pathlib import Path
from time import sleep
from typing import List, Tuple

import requests

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36",
}


class LightNovel:
    __metaclass__ = ABCMeta

    def __init__(self, work_id, work_url, work_prefix, work_website):
        self.work_id = work_id  # work id
        self.work_url = work_url  # work url
        self.work_prefix = work_prefix  # prefix of info JSON
        self.work_website = work_website  # website title

    def get_work_info(self, work_id) -> Tuple[str, str, str, List[str]]:
        try:
            work_html = requests.get(self.work_url, headers=headers)
            work_html.encoding = 'utf-8'

            return self.get_work_info_helper(work_html)
        except Exception as e:
            print(f'- 错误信息开始\n{e}\n- 错误信息结束')
            s = input(
                f'    ! 在获取作品 {work_id} 信息时发生错误。按回车重试，或输入任何内容退出：')
            if not s:
                return self.get_work_info(work_id)
            else:
                raise

    @abstractmethod
    def get_work_info_helper(self, work_html) -> Tuple[str, str, str, List[str]]:
        pass

    def get_ep_content(self, ep_id) -> str:
        try:
            ep_html = requests.get(self.get_ep_url(ep_id), headers=headers)
            ep_html.encoding = 'utf-8'

            return self.get_ep_content_helper(ep_html)
        except Exception as e:
            print(f'- 错误信息开始\n{e}\n- 错误信息结束')
            s = input(
                f'    ! 在获取作品 {self.work_id} 的章节 {ep_id} 内容时发生错误。按回车重试，或输入任何内容退出：')
            if not s:
                return self.get_ep_content(ep_id)
            else:
                raise

    @abstractmethod
    def get_ep_url(self, ep_id) -> str:
        pass

    @abstractmethod
    def get_ep_content_helper(self, ep_html) -> str:
        pass

    @abstractmethod
    def get_ep_info(self, ep_raw) -> Tuple[str, str, str]:
        """
        Get the episode from episode raw info
        """
        pass


class Syosetu(LightNovel):
    def __init__(self, work_id):
        super().__init__(work_id, f'https://ncode.syosetu.com/{work_id}', 'ss', '小説家になろう')

    def get_work_info_helper(self, work_html) -> Tuple[str, str, str, List[str]]:
        work_title = work_html \
            .text \
            .split('<p class="novel_title">', 1) \
            .pop() \
            .split('</p>', 1)[0]
        work_author = work_html \
            .text \
            .split('<div class="novel_writername">', 1) \
            .pop() \
            .split('>', 1) \
            .pop() \
            .split('</a>', 1)[0]
        work_intro = work_html \
            .text \
            .split('<div id="novel_ex">', 1) \
            .pop() \
            .split('</div>', 1)[0]
        work_eps = work_html \
                       .text \
                       .split(f'<dl class="novel_sublist2">\n<dd class="subtitle">\n<a href="/{self.work_id}/')[1:]
        work_eps[-1] = work_eps[-1].split('</div>', 1)[0]

        return work_title, work_author, work_intro, work_eps

    def get_ep_url(self, ep_id) -> str:
        return f"{self.work_url}/{ep_id}"

    def get_ep_content_helper(self, ep_html) -> str:
        txt = ep_html.text
        pre = "" \
            if 'id="novel_p"' not in txt \
            else txt \
                     .split('<div id="novel_p" class="novel_view">', 1) \
                     .pop() \
                     .split('</div>', 1)[0] + \
                 '<p><br /></p>\n<hr />\n<p><br /></p>'
        infix = txt \
            .split('<div id="novel_honbun" class="novel_view">', 1) \
            .pop() \
            .split('</div>', 1)[0]
        post = "" \
            if 'id="novel_a"' not in txt \
            else '<p><br /></p>\n<hr />\n<p><br /></p>' + \
                 txt \
                     .split('<div id="novel_a" class="novel_view">', 1) \
                     .pop() \
                     .split('</div>', 1)[0]
        return re.sub(r' id="L[pa]?\d+"', '', pre + infix + post) \
            .strip()

    def get_ep_info(self, ep_raw) -> Tuple[str, str, int]:
        ep_id = ep_raw.split('/', 1)[0]
        title = ep_raw.split('/">', 1).pop().split('</a>', 1)[0]
        ts = int(time.mktime(time.strptime(
            ep_raw.split('span title="', 1).pop().split(' 改稿', 1)[0]
            if '<span' in ep_raw
            else ep_raw.split('<dt class="long_update">', 1).pop().split('</dt>', 1)[0].lstrip(), '%Y/%m/%d %H:%M')))

        return ep_id, title, ts


class Kakuyomu(LightNovel):
    def __init__(self, work_id):
        super().__init__(work_id, f'https://kakuyomu.jp/works/{work_id}', 'ky', 'カクヨム')

    def get_work_info_helper(self, work_html) -> Tuple[str, str, str, List[str]]:
        work_title = work_html \
            .text \
            .split(f'<a href="/works/{self.work_id}">', 1) \
            .pop() \
            .split('</a>', 1)[0]
        work_author = work_html \
            .text \
            .split('<span id="workAuthor-activityName">', 1) \
            .pop() \
            .split('>', 1) \
            .pop() \
            .split('</a>', 1)[0]
        work_intro = work_html \
            .text \
            .split('class="ui-truncateTextButton js-work-introduction">', 1) \
            .pop() \
            .split('</p>', 1)[0] \
            .strip() \
            .replace('<span class="ui-truncateTextButton-restText test-introduction-rest-text">', '') \
            .split('</span>', 1)[0]
        work_eps = work_html \
                       .text \
                       .split('<ol class="widget-toc-items test-toc-items">', 1) \
                       .pop() \
                       .split('</ol>', 1)[0] \
                       .split('episodes/')[1:]

        return work_title, work_author, work_intro, work_eps

    def get_ep_url(self, ep_id) -> str:
        return f"{self.work_url}/episodes/{ep_id}"

    def get_ep_content_helper(self, ep_html) -> str:
        return re \
            .sub(r' id="p\d+"', '', ep_html
                 .text
                 .split('reading_quantity">', 1)
                 .pop().
                 split('</div>', 1)[0]
                 .rstrip()
                 ) \
            .replace(' class="blank"', '') \
            .strip()

    def get_ep_info(self, ep_raw) -> Tuple[str, str, int]:
        ep_id = ep_raw.split('"', 1)[0]
        title = \
            ep_raw.split(
                '<span class="widget-toc-episode-titleLabel js-vertical-composition-item">',
                1).pop().split(
                '</span>', 1)[0]
        ts = int(time.mktime(
            time.strptime(
                ep_raw.split('datetime="', 1).pop().split('"', 1)[0].lstrip(),
                '%Y-%m-%dT%H:%M:%SZ')))
        return ep_id, title, ts


def ruby_text(matched):
    return f'|{matched.group(1)}《{matched.group(2)}》'


def run(work_id: str, work_type: int, work_dir: str, work_format: str = "html",
        need_title: bool = False, work_migration: bool = False, work_latest: str = "", ) -> Tuple[str, str]:
    # init Light-Novel instance
    if work_type == 1:
        ln = Syosetu(work_id)
    elif work_type == 2:
        ln = Kakuyomu(work_id)
    else:
        print('未知小说类型')
        exit()

    # work info JSON path
    work_json_path = f'./episodes/{ln.work_prefix}_{work_id}.json'

    # get work info
    work_title, work_author, work_intro, work_eps = ln.get_work_info(work_id)

    # if info JSON exists, read it; otherwise, create one
    if Path(work_json_path).is_file():
        with open(work_json_path, 'r', encoding='utf-8') as f:
            work_json = json.load(f)
    else:
        work_json = {
            'id': work_id,
            'title': work_title,
            'author': work_author,
            'intro': work_intro,
            'episodes': {}
        }

    # check if needs program to determine the title
    if need_title:
        print(work_title)
        work_dir += work_title

    # create output dirs if not exist
    if not Path(work_dir).is_dir():
        os.mkdir(work_dir)
    if not Path(work_dir + '/toast').is_dir():
        os.mkdir(work_dir + '/toast')
    if not Path(work_dir + '/web').is_dir():
        os.mkdir(work_dir + '/web')
    if not Path(work_dir + '/web/未').is_dir():
        os.mkdir(work_dir + '/web/未')
    if not Path(work_dir + '/web/完').is_dir():
        os.mkdir(work_dir + '/web/完')

    # update intro if necessary
    if work_intro != work_json['intro']:
        path = f'{work_dir}/web/未/intro_{int(time.time())}.txt'
        with open(path, 'w', encoding='utf-8') as f:
            f.write(
                f'原简介：\n{work_json["intro"].replace("<br />", "")}\n\n----------------\n\n新简介：\n{work_intro.replace("<br />", "")}')
        work_json['intro'] = work_intro
        print(f'\r    *小说『{work_title}』简介有修改，请查看 {path}')

    # total episodes
    ep_total = len(work_eps)

    # episodes object
    eps = work_json['episodes']

    try:
        for idx, ep_raw in enumerate(work_eps):
            # get episode id, title, timestamp from raw info text
            ep_id, title, ts = ln.get_ep_info(ep_raw)

            # if migrating, update the record file only
            if work_migration and work_latest and int(ep_id) <= int(work_latest):
                eps[ep_id] = {
                    'id': ep_id,
                    'title': title,
                    'ts': ts
                }
                print(f'\r{idx + 1} / {ep_total}', end='')
                continue

            # if no updates for current existing episode, skip
            if ep_id in eps and eps[ep_id]['ts'] == ts:
                continue

            # get episode content
            content = ln.get_ep_content(ep_id)

            # convert timestamp to local time string
            ts_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))

            # episode output filename w/o extension
            ep_fn = ep_id if work_type == 1 else idx + 1

            # if episode not exists in local info JSON, create one; otherwise, update the timestamp
            if ep_id not in eps:
                eps[ep_id] = {
                    'id': ep_id,
                    'title': title,
                    'ts': ts
                }
                print(f'\r    !新增-{ep_fn} ({ts_str}): {title}')
            else:
                eps[ep_id]['ts'] = ts
                print(f'\r    *修改-{ep_fn} ({ts_str}): {title}')

            # write episode content to corresponding file
            if work_format == "html":
                with open(f'{work_dir}/web/未/{ep_fn}_{ts}.html', 'w', encoding='utf-8') as f:
                    f.write(
                        f'<h1>{title}</h1>\n<p><br /></p>\n{content}\n\n<!--\n投稿网站：{ln.work_website}\n投稿作品：{work_id}\n投稿时间：{ts_str}\n投稿ID：{ep_id}\n-->')
            elif work_format == "txt":
                content = re.sub(r"<ruby><rb>(\S[^</>]+)</rb><rp>[（(《]</rp><rt>(\S[^</>]+)</rt><rp>[）)》]</rp></ruby>",
                                 ruby_text,
                                 re.sub(r"</?p>", "", content.replace("<p><br />", "").replace("<br />", "\n").replace('<hr />', '================================')))
                content += f'\n\n# 投稿网站：{ln.work_website}\n# 投稿作品：{work_id}\n# 投稿时间：{ts_str}\n# 投稿ID：{ep_id}'
                with open(f'{work_dir}/web/未/{ep_fn}_{ts}.txt', 'w', encoding='utf-8') as f:
                    f.write(f'{title}\n\n{content}')

            print(f'\r{idx + 1} / {ep_total}', end='')

            sleep(3)
    finally:
        # dump work info JSON
        with open(work_json_path, 'w', encoding='utf-8') as f:
            json.dump(work_json, f, ensure_ascii=False, indent=2)

    return work_title, work_author
