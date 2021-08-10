# Web 轻小说更新脚本（Python）

**前置要求**

- Python v3.6 或更高：https://www.python.org/downloads/
- pip：Python 包管理工具
- request：Python 网络请求库
- urllib3 1.25.11：包含在 request 库的依赖中，但如果你需要全局魔法访问小说家，则需要手动安装（降级）

**支持站点**

- https://ncode.syosetu.com/
- https://kakuyomu.jp/

**使用步骤**

1. 下载 Python 并安装，推荐勾选 pip 和 PATH 选项
2. 如果你没有勾选 PATH，则需要手动设置 Python 的系统变量
3. 如果你没有勾选 pip，则需要手动安装 pip
4. 命令行：`pip install request`
5. 如果你是魔法用户，命令行：`pip install urllib3==1.25.11`
6. 修改 episodes/index.json 文件
7. 命令行：`python update.py`

**运行参数**

```
# 0：更新「小説家になろう」和「カクヨム」，默认值
# 1：更新「小説家になろう」
# 2：更新「カクヨム」
python update.py [0 | 1 | 2]
```

**episodes/index.json**

- 文件格式：JSON
- // 后面是注释，到时候需要删掉
- 初始样板

```JSON
{
  "format": "html",
  "migration": false,
  "max": 0,
  "works": {

  }
}
```

- 详解

```JSON
{
  "format": "html", // 字符串，值[html | txt]
  /*
    是否开启迁移模式（仅针对生肉）
    如果开启了迁移模式，且作品下的 work_latest 字段不为空，则不会下载小于（包含）字段值的章节
    i.e.
      比如小说家的某一篇文章ID是100，我给 work_latest 字段赋值100
      "n5657fv": {
        "work_latest": "100"
      }
      则脚本只会从章节101开始下载
      * 在正常执行完后该字段将自动恢复为 false，且所有 work_latest 字段的值清空
  */
  "migration": false, // 布尔，值[true | false]
  "max": 5, // 文件夹名前缀数字，指已经抓取过的作品的数量，通常不用管
  "works": {
    /*
      作品ID，字符串，必填
      https://ncode.syosetu.com/n5657fv/ → n5657fv
      https://kakuyomu.jp/works/1177354054894002394 → 1177354054894002394
    */
    "n5657fv": {
      "work_id": "n5657fv", // ID，字符串
      // 标题，字符串
      "work_title": "転生したら第七王子だったので、気ままに魔術を極めます",
      // 作者，字符串
      "work_author": "謙虚なサークル",
      /*
        类型，整数，值[1 | 2]
        指「小説家になろう」或「カクヨム」
        如果不填，会自动根据作品ID识别
        1：小説家になろう
        2：カクヨム
      */
      "work_type": 1,
      /*
        状态，整数，值[0 | 1]
        指是否更新该作品
        如果不想更新该作品，或该作品已完结，需要手动设置为1
        0：更新，默认
        1：不更新
      */
      "work_status": 0,
      /*
        存储文件夹名
        如果未指定，会根据 max 和小说标题自动生成
      */
      "work_dir": "2.転生したら第七王子だったので、気ままに魔術を極めます",
      /*
        该字段用于迁移
        如果开启迁移，则只会下载章节ID在该字段值之后的作品；空则不处理
      */
      "work_latest": ""
    },
    "1177354054902351647": {
      "work_id": "1177354054902351647",
      "work_title": "ヤンデレ妹にゾンビ(女の子)として死者蘇生されました",
      "work_author": "ぽんすけ",
      "work_type": 2,
      "work_status": 1, // 该作品已完结
      "work_dir": "3.ヤンデレ妹にゾンビ(女の子)として死者蘇生されました",
      "work_latest": ""
    }
  }
}
```

- 获取カクヨム的作品 ID 为 1177354054902351647 的全部生肉

```JSON
{
  "format": "html",
  "migration": false,
  "max": 5,
  "works": {
    ..., // 前略
    "1177354054902351647": {

    }
  }
}
```

- 获取カクヨム的作品 ID 为 1177354054902351647 的全部生肉
- 并指定路径

```JSON
{
  "format": "html",
  "migration": false,
  "max": 5,
  "works": {
    ..., // 前略
    "1177354054902351647": {
      "work_dir": "这是一个合法的路径名"
    }
  }
}
```

- 获取カクヨム的作品 ID 为 16816452219902715215 的自章节 ID 16816700426153064482 以后的生肉
- 并指定路径

```JSON
{
  "format": "html",
  "migration": true,
  "max": 5,
  "works": {
    ..., // 前略
    "1177354054902351647": {
      "work_latest": "16816700426153064482"
    }
  }
}
```

**目录结构**

```
├── 1.転生したら第七王子だったので、気ままに魔術を極めます
│   ├── toast // 熟肉文件夹
│   └── web // Web小说下载路径
│       ├── 完 // 已翻译的
│       │   └── *.[txt | html]
│       └── 未 // 未翻译的，下载的生肉会在这里
│           └── *.[txt | html]
├── episodes
│   ├── index.json
│   ├── ss_*.json // 自动生成的「小説家になろう」记录文件
│   └── ky_*.json // 自动生成的「カクヨム」记录文件
├── .gitignore
├── ln.py
├── README.md
└── update.py
```

**章节下载间隔**

```
- ln.py
  # 默认3秒，可自行调节
  sleep(3)
```
