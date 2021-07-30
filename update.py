import json
import re
import sys

import ln


def main():
    # 0 = no vpn; 1 = syosetu; 2 = kakuyomu
    mode = int(sys.argv[1]) if len(sys.argv) == 2 else 0

    err = False  # error flag

    # open works info JSON
    with open('./episodes/index.json', 'r', encoding='utf-8') as f:
        index_json = json.load(f)

    work_max = index_json['max']  # max index of existing dirs
    work_format = index_json['format']  # output format
    work_migration = index_json['migration']  # migrate or not
    works = index_json['works']  # works object
    works_total = len(works)  # total works
    try:
        for idx, (work_id, work) in enumerate(works.items()):
            need_title = False
            if 'work_id' not in work:
                work['work_id'] = work_id
            if 'work_title' not in work:
                work['work_title'] = ''
            if 'work_author' not in work:
                work['work_author'] = ''
            if 'work_type' not in work:
                if work['work_id'][0] == 'n':
                    work['work_type'] = 1
                elif work['work_id'].isdigit():
                    work['work_type'] = 2
            if 'work_status' not in work:
                work['work_status'] = 0
            if 'work_dir' not in work:
                work_max += 1
                work['work_dir'] = f'{work_max}.{work["work_title"]}'
            if 'work_latest' not in work:
                work['work_latest'] = ''

            if work['work_title'] == '' or re.match(r'^\d+\.$', work['work_title']):
                need_title = True

            if work['work_status'] != 0:
                print(f'\r- 跳过 {idx + 1} / {works_total} [不更新]: {work["work_title"]}')
                continue
            elif work['work_type'] not in [1, 2]:
                print(f'\r- 跳过 {idx + 1} / {works_total} [未知类型]: {work["work_title"]}')
                continue
            elif work['work_type'] != mode and mode != 0:
                print(f'\r- 跳过 {idx + 1} / {works_total} [类型不匹配]: {work["work_title"]}')
                continue

            print(f'\r> 更新 {idx + 1} / {works_total}: {work["work_title"]}', end="" if need_title else "\n")

            work_title, work_author = \
                ln.run(work['work_id'], work['work_type'], work['work_dir'], work_format, need_title, work_migration,
                       work['work_latest'])

            work['work_title'] = work_title
            work['work_author'] = work_author
            if need_title:
                work['work_dir'] = work['work_dir'] + work_title

            del work['work_latest']
            work['work_latest'] = ''  # migration complete
    except Exception as e:
        err = True
        print("出错咯：" + e)
    finally:
        # update the max index of existing dirs
        index_json['max'] = work_max
        if not err:
            index_json['migration'] = False

        # dump works info JSON
        with open('./episodes/index.json', 'w', encoding='utf-8') as f:
            json.dump(index_json, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
