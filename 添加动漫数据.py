import requests
import json
import os
import datetime
import time
import sys

cv_picture = []
cv_dir = "cv_images"


# 处理非法名称
def sanitize_filename(name):
    return (
        name.replace("?", "_")
        .replace("!", "_")
        .replace("。", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "_")
        .replace("*", "_")
        .replace('"', "_")
        .replace("<", "_")
        .replace(">", "_")
        .replace("|", "_")
        .replace(" ", "_")
        .replace("！", "_")
        .replace("？", "_")
        .replace("：", "_")
        .strip()
    )


class Picture:
    def __init__(self, animeName, roleName, url):
        self.animeName = sanitize_filename(animeName)
        self.roleName = roleName
        self.url = url
        self.localPath = (
            "characters/"
            + self.animeName
            + "/"
            + sanitize_filename(self.roleName)
            + ".jpg"
        )

    def __str__(self):
        return f"url: {self.url}, localPath: {self.localPath}"

    def download(self):
        if os.path.exists(self.localPath):
            # print(f"已存在，跳过下载: {self.localPath}")
            return
        # 没有目录则先创建
        os.makedirs(os.path.dirname(self.localPath), exist_ok=True)
        try:
            response = requests.get(self.url, stream=True, timeout=15)
            response.raise_for_status()
            with open(self.localPath, "wb") as f:
                for chunk in response.iter_content(1024 * 16):
                    if chunk:  # 过滤掉 keep-alive 空块
                        f.write(chunk)
            print(f"图片已保存: {self.localPath}")
        except Exception as e:
            print(f"下载图片失败: {self.url}, 错误: {e}")


class Role:
    def __init__(self):
        self.cvName = ""
        self.isMainRole = False
        self.roleName = ""
        self.picture = None
        self.summary = ""

    def __str__(self):
        return f"角色名: {self.roleName}, CV: {self.cvName}, 主役: {self.isMainRole}, 图片: {self.picture}"


class ANIME:
    def __init__(self, animeName):
        self.data = {}
        self.data["别名"] = ""
        self.data["观看状态"] = True
        self.data["作品大类"] = "Anime"
        self.data["中文名"] = sanitize_filename(animeName)
        self.data["日文名"] = ""
        self.data["开播日期"] = ""
        self.data["开播年份"] = 0
        self.data["开播月份"] = 0
        self.data["Bangumi评分"] = 0.0
        self.data["集数"] = 0
        self.data["具体类型"] = ""
        self.data["动画公司"] = ""
        self.data["原作"] = ""
        self.data["主役声优"] = []  # 包含在角色列表中
        self.data["tags"] = []
        self.data["meta_tags"] = []
        self.data["简介"] = ""
        self.data["封面"] = None
        self.data["导演"] = set()
        self.data["脚本"] = set()
        self.data["官网"] = ""
        self.data["动画制片人"] = set()
        self.data["章节列表"] = []
        self.data["角色列表"] = []

    def __str__(self):
        lines = []
        for key, value in self.data.items():
            if key == "章节列表":
                lines.append(f"{key} ({len(value)}):")
                for ep in value:
                    lines.append(f"  - {ep}")
            elif key == "角色列表":
                lines.append(f"{key} ({len(value)}):")
                for role in value:
                    lines.append(f"  - {role}")
            else:
                lines.append(f"{key}: {value}")

        return "\n".join(lines)

    def getTagToType(self):
        tags = self.data["tags"] + self.data["meta_tags"]
        rules = [
            (["小说", "轻小说改", "轻改"], "小说改"),
            (["gal", "GAL", "gal改", "GAL改", "游戏改", "galgame"], "游戏改"),
            (["漫画", "漫改", "漫画改"], "漫改"),
            ("原创", "原创"),
        ]

        self.data["具体类型"] = "未知"

        for keys, result in rules:
            if isinstance(keys, str):
                keys = [keys]
            if any(k in tags for k in keys):
                self.data["具体类型"] = result
                break

    def write_file(self):
        cn_name = sanitize_filename(self.data.get("中文名", "unknown")) or "unknown"
        file_path = f"./我的动漫/主页/{cn_name}.md"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if os.path.exists(file_path):
            msg = f"文件已存在: {file_path}，中文名: {self.data.get('中文名', '')}"
            print(msg)
            return 
            #raise FileExistsError(msg)

        tags = self.data.get("tags", [])
        meta_tags = self.data.get("meta_tags", [])
        tags_str = ", ".join(tags)
        meta_tags_str = ", ".join(meta_tags)

        cover = self.data.get("封面")
        cover_value = cover.localPath if isinstance(cover, Picture) else ""

        lines = []
        lines.append("---")
        lines.append(f"笔记ID: {datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
        lines.append(f"别名: {self.data.get('别名', '').replace(":","：")}")# obsidian中会和属性冲突
        lines.append(f"观看状态: {str(self.data.get('观看状态', True)).lower()}")
        lines.append(f"作品大类: {self.data.get('作品大类', 'Anime')}")
        lines.append(f"中文名: {self.data.get('中文名', '')}")
        lines.append(f"日文名: {self.data.get('日文名', '')}")
        lines.append(f"封面: {cover_value}")
        lines.append(f"开播日期: {self.data.get('开播日期', '')}")
        lines.append(f"开播年份: {self.data.get('开播年份', 0)}")
        lines.append(f"开播月份: {self.data.get('开播月份', 0)}")
        lines.append(f"Bangumi评分: {self.data.get('Bangumi评分', 0.0)}")
        lines.append(f"集数: {self.data.get('集数', 0)}")
        lines.append(f"具体类型: {self.data.get('具体类型', '')}")
        lines.append(f"动画公司: {self.data.get('动画公司', '')}")
        lines.append(f"原作: {self.data.get('原作', '')}")
        lines.append(f"主役声优: {",".join(self.data.get('主役声优', ''))}")
        lines.append(f"user_tags: [{tags_str}]")
        lines.append(f"tags: [{meta_tags_str}]")
        lines.append("---")
        lines.append("")
        lines.append(f"> [!bookinfo|noicon]+ **{self.data.get('中文名', '')}**")
        lines.append(f"> ![bookcover|400]({cover_value})")
        lines.append(">")
        lines.append("| 日文名 | {0} |".format(self.data.get("日文名", "")))
        lines.append("|:------: |:------------------------------------------: |")
        lines.append(f"| 类型 | {self.data.get('具体类型', '')} |")
        lines.append(
            f"| 新番 | {self.data.get('开播年份', '')} 年 {self.data.get('开播月份', '')} 月 |"
        )
        lines.append(f"| 集数 | 共{self.data.get('集数', 0)}话 |")
        lines.append(
            f"| 官网 | [{self.data.get('官网', '')}](https://{self.data.get('官网', '')}) |"
        )
        lines.append(f"| 制作 | {self.data.get('动画公司', '')} |")
        lines.append(f"| 导演 | {",".join(self.data.get('导演', ''))} |")
        lines.append(f"| 脚本 | {",".join(self.data.get('脚本', ''))} |")
        lines.append(f"| 评分 | {self.data.get('Bangumi评分', 0.0)}|")
        lines.append(f"| 制片人 | {",".join(self.data.get('动画制片人', ''))} |")

        lines.append("")
        lines.append("> [!abstract]+ **简介**")
        lines.append(f"> {self.data.get('简介', '')}")

        # 章节列表
        lines.append("")
        lines.append("> [!tip]+ **章节列表**")
        chapters = self.data.get("章节列表", [])
        if chapters:
            for ep in chapters:
                sort = ep.get("sort", "")
                name = ep.get("名称") or ep.get("name") or ""
                name_cn = ep.get("中文名", "")
                airdate = ep.get("放送日期", "")
                ep_text = f"第{sort}话：{name_cn or name}"
                if airdate:
                    ep_text += f" ({airdate})"
                lines.append(f">- [ ] {ep_text}")
        else:
            lines.append("- 暂无章节信息")

        # 主要角色（最多12个）
        lines.append("")
        lines.append("> [!tip]+ **主要角色**")
        lines.append("> ")
        selected_roles = (self.data.get("角色列表", []))[:12]
        lines.append("| 角色 | CV | 简介| 角色图片 |")
        lines.append("|:----:|:---:|:---:|:--------:|")
        if selected_roles:
            for role in selected_roles:
                role_name = role.roleName or ""
                cv_name = role.cvName or ""
                # print(role.summary)
                role_summary = (
                    role.summary.replace("\n", "<br>").replace("\r", "") or ""
                )
                pic_path = ""
                if isinstance(role.picture, Picture):
                    pic_path = role.picture.localPath or ""
                pic_md = f"![{role_name}]({pic_path})" if pic_path else ""
                lines.append(f"| {role_name} | {cv_name} | {role_summary} | {pic_md} |")
        else:
            lines.append("| - | - | - | - |")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        print(f"已写入文件: {file_path}")


# ---------------------------
# 1. 搜索动画
# ---------------------------
def search_anime(animeName):
    api_url = "https://api.bgm.tv/v0/search/subjects"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "MyAnimeApp/1.0 (https://example.com)",
    }

    payload = {
        "keyword": animeName,
        "filter": {"type": [2]},
        "limit": 2,
        "offset": 0,
        "sort": "rank",
    }

    response = requests.post(api_url, headers=headers, json=payload, timeout=15)
    response.raise_for_status()
    return response.json()


# ---------------------------
# 2. 获取条目详情
# ---------------------------
def get_subject_detail(anime, subject_id):
    url = f"https://api.bgm.tv/v0/subjects/{subject_id}"
    headers = {"User-Agent": "MyAnimeApp/1.0 (https://example.com)"}
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    detail_json = response.json()
    # print(json.dumps(detail_json, indent=4, ensure_ascii=False))
    # 中文名 / 日文名
    anime.data["中文名"] = detail_json.get("name_cn") or anime.data["中文名"]
    anime.data["日文名"] = detail_json.get("name") or ""

    # 详细信息
    aliases = []
    for item in detail_json.get("infobox", []):
        if item.get("key") == "别名":
            aliases = [v["v"] for v in item.get("value", [])]
        if item.get("key") in ["动画制作", "制作", "製作"]:
            anime.data["动画公司"] = item.get("value")
        if item.get("key") in ["原作"]:
            anime.data["原作"] = item.get("value")
        if item.get("key") in ["导演"]:
            anime.data["导演"].add(item.get("value"))
        if item.get("key") in ["脚本"]:
            anime.data["脚本"].add(item.get("value"))
        if item.get("key") in ["官方网站"]:
            anime.data["官网"] = item.get("value")
        if item.get("key") in ["动画制片人"]:
            anime.data["动画制片人"].add(item.get("value"))

    anime.data["别名"] = " / ".join(aliases)

    # 开播日期
    date = detail_json.get("date", "")
    anime.data["开播日期"] = date
    if date and len(date) >= 7:
        anime.data["开播年份"] = int(date[:4])
        anime.data["开播月份"] = int(date[5:7])

    # 评分
    anime.data["Bangumi评分"] = detail_json.get("rating", {}).get("score", 0.0)

    # 集数
    anime.data["集数"] = detail_json.get("eps", 0)

    # 简介
    anime.data["简介"] = detail_json.get("summary", "")

    # tags并去重
    raw_tags = [t["name"] for t in detail_json.get("tags", [])]
    # 按长度从长到短排序
    sorted_tags = sorted(raw_tags, key=len, reverse=True)
    final_tags = []
    for tag in sorted_tags:
        # 如果这个 tag 是某个已保留 tag 的子串，则跳过
        if any(tag in kept for kept in final_tags):
            continue
        final_tags.append(tag)

    anime.data["tags"] = final_tags
    anime.data["meta_tags"] = list(set([t for t in detail_json.get("meta_tags", "")]))

    # 从tag识别具体的动画类型
    anime.getTagToType()
    # 封面
    images = detail_json.get("images", {})
    anime.data["封面"] = Picture(anime.data["中文名"], "封面", images.get("large", ""))


# 获取制作等信息，上一个接口返回数据对一些番支持少，需要此接口补充
def get_presons_detail(anime, subject_id):
    url = f"https://api.bgm.tv/v0/subjects/{subject_id}/persons"
    headers = {"User-Agent": "MyAnimeApp/1.0 (https://example.com)"}
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    json_data = response.json()
    # print(json.dumps(json_data, indent=4, ensure_ascii=False))
    # 动画公司，原作，原作作者，制作公司，导演，脚本，制片人
    for person in json_data:
        role = person.get("relation", "")
        name = person.get("name", "")
        if role in ["动画制作"]:
            anime.data["动画公司"] = name
        elif role == "原作" or role == "原案":
            anime.data["原作"] = name
        elif role == "导演":
            anime.data["导演"].add(name)
        elif role == "脚本":
            anime.data["脚本"].add(name)
        elif role == "动画制片人":
            anime.data["动画制片人"].add(name)


# 获取角色列表
def get_character_list(anime, subject_id):
    animeName = anime.data["中文名"]
    url = f"https://api.bgm.tv/v0/subjects/{subject_id}/characters"
    headers = {"User-Agent": "MyAnimeApp/1.0 (https://example.com)"}
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    json_data = response.json()
    # print(json.dumps(json_data, indent=4, ensure_ascii=False))
    roles = []
    main_cv = []
    for ch in json_data:
        role = Role()
        role.roleName = ch.get("name") or ch.get("role_name", "")
        # 过滤乱入数据
        if role.roleName in ["圣光君", "ナレーション"]:
            continue
        role.isMainRole = ch.get("relation") == "主角"
        role.summary = ch.get("summary")
        # 角色图片
        img = ch.get("images", {})
        if img:
            role.picture = Picture(animeName, role.roleName, img.get("large", ""))

        # 声优（只取第一个）
        actors = ch.get("actors", [])
        if actors:
            role.cvName = actors[0].get("name", "")
            if role.isMainRole:
                cv_picture.append(
                    Picture(
                        cv_dir,
                        role.cvName,
                        actors[0].get("images", {}).get("large", ""),
                    )
                )
                main_cv.append(role.cvName)
        roles.append(role)

    anime.data["角色列表"] = roles
    anime.data["主役声优"] = main_cv


# 获取章节列表
def get_episode_list(anime, subject_id):
    headers = {"User-Agent": "MyAnimeApp/1.0 (https://example.com)"}
    api_url = f"https://api.bgm.tv/v0/episodes?subject_id={subject_id}"
    response = requests.get(api_url, headers=headers, timeout=15)
    response.raise_for_status()
    json_data = response.json()
    # print(json.dumps(json_data, indent=4, ensure_ascii=False))
    episodes = []
    for ep in json_data.get("data", []):
        episodes.append(
            {
                "id": ep.get("id"),
                "sort": ep.get("sort"),
                "名称": ep.get("name"),
                "中文名": ep.get("name_cn"),
                "时长": ep.get("duration"),
                "放送日期": ep.get("airdate"),
            }
        )
    anime.data["章节列表"] = episodes


# ---------------------------
# 3. 填充 ANIME 对象
# ---------------------------
def fill_anime(anime: ANIME, subject_id: int):
    # 获取动画详情
    get_subject_detail(anime, subject_id)
    # 制作信息
    get_presons_detail(anime, subject_id)
    # 章节列表
    get_episode_list(anime, subject_id)
    # 角色列表
    get_character_list(anime, subject_id)

    return anime


def download_images(anime: ANIME):
    anime.data["封面"].download()
    i = 0
    for role in anime.data["角色列表"]:
        i += 1
        if i > 12:  # 限制下载前12个角色的图片，避免过多下载
            break
        if role.picture:
            role.picture.download()
    for cv in cv_picture:
        cv.download()


# ---------------------------
# 4. 主流程
# ---------------------------
def getBgmTvAnimeData(animeName, tag=0):
    anime = ANIME(animeName=animeName)
    anime_list = []
    # 搜索
    search_json = search_anime(animeName)
    if not search_json["data"]:
        print("未找到条目")
        return None
    # print(json.dumps(search_json, indent=4, ensure_ascii=False))

    ## 获取所有包含此名称的所有结果。
    # 先判断查找名称
    # 如果查找名称有误，则获取返回的第一个结果，并去除空格后的数据
    # 适配多季的情况

    for data in search_json["data"]:
        if animeName in data["name_cn"]:
            tag = 1
            break
    if tag == 0:
        animeName_suggested = search_json["data"][0]["name_cn"].split(" ")[0]
        if animeName_suggested=="":
            print(f"查找异常，请检查输入名称：{animeName}")
            return None
        print(f"名称有误，{animeName}，建议替换为：{animeName_suggested}")
        user_input = input(f"是否使用建议名称 '{animeName_suggested}' 继续？(y/n): ")
        if user_input.lower() == "y":
            animeName = animeName_suggested
            return getBgmTvAnimeData(animeName, tag=1)
        else:
            print("已取消操作。")
            return None

    for data in search_json["data"]:
        subject_id = data["id"]
        name_cn = data["name_cn"]
        if animeName in name_cn:
            anime = ANIME(animeName=animeName)
            anime = fill_anime(anime, subject_id)
            anime_list.append(anime)

    return anime_list


# ---------------------------
# 测试
# ---------------------------
if __name__ == "__main__":
    anime_name_list = [
        # "妄想学生会",
        # "记录的地平线",
        # "神薙",
        # "在地下城寻求邂逅是否搞错了什么",
        # "咒术回战",
        # "我立于百万生命之上",
        # "你与我最后的战场，亦或是世界起始的圣战",
        # "冰菓",
        # "永生之酒",
        # "樱花庄的宠物女孩",
        # "零之使魔",
        # "旋风管家",
        # "我的青春恋爱物语果然有问题",
        # "路人女主的养成方法",
        # "约会大作战",
        # "Re：从零开始的异世界生活",
        # "某科学的超电磁炮",
        # "刀剑神域",
        # "最游记",
        # "GAMERS电玩咖",
        # "野良神",
        # "我女友与青梅竹马的惨烈修罗场",
        # "风夏",
        # "打工吧！魔王大人",
        # "狼与香辛料",
        # "妖怪公寓的优雅日常",
        # "Re：creators",
        # "碧蓝之海",
        # "绝园的暴风雨",
        # "寻找失去的未来",
        # "刀语",
        # "传说中勇者的传说",
        # "学生会的一己之见",
        # "辉夜大小姐想让我告白",
        # "星掠者",
        # "ReLIFE",
        # "Cop craft",
        # "大神与七位伙伴",
        # "[C] THE MONEY OF SOUL AND POSSIBILITY CONTROL",
        # "刺客守则",
        # "笨蛋，测验，召唤兽",
        # "这个美术社大有问题！",
        # "问题儿童都来自异世界",
        # "Angel Beats",
        # "君主·埃尔梅罗二世事件薄",
        # "在下坂本，有何贵干",
        # "Dr.STONE 石纪元",
        # "半田君传说",
        # "女高中生的虚度日常",
        # "丹特丽安的书架",
        # "噬血狂袭",
        # "灰与幻想的格林姆迦尔",
        # "我的女神",
        # "月刊少女野崎君",
        # "Fate stay night",
        # "Fate zero",
        # "命运 冠位指定 绝对魔兽战线 巴比伦尼亚",
        # "剑姬神圣谭",
        # "YUNO 在这世界尽头咏唱爱的少女",
        # "我们无法一起学习",
        # "这个勇者明明超强却过分慎重",
        # "钢之炼金术师",
        # "青春猪头少年不会梦到兔女郎学姐",
        # "青春猪头少年不会梦到怀梦美少女",
        # "叛逆性百万亚瑟王",
        # "某科学的一方通行",
        # "Fate extra last encore",
        # "男子高中生的日常",
        # "紫罗兰永恒花园",
        # "恋爱研究所",
        # "我们仍未知到那天所看见的花的名字",
        # "青之驱魔师",
        # "龙娘七七七埋藏的宝藏",
        # "神的记事本",
        # "五等分的新娘",
        # "魔法禁书目录",
        # "妖精的尾巴",
        # "宅男腐女恋爱真难",
        # "从零开始的魔法书",
        # "Overlord",
        # "Fate apocrypha",
        # "恋爱随意链接",
        # "魔弹之王与战姬",
        # "东京食尸鬼",
        # "干物妹小埋",
        # "埃罗芒阿老师",
        # "少女编号",
        # "欢迎来到实力至上主义教室",
        # "只有神知道的世界",
        # "命运石之门",
        # "爆肝工程师的异世界狂想曲",
        # "龙珠",
        # "白色相簿2",
        # "我被绑架到贵族女校当庶民样本",
        # "游戏人生",
        # "当不成勇者的我，只好认真找工作了。",
        # "盾之勇者成名录",
        # "欢迎加入NHK",
        # "Charlotte 夏洛特",
        # "GJ部",
        # "为美好世界献上祝福",
        # "异世界四重奏",
        # "RDG 濒危物种少女",
        # "最近妹妹的样子有点怪",
        # "废弃公主",
        # "苍之骑士团",
        # "属性咖啡厅",
        # "皇帝圣印战记",
        # "发条精灵战记",
        # "异界魔王与召唤少女的隶属魔术",
        # "不正经的魔术讲师与禁忌教典",
        # "灼眼的夏娜",
        # "你好 世界",
        # "异世界迷宫黑心企业",
        # "RAIL WARS! 日本国有铁道公安队",
        # "月姬",
        # "幻想嘉年华",
        # "赤色的约定",
        # "极黑的布伦希尔德",
        # "租借女友",
        # "魔法少女伊莉雅",
        # "漫画家与助手",
        # "为美好世界献上爆炎",
        # "家庭教师",
    ]

    if len(sys.argv) > 1:
        anime_name_list = sys.argv[1:]
    else:
       print("缺少参数：<需要添加的动漫名称> ，支持多组入餐")
    anime_list = []
    for animeName in anime_name_list:
        anime_list = getBgmTvAnimeData(animeName)
        for anime in anime_list:
            print(anime.data["中文名"])
            anime.write_file()
            download_images(anime)
            time.sleep(30)
    