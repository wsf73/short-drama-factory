#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""short-drama-factory v4.5 单集剧本机检（分档）

用法:
    python validate_episode.py <单集剧本.md> [--format auto|standard|long|manju] [--prev 前集.md ...] [--ref-images N]
    python validate_episode.py --self-test
    （Windows 用 python；macOS / Linux 用 python3）

    --ref-images N  单集配额上限（默认 4；0 = 关闭本项检查）。
                    单集「场景数 + 人物数」为全系统第一硬性规则，优先于时长/体量：
                    AI 视频生成时"每张参考图 = 一个场景或一个人物"，超 N 则下游一次出图放不下
                    （规格 references/reference-image-quota.md）。配额与时长冲突时，保配额、调整时长——
                    标注「【配额裁定】：配额优先，本集时长调整为 X 秒」即按实际时长 / standard 档交付，
                    E17 长档下限让位（不得为凑时长突破配额）。

档位 profile (--format; 默认 auto = 按正文自检: 含"长档"→long, 含"漫剧"→manju, 否则 standard):
    standard  标准档 90~120 秒   正文体量 实拍 680~900 / 漫剧 480~700   场景 <=2   对白行 >=4
    long      长档   150~195 秒  正文体量 实拍 1050~1400 / 漫剧 850~1150  场景 <=3   对白行 >=8   必设【本集中段小钩】
    manju     漫剧档 60~90 秒    正文体量 480~700                       场景 <=2   对白行 >=4

检查项 (FAIL=拦截必须修复, WARN=告警复核, NOTE=保护性反例提示, 明确不是缺陷):
    E1  正文体量【参考带】= 对白+动作行+断章画面（不计【】字段行/[场景][人物]）
          参考带按【本集时长】动态推导（≈5.0~7.6 字/秒·含动作）；无时长则用档位典型
          WARN(超参考带，不拦) / FAIL(低于参考带 0.6 倍 = 极端空稿)
    E2  单句台词(常规 12~18 字 / 爆发金句 8~12) 上限 25 字(超长告警,非拦截)   WARN(逐句 >25)
          注: 独白/旁白不按此判(改按 E12 的 os_len/vo_len)
    E3  场景数 <=2 ([场景] 标记计数)                FAIL(>2)
    E4  黄金前3秒: 首个内容行含冲突信号词（②行动型可用「反常动作」词）      FAIL(无)
    E5  开篇禁词(起床/拉窗帘/太阳升起/走在路上等)     WARN
    E6  断章卡点: 存在【本集断章卡点】且含黑屏/悬念   FAIL(缺)
    E7  情绪流变词: 存在【情绪流变】链条(-> 或 ➔)    WARN(缺)
    E8  复读检测: 主角台词与前集传入(--prev)重复     WARN(重复句)
    E9  对白行数: >= 本档位下限(标准/漫剧 4 行, 长档 8 行)  WARN(不足)
          注: 独白/旁白行不计入对白行数(防用独白充数绕过攻防结构检查)
    E10 合规红线词(断肢/开膛/下蛊等一票否决直观描写)  FAIL
    E11 长档中段小钩: 存在【本集中段小钩】(long 档)      FAIL(长档缺)
    E12 独白/旁白配额: 内心独白 标准1/长档2/漫剧1 处(单处 25/30/20 字); 旁白 ≤1 处·≤12 字  FAIL(超配额)
    E13 独白/旁白连排: 两条相邻, 或紧贴断章收尾            FAIL
    E14 独白里写交代设定 / 抽象情绪                       WARN
    E15 前 3 秒出现独白/旁白(应为场内冲突)                FAIL
    E16 时长虚标(v3.4.1·long 档): 【本集时长】> 台词量可拆时长×1.20      FAIL
          可拆时长 = 纯台词字数÷4.5(参考语速) + 动作行数×1.5s + 5s 留白；动作行字数不参与时长换算；
          写作目标语速 5.5 字/s（15秒≈82字，上限 95字≈6.33字/s）
    E17 长档降级(v3.4.2·long 档): 【本集时长】< 150 秒(长档下限)          FAIL
          即"挂长档名头、交标准档体量"：补足纯台词(180s≈990字)或降为 standard 档
          (8 字动作 ≈ 2~3s，与 8 字台词不同价)——防"氛围 △ 行凑体量、虚标 180 秒"
    E19 15秒窗口台词密度(v4.0·WARN 生产端建议): 连续对白块 >95 字       WARN
          △动作行/独白/旁白视为视觉断点重置累积；独白/旁白不计入对白累积；
          95字≈15秒×6.33字/s触顶，超量则 AI 口型/节奏崩坏——建议插动作行断点或拆分
    E20 动作单段≤40字(v4.2·WARN 软约束): 单条 △ 镜头净字数 >40 字      WARN
          一条 △ 超 40 字＝一个镜头塞了两个机位/动作，建议拆为两个 △ 镜头（软约束不拦截）
    E21 对白/动作字数黄金比 25%~70%(v4.2·WARN): 对白/(对白+△动作)        WARN
          >70%→缺少肢体冲突与视听调度；<25%→缺乏唇枪舌战；独白/旁白不计入两端
    E22 台词用语/错别字(常用误用对照，如 竞然/迫不急待/掉过钱…)          WARN(只提示，不拦)
    E23 冲突形态适配: ②行动坚持型必须设【质疑者配角】(准备×质疑的对手位)  FAIL(缺或为空)
    E24 单集配额【第一硬性规则·v4.5】: 场景数 + 人物数 <= N(默认 4, --ref-images 调整, 0=关闭)  FAIL(超限)
          全系统优先级最高，优先于时长(E16/E17)与体量(E1)：AI 视频生成"每张参考图 = 一个场景或一个人物"，
          单集超限则下游无法一次出图。超限修法：合并工具位/公职功能位/无台词角色、降为画外/群像、合并场景；
          若压缩后撑不满原定时长，保配额、调整时长（【配额裁定】：配额优先，按实际时长/standard 档交付或拆集）
          （规格 references/reference-image-quota.md）
    E18 对白语气供给(v3.4.3·对接导演端 V6.9.3 C16 / model-adapters §5.2):
        E18a 神态短语含空泛情绪结果词(开心/愤怒等)                       WARN
        E18b 全篇对白行无一处语气词(极端态: 嗓音/发声方式信息整集缺失)    WARN
          语气词写法见 templates/episode-format.md §四 神态短语规格（画面词｜语气词）；
          部分覆盖不拦（逐句语气由导演端 C16b 在分镜稿上按 50% 缺失率兜底）。

保护性反例 (NOTE 级 —— 提示"你可能过度修正了", 不要求修改; 详见 references/protective-counterexamples.md):
    N12 碎句化: 连续 >=5 行对白且每行净字数 <=4      NOTE(疑为绕开 E2 而剁碎完整句)
    N13 堆动作: 动作行 >=12 且均净字数 <=14 且对白行 <= 本档下限  NOTE(疑为凑 E1 体量堆动作)
    N14 贴下限: 体量 <= 下限+15 且断章段净字数 <20    NOTE(疑为达标而压掉必要过程/断章过干)
退出码: 0=通过(可含WARN/NOTE), 1=FAIL, 2=用法错误
"""
import re
import sys

# 剧本文本体量阈值(仅计正文: 对白行 + △动作行 + 断章卡点画面描述)
NET_MIN, NET_MAX = 480, 850          # 实拍短剧（宽参考带：只抓极端过薄/过厚，中间不卡）
NET_MIN_ANIME, NET_MAX_ANIME = 330, 620  # 漫剧/竖屏动画
NET_LONG_MIN, NET_LONG_MAX = 820, 1400        # 长档(150~195秒弹性) 实拍
NET_LONG_ANIME_MIN, NET_LONG_ANIME_MAX = 660, 1150  # 长档 漫剧/竖屏动画
SENT_MAX = 25                        # 单句台词上限(WARN 级告警,非拦截; 常规 12~18)

# ---- 长档时长守恒锚点（v4.3：按实测语速重校——15秒≈95字上限，写作目标 5.5 字/s）----
# E16 管上限（禁虚标）、E17 管下限（禁降级交付）：两端夹住，长档才真的"点长档得长档"。
LONG_MIN_SEC = 150                   # 长档【本集时长】下限(秒)：低于此即"挂长档名头、交标准档体量"
DLG_PER_SEC = 4.5                    # 台词→时长换算参考语速(字/s)，用于 E16（容差 ±20%）；
                                     # 说明：95字/15秒（6.33字/s）是「连续对白时的局部上限」，不是全片均值；
                                     #      全片对白时间占比宜 60~75%，其余留给动作/留白/转场~→有效均值 ~4.5 字/s
DLG_TARGET = {90: 400, 120: 540, 150: 670, 180: 800, 195: 870}   # 各目标时长的纯台词量【参考中值】(字)，非硬门槛
WIN15_MAX_CHARS = 95                 # E19: 任何连续对白块净字数上限(字)，≈15秒×6.33字/s触顶

# ---- 单集配额（v4.5 第一硬性规则 · 由 v4.4 参考图配额升格）----
# 下游 AI 视频生成"每张参考图 = 一个场景或一个人物"，单集可投喂参考图数量有硬上限；
# 剧本端须保证「场景数 + 人物数」≤ 该上限，否则一次出图放不下。
# v4.5 起：默认 4，且为全系统第一硬性规则——优先于时长(E16/E17)与体量(E1)；
# 配额与时长冲突时一律保配额、调整时长（见 quota_ruling() / 【配额裁定】字段）。
# 可用 --ref-images N 调整，--ref-images 0 关闭本项检查。
REF_IMAGE_LIMIT = 4

# ---- 对白语气供给（v3.4.3 · 对接导演端 V6.9.3 C16 / model-adapters §5.2 对白三要素）----
# 官方对白三要素 = WHO SPEAKS + WHAT THEY SAY + HOW THEY SOUND；
# 剧本端负责第三要素的"上游供给"：神态短语里的语气词原文保留，导演端直接搬进台词语气位。
# 规格见 templates/episode-format.md §四（画面词在前｜语气词在后，用全角 ｜ 分界）。
TONE_WORDS = ("嘶哑", "沙哑", "气音", "颤声", "发颤", "哭腔", "哽咽", "破音", "气若游丝",
              "有气无力", "低语", "轻声", "柔声", "厉声", "厉喝", "嘶吼", "低吼", "怒喝",
              "咆哮", "一字一顿", "一字一句", "拖长音", "阴阳怪气", "讥诮", "嗤笑", "冷笑",
              "咬牙切齿", "压低声音", "压着嗓", "急促", "咬着牙", "冷冷", "淡淡", "沉声",
              "低声", "高声", "尖声", "声音极低", "声音发", "嗓音", "语气", "颤", "哑",
              "低声道", "冷声道", "字字")
E18_VAGUE_WORDS = ("开心", "难过", "生气", "愤怒", "悲伤", "伤心", "高兴", "邪魅", "伤感", "激动")

# ---- E22 台词用语/错别字（常用误用对照，WARN 级：只提示、不拦）----
TYPO_LITERALS = (
    ("竞然", "竟然"), ("既使", "即使"), ("即然", "既然"),
    ("迫不急待", "迫不及待"), ("按耐", "按捺"), ("穿流不息", "川流不息"),
    ("走头无路", "走投无路"), ("挺而走险", "铤而走险"), ("一如继往", "一如既往"),
    ("按步就班", "按部就班"), ("甘败下风", "甘拜下风"), ("相形见拙", "相形见绌"),
    ("不加思索", "不假思索"), ("有持无恐", "有恃无恐"), ("天翻地复", "天翻地覆"),
    ("人情事故", "人情世故"), ("鬼鬼崇崇", "鬼鬼祟祟"), ("声名雀起", "声名鹊起"),
    ("一愁莫展", "一筹莫展"), ("不径而走", "不胫而走"), ("张慌", "张皇"),
    ("倍受", "备受"), ("做为", "作为"), ("帐号", "账号"), ("通霄", "通宵"),
    ("瞪目结舌", "瞠目结舌"), ("蜂涌", "蜂拥"), ("各行其事", "各行其是"),
    ("断章取意", "断章取义"), ("来不急", "来不及"), ("楞", "愣"),
    ("攒紧", "攥紧"), ("趔列", "趔趄"), ("踉仓", "踉跄"),
    ("嘀估", "嘀咕"), ("嘱付", "嘱咐"), ("多嗦", "哆嗦"), ("硬咽", "哽咽"),
)
TYPO_REGEX = (
    (r"掉(?:过|了)[^。！？\n]{0,4}(?:钱|银子)", "「掉」用于钱物不通，口语应为「掏」/「出」"),
)

# ---- 独白 / 旁白（非说话的叙述通道）----
# 详见 references/inner-monologue-vo.md：独白是「配额制工具」，不是台词，也不是心理描写替身。
VO_OS_TAGS = ("内心独白", "独白", "心声")            # 只有观众听见的说话人心声
VO_VO_TAGS = ("旁白", "画外音", "画面字幕", "字幕")   # 第三人称点题 / 时间锚
# E14：独白里出现「交代设定/前情」信号词，或抽象情绪词（应写「具体的账」）
VO_EXPO_WORDS = ["事情要从", "这一切都要从", "这一切都因为", "之所以", "众所周知",
                 "前情", "话说当年", "回顾一下", "背景是", "原来是这样的"]
VO_ABSTRACT_WORDS = ["五味杂陈", "百感交集", "思绪万千", "心如刀割", "难以言表", "感慨万千"]

# 档位 profile（体量区间另按 profile + 是否漫剧解析，见 net_band()）
#   os / os_len: 内心独白 每集配额(处) / 单处字数上限
#   vo / vo_len: 旁白·字幕 每集配额(处) / 单处字数上限
PROFILES = {
    "auto":     {"scenes": 2, "lines": 4, "midhook": False, "os": 1, "os_len": 25, "vo": 1, "vo_len": 12, "label": "自动分档"},
    "standard": {"scenes": 2, "lines": 4, "midhook": False, "os": 1, "os_len": 25, "vo": 1, "vo_len": 12, "label": "标准档 90~120 秒"},
    "long":     {"scenes": 3, "lines": 8, "midhook": True,  "os": 2, "os_len": 30, "vo": 1, "vo_len": 12, "label": "长档 150~195秒弹性"},
    "manju":    {"scenes": 2, "lines": 4, "midhook": False, "os": 1, "os_len": 20, "vo": 1, "vo_len": 12, "label": "漫剧档 60~90 秒"},
}

OPEN_BAN_WORDS = ["早晨起床", "起床", "拉窗帘", "太阳升起", "醒过来", "走在路上",
                  "整理衣服", "开车上班", "喝咖啡闲聊", "悠闲的清晨", "阳光明媚的早晨"]

# 注: 不含 "△" —— 动作行本身不等于冲突, 否则任何以动作开场的剧本恒过 E4
# 注: 不含 "冷笑" —— "冷笑"是 AI 假动作陈词滥调(见反AI禁词口径), 不应作为开局冲突信号词
CONFLICT_SIGNALS = ["！?", "！", "枪", "刀", "巴掌", "扔", "砸", "吼",
                    "逼", "跪", "撕", "拍在", "顶在", "推", "踹", "骂", "羞辱", "退婚",
                    "病危", "签字", "死", "滚", "住手", "救", "断裂", "炸", "烧", "血"]
# ②行动坚持型的开篇钩子是「反常动作」，不属于以上冲突词——另附表，避免被 E4 误杀
ACTION_SIGNALS = ["囤", "搬", "扛", "抬", "焊", "封", "锁", "插销", "装箱", "码",
                  "发电机", "钢板", "密封", "加固", "抢购", "屯", "备货", "储", "水桶",
                  "断电", "停水", "挖", "砌", "钻", "拧", "钉", "背", "贴", "算"]

BREAK_WORDS = ["断章", "卡点", "黑屏", "悬念"]

REDLINE_WORDS = ["断肢", "开膛", "破肚", "身首异处", "凌迟", "活埋", "注射死刑", "吸毒",
                 "制毒", "自杀方法", "下蛊害人", "蛊毒害人", "真实的国家机关"]


_VO_LINE_RE = re.compile(r"^(内心独白|独白|心声|旁白|画外音|画面字幕|字幕)(（[^）]*）|\([^)]*\))?\s*[:：]\s*(.+)$")


def _vo_line(line):
    """独白/旁白行 → (kind, 内容)；kind ∈ {'os' 内心独白, 'vo' 旁白/字幕}；非独白行返回 None

    这是「只有观众听见」的叙述通道，不是台词。因此：
      - 不计入 E9 对白行数（防「用独白充数绕过攻防结构检查」的漏洞）
      - 不按 E2 台词 25 字上限判，改按本档位 os_len / vo_len 判（E12）
    规格见 references/inner-monologue-vo.md。
    """
    s = line.strip()
    if not s or s.startswith(("[", "△", "【", "#", ">")):
        return None
    m = _VO_LINE_RE.match(s)
    if not m:
        return None
    return ("os" if m.group(1) in VO_OS_TAGS else "vo", m.group(3))


def _is_dialogue(line):
    """对白行: 角色名(可选括号提示): 台词  —— 不以[ △ 【开头，且不是独白/旁白行"""
    s = line.strip()
    if not s or s.startswith(("[", "△", "【", "#", ">")):
        return None
    if _vo_line(s):
        return None
    m = re.match(r"^([\u4e00-\u9fa5A-Za-z0-9]{1,8})(（[^）]*）|\([^)]*\))?\s*[:：]\s*(.+)$", s)
    return m.group(3) if m else None


def _paren_of(line):
    """对白行的神态短语（括号内容）→ str；无括号或非对白行返回 ''"""
    s = line.strip()
    if not s or _vo_line(s) is not None:
        return ""
    m = re.match(r"^[\u4e00-\u9fa5A-Za-z0-9]{1,8}(?:（([^）]*)）|\(([^)]*)\))?\s*[:：]", s)
    if not m:
        return ""
    return (m.group(1) or m.group(2) or "").strip()


def net_chars(text):
    """剧本文本体量: 仅计
        - 对白行台词
        - 独白/旁白行内容（占用成片时长，故计入体量；但不计入对白行数）
        - △ 动作指示行内容
        - 【本集断章卡点】画面描述
    剔除: 【所属阶段】【黄金前3秒钩子】【情绪流变】【本集时长】等字段行,
          以及 [场景]/[人物] 标记行(结构性元数据, 非剧本正文)
    """
    total = 0
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        d = _is_dialogue(s)
        v = _vo_line(s)
        if v is not None:
            body = v[1]
        elif d is not None:
            body = d
        elif s.startswith("△"):
            body = re.sub(r"^△\s*", "", s)
        elif s.startswith("【本集断章卡点】"):
            body = re.sub(r"^【本集断章卡点】\s*[:：]?\s*", "", s)
        else:
            continue  # 字段行【】/标记行[]/普通行 一律不计
        body = re.sub(r"[\s，。！？；：、…—\-·“”\"'‘’（）()《》!?.]", "", body)
        total += len(body)
    return total


def _header_text(text):
    """只取剧本头部（前 3 行：集标题/档位标注区）——避免正文里随口出现的
    '长档/漫剧' 字样把 auto 分档带偏。显式档位请用 --format。"""
    return "\n".join(text.splitlines()[:3])


def is_anime(text):
    """漫剧/竖屏动画项目: 头部含 '漫剧' 即按漫剧体量档判 E1"""
    return "漫剧" in _header_text(text)


def is_long(text):
    """长档项目: 头部含 '长档' 即按长档体量判 E1/E3/E9/E11"""
    return "长档" in _header_text(text)


def quota_ruling(text):
    """v4.5 第一硬性规则配套：正文是否标注「【配额裁定】：配额优先…」。
    含义：单集「场景数 + 人物数 ≤ 4」与既定档位/时长冲突时，明确裁定保配额、调整单集时长
    （按实际体量以 standard 档交付，或将本集拆成两集）——E17 长档 150 秒下限对此类集让位。
    无字段时一切照旧（长档仍受 E16/E17 双面夹住）。"""
    m = re.search(r"【配额裁定】[：:]\s*([^\n】]{1,80})", text)
    return bool(m and "配额优先" in m.group(1))


def resolve_profile(text, profile="auto"):
    """auto 档按正文自检: 含"长档"→long, 含"漫剧"→manju, 否则 standard。
    v4.5：第一硬性规则裁定优先——长档集若标注【配额裁定】配额优先（≤4 配额撑不满 150 秒），
    按 standard 档校验交付，E11/E16/E17 不再以长档口径拦截。"""
    if profile != "auto":
        resolved = profile if profile in PROFILES else "standard"
    elif is_long(text):
        resolved = "long"
    elif is_anime(text):
        resolved = "manju"
    else:
        resolved = "standard"
    if resolved == "long" and quota_ruling(text):
        return "standard"
    return resolved


def net_band(text, profile):
    """正文体量【参考带】。优先按剧本自报的【本集时长】动态推导，并按冲突形态微调系数：
    ①对话型 ×5.0~7.6（台词为主）/ 混合 ×4.2~6.5 / ②行动型 ×3.5~5.5（动作承载、文字量天然少）。
    无【本集时长】时退回档位典型带。体量是参考值，不硬卡（见 E1）——用户说“我这集 4 分钟”就按 240 秒算。"""
    m = re.search(r"【本集时长】[：:]\s*(\d+)", text)
    if m:
        t = int(m.group(1))
        if t > 0:
            _mode = conflict_mode(text)
            _lo, _hi = (3.5, 5.5) if _mode == "行动型" else ((4.2, 6.5) if _mode == "混合" else (5.0, 7.6))
            return (round(t * _lo), round(t * _hi))
    if profile == "long":
        return (NET_LONG_ANIME_MIN, NET_LONG_ANIME_MAX) if is_anime(text) else (NET_LONG_MIN, NET_LONG_MAX)
    if profile == "manju":
        return NET_MIN_ANIME, NET_MAX_ANIME
    return (NET_MIN_ANIME, NET_MAX_ANIME) if is_anime(text) else (NET_MIN, NET_MAX)


def scene_count(text):
    return len(re.findall(r"^\[场景\]|^【场景】|^##?\s*场景", text, re.M))


def roster_count(text):
    """[人物] 名册条目数（按 、，,／/ 切分，剔除括号备注）。E24 参考图配额用。
    与 scene_count 相加即为「单集需要的参考图张数」。"""
    n = 0
    for line in re.findall(r"^\[人物\][：:]\s*(.+)$", text, re.M):
        for x in re.split(r"[、，,／/]", line):
            if re.sub(r"（[^）]*）|\([^)]*\)", "", x).strip():
                n += 1
    return n


def first_content_lines(text, n=3):
    out = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith(("#", ">", "第", "【", "[")):
            continue
        out.append(s)
        if len(out) >= n:
            break
    return out


def conflict_mode(text):
    """冲突形态：对话型（嘴仗）/ 行动型（准备×质疑）/ 混合；缺省=对话型。
    规格见 references/conflict-modes.md。行动型：战场在错位（做事↔质疑），对白天然稀少
    → E9 对白行下限减半、E21 对白占比下限降至 10%，否则行动型会被对白类规则误杀。"""
    m = re.search(r"【冲突形态】[：:]\s*([^\n【]{1,30})", text)
    if m:
        s = re.split(r"[／/\s、,，]", m.group(1).strip())[0]
        if "行动" in s:
            return "行动型"
        if "混合" in s:
            return "混合"
    return "对话型"


def validate(text, prev_texts=(), profile="auto", ref_limit=None):
    profile = resolve_profile(text, profile)
    prof = PROFILES[profile]
    mode = conflict_mode(text)
    if mode == "行动型":
        lines_min = max(3, prof["lines"] // 2)      # 长档 8→4（对白天然少）
    elif mode == "混合":
        lines_min = max(4, prof["lines"] - 2)       # 长档 8→6（行动外壳+对话火力）
    else:
        lines_min = prof["lines"]
    act_credit = 4.0 if mode == "行动型" else (2.5 if mode == "混合" else 1.5)    # 动作拍权重：行动型>混合>对话型（行动型靠准备动作承载叙事，否则 E16/E17 两头夹）
    fails, warns = [], []
    nc = net_chars(text)
    lo, hi = net_band(text, profile)
    if nc < lo * 0.5:
        fails.append(f"E1 [{profile}] 正文体量 {nc} 过薄（参考带 {lo}~{hi}；仅拦极端空稿）")
    elif not (lo <= nc <= hi):
        warns.append(f"E1 正文体量 {nc} 超出参考带 {lo}~{hi}（体量为参考值：按【本集时长】或内容判断，不拦）")

    # E2 单气口≤25字：仅限对白行，按标点拆 clause（一行内可有多个气口），逐 clause 净字数 >25 → WARN；
    # △动作行/独白旁白不按此判（独白/旁白走 E12），不误伤动作描写。
    for line in text.splitlines():
        d = _is_dialogue(line)
        if not d:
            continue
        for clause in re.split(r"[，。！？；、…—!?;]", d):
            c = re.sub(r"[\s“”\"‘’（）()《》：:，。！？；、…—]", "", clause)
            if len(c) > SENT_MAX:
                warns.append(f"E2 单句台词 {len(c)} 字(>{SENT_MAX}): {c[:18]}…")

    sc = scene_count(text)
    _cap = prof["scenes"]
    _md = re.search(r"【本集时长】[：:]\s*(\d+)", text)
    if _md:
        _t = int(_md.group(1))
        if _t > 0:
            _cap = max(_cap, int(round(_t / 75.0)))   # 自定义长集（>195s）：场景上限随集长放宽，≈每 75 秒 1 场
    if sc > _cap:
        fails.append(f"E3 [{profile}] 场景数 {sc} >{_cap}")
    if sc == 0:
        warns.append("E3 未检出 [场景] 标记，无法核对场景数")

    # E24 单集配额【第一硬性规则】：场景数 + 人物数 <= N（v4.5 默认 4，优先于时长/体量）
    _rl = REF_IMAGE_LIMIT if ref_limit is None else ref_limit
    ppl = roster_count(text)
    if _rl and sc + ppl > _rl:
        fails.append(f"E24 第一硬性规则·配额超限：场景 {sc} + 人物 {ppl} = {sc + ppl} > {_rl}"
                     "（单集配额为全系统第一规则，优先于时长/体量：应合并工具位/公职功能位/无台词角色、"
                     "降为群像画外、台词承接或合并场景；压缩后撑不满原时长的，保配额、调整时长——"
                     "标注【配额裁定】：配额优先，本集时长调整为 X 秒，按实际时长交付或拆集）")

    head = "".join(first_content_lines(text))
    banned_hit = any(w in head for w in OPEN_BAN_WORDS)
    _sig = CONFLICT_SIGNALS + (ACTION_SIGNALS if mode == "行动型" else [])
    if banned_hit or not any(w in head for w in _sig):
        fails.append("E4 前3秒无冲突/命中开篇废镜头词(须直接切入冲突顶点，禁铺垫；②行动型可用反常动作)")
    for w in OPEN_BAN_WORDS:
        if w in head:
            warns.append(f"E5 开篇疑似废镜头禁词「{w}」")

    if not re.search(r"【本集断章卡点】|\[本集断章", text):
        fails.append("E6 缺【本集断章卡点】段")
    else:
        seg = re.search(r"【本集断章卡点】(.{0,200})", text, re.S)
        if seg and not any(w in seg.group(1) for w in ["黑屏", "悬念", "下滑", "解锁"]):
            warns.append("E6 断章卡点缺黑屏/下滑解锁落点词")

    if not re.search(r"【情绪流变】.*(->|➔|➔|→)", text):
        warns.append("E7 缺【情绪流变】链条(应标: 遭受刁难 ➔ … ➔ 绝命断章)")

    rounds = 0
    my_lines = [d for d in (_is_dialogue(l) for l in text.splitlines()) if d]
    rounds = len(my_lines)
    if prof["midhook"] and not re.search(r"【本集中段小钩】|\[本集中段小钩", text):
        fails.append("E11 长档缺【本集中段小钩】(≈90 秒处必设新信息/新威胁，防滑走)")
    if rounds < lines_min:
        warns.append(f"E9 [{profile}] 对白行仅 {rounds} 行(<{lines_min})，攻防结构不足" + ("（行动型已减半）" if mode == "行动型" else ""))
    # E23 行动型必须有【质疑者配角】（准备×质疑 的对手位）
    if mode == "行动型":
        _q = re.search(r"【质疑者配角】[：:]\s*([^\n]*)", text)
        if (not _q) or _q.group(1).strip() in ("", "无", "无。", "—", "-"):
            fails.append("E23 行动型缺【质疑者配角】（对手位缺失：准备×质疑 必须有质疑者；无对手位＝行动流水账）")

    # ---- 对白语气供给（E18 · v3.4.3；对接导演端 V6.9.3 C16 / model-adapters §5.2）----
    # 剧本端负责对白三要素之三 HOW THEY SOUND 的上游供给：语气词写在神态短语里、原文保留，
    # 导演端直接搬进镜行台词语气位 `台词：【角色（语气）："…"】`（分流表见 §5.2）。
    if my_lines:
        # E18a 神态短语空泛情绪结果词（导演端无法执行的结果词，需改四维可执行词）
        for l in text.splitlines():
            p = _paren_of(l)
            if not p:
                continue
            v = [w for w in E18_VAGUE_WORDS if w in p]
            if v:
                warns.append(f"E18a 神态短语含空泛情绪词「{'/'.join(v)}」：{p}——"
                             "改为可执行的语气/画面词（如 压着怒·低语 ／ 指节捏白），"
                             "规格见 templates/episode-format.md §四")
                break
        # E18b 全篇对白零语气词（极端态：HOW THEY SOUND 整集缺失 → 下游表情/声音一并扁平）
        tone_lines = sum(1 for l in text.splitlines()
                         if _is_dialogue(l) and any(w in _paren_of(l) for w in TONE_WORDS))
        if tone_lines == 0:
            warns.append(f"E18b 全篇 {rounds} 行对白无一处语气词（嗓音/发声方式信息整集缺失）——"
                         "官方对白三要素之三 HOW THEY SOUND 上游缺供：给关键对白补语气词"
                         "（如（气音·发颤）／（俯身逼近｜甜笑·柔声）），规格见 templates/episode-format.md §四")

    # ---- 独白 / 旁白通道（E12~E15；规格见 references/inner-monologue-vo.md）----
    # 独白是「配额制工具」：只服务委屈立住/点题转折/立人设/心事外化，不承担交代设定。
    seq = []            # 内容行序列 (cls, text)，cls ∈ os/vo/dia/act/break
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith(("#", ">", "[场景", "[人物", "第【")):
            continue
        if s.startswith("【本集断章卡点】") or s.startswith("[本集断章"):
            seq.append(("break", s)); continue
        if s.startswith("【"):
            continue
        v = _vo_line(s)
        if v is not None:
            seq.append((v[0], v[1])); continue
        if _is_dialogue(s) is not None:
            seq.append(("dia", s)); continue
        if s.startswith("△"):
            seq.append(("act", s)); continue

    os_cnt = sum(1 for c, _ in seq if c == "os")
    vo_cnt = sum(1 for c, _ in seq if c == "vo")
    if os_cnt > prof["os"]:
        fails.append(f"E12 [{profile}] 内心独白 {os_cnt} 处 > {prof['os']}：独白是配额制工具，超量即注水")
    if vo_cnt > prof["vo"]:
        fails.append(f"E12 [{profile}] 旁白/字幕 {vo_cnt} 处 > {prof['vo']}：旁白只服务点题转折")
    for cls, body in seq:
        if cls in ("os", "vo"):
            cap = prof["os_len"] if cls == "os" else prof["vo_len"]
            n = len(re.sub(r"[\s，。！？；：、…—\-·“”\"'‘’（）()《》!?.]", "", body))
            if n > cap:
                fails.append(f"E12 {'内心独白' if cls == 'os' else '旁白/字幕'}单处 {n} 字 >{cap}（{body[:14]}…）")

    for i in range(len(seq) - 1):
        if seq[i][0] in ("os", "vo") and seq[i + 1][0] in ("os", "vo"):
            fails.append("E13 连续两条独白/旁白（禁连排）：独白之间必须隔动作或台词")
            break
    bi = next((i for i, (c, _) in enumerate(seq) if c == "break"), None)
    if bi is not None and bi > 0 and seq[bi - 1][0] in ("os", "vo"):
        fails.append("E13 独白/旁白紧贴断章收尾：断章必须落在画面/事件上（独白收尾＝软收尾）")

    for cls, body in seq:
        if cls not in ("os", "vo"):
            continue
        for w in VO_EXPO_WORDS:
            if w in body:
                warns.append(f"E14 独白含交代设定/前情信号「{w}」：独白不承担交代设定（红线 2）")
                break
        for w in VO_ABSTRACT_WORDS:
            if w in body:
                warns.append(f"E14 独白写抽象情绪「{w}」：独白要写「具体的账」（我给他生了五个孩子），不写抽象感受")
                break

    for s in first_content_lines(text, 3):
        if _vo_line(s):
            fails.append("E15 前 3 秒出现独白/旁白：黄金 3 秒必须是场内冲突（独白开场＝软开场，踩红线 1）")
            break

    # E16 时长虚标（v3.4.1·长档；v4.0 报错信息补双语速口径）：【本集时长】必须能被台词量支撑
    # 可拆时长 ≈ 纯台词字数÷4.5(参考语速) ＋ 动作行数×act_credit(对话型1.5 / 混合2.0 / 行动型2.5) ＋ 断章留白5s
    # 动作行字数不参与换算（8 字动作 ≈ 2~3s，与 8 字台词不同价）——防"动作行凑体量虚标 180 秒"
    # 参考语速 4.5 字/s（= 局部上限 6.33 × 对白时间占比~0.7）；E16 容差 ±20%（不卡小偏差）
    m_dur = re.search(r"【本集时长】[:：]?\s*(\d{2,4})\s*秒", text)
    if m_dur and profile == "long":
        dlg_chars = 0
        action_lines = 0
        for line in text.splitlines():
            s = line.strip()
            v = _vo_line(s)
            d = _is_dialogue(s)
            if v is not None:
                dlg_chars += len(re.sub(r"[\s，。！？；：、…—]", "", v[1]))
            elif d is not None:
                dlg_chars += len(re.sub(r"[\s，。！？；：、…—]", "", d))
            elif s.startswith("△"):
                action_lines += 1
        est = dlg_chars / DLG_PER_SEC + action_lines * act_credit + 5
        claimed = int(m_dur.group(1))
        if claimed > est * 1.20:
            fails.append(
                f"E16 时长虚标：标注 {claimed}s，按台词量最多可拆 {est:.0f}s"
                f"（纯台词 {dlg_chars} 字÷4.5字/s【参考语速】 ＋ {action_lines} 动作拍×{act_credit}s[{mode}] ＋ 留白）——"
                "参考语速 4.5 字/s（局部上限 6.33 × 对白占比 0.7），容差 ±20%；补足台词量或改标真实时长；"
                "动作行字数不参与时长换算，禁止用氛围 △ 行凑体量虚标")

        # E17 长档时长下限（v3.4.2）：标注低于档位下限 = 降级交付
        # 补 E16 的反面——E16 拦"虚标"，E17 拦"诚实标短的降级"，两端夹住长档时长守恒。
        if claimed < LONG_MIN_SEC:
            fails.append(
                f"E17 长档降级：标注 {claimed}s 低于长档下限 {LONG_MIN_SEC}s——挂着长档名头、交的是标准档体量"
                f"（纯台词仅 {dlg_chars} 字，可拆 {est:.0f}s）。三条出路：① 补足纯台词量做成真长档"
                "（150s≈670字 / 180s≈800字 / 195s≈870字 纯台词【参考中值】）；"
                "② 明确改 --format standard（90~120 秒）；"
                "③ 若受 E24 第一硬性规则所限（场景+人物≤4、撑不满 150 秒），标注"
                "「【配额裁定】：配额优先，本集时长调整为 X 秒」即按实际时长交付（保配额、调时长）。"
                "禁止用动作行凑体量后标短时长来规避 E16")

    for prev in prev_texts:
        prev_set = set(re.sub(r"\s", "", p) for p in (_is_dialogue(l) for l in prev.splitlines()) if p)
        for d in my_lines:
            dd = re.sub(r"\s", "", d)
            if dd in prev_set and len(dd) >= 8:
                warns.append(f"E8 台词与前集复读: {dd[:16]}…")

    for w in REDLINE_WORDS:
        if w in text:
            fails.append(f"E10 合规一票否决类直观描写「{w}」")

    # ---- E19 15秒窗口台词密度（v4.0·WARN 生产端建议，非平台硬约束）----
    # 连续对白块净字数 >95 → WARN：95字≈15秒×6.33字/s触顶，超量则 AI 口型/节奏崩坏。
    # △动作行/独白/旁白/字段行/断章行均视为视觉断点，重置累积；独白/旁白本就不计入对白累积。
    run_chars = 0
    for line in text.splitlines():
        s = line.strip()
        d = _is_dialogue(s)
        if d is not None:
            run_chars += len(re.sub(r"[\s，。！？；：、…—]", "", d))
            continue
        if run_chars > WIN15_MAX_CHARS:
            warns.append(f"E19 15秒窗口台词超量：连续对白 {run_chars} 字超过 {WIN15_MAX_CHARS} 字上限"
                         f"（对应 {run_chars / 15:.2f} 字/s 触顶 6.33 字/s），建议插入 △动作行断点或拆分")
        run_chars = 0
    if run_chars > WIN15_MAX_CHARS:
        warns.append(f"E19 15秒窗口台词超量：连续对白 {run_chars} 字超过 {WIN15_MAX_CHARS} 字上限"
                     f"（对应 {run_chars / 15:.2f} 字/s 触顶 6.33 字/s），建议插入 △动作行断点或拆分")

    # ---- E20 动作单段≤40字软约束（WARN）：单条 △ 镜头净字数 >40 字 → 建议拆为两个 △ 镜头 ----
    # 一条 △ 超过 40 字＝一个镜头塞了两个机位/动作，导演端无法一镜拍完；WARN 不拦截。
    # ---- E21 对白/动作字数黄金比 25%~70%（WARN）：比例=对白净字数/(对白净字数+△动作净字数) ----
    # 对白>70% → 全靠嘴说、缺肢体冲突与视听调度；<25% → 缺唇枪舌战。独白/旁白不计入两端（非攻防台词）。
    act_total = 0
    dlg_total = 0
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("△"):
            body = re.sub(r"^△\s*", "", s)
            n = len(re.sub(r"[\s，。！？；：、…—\-·“”\"‘’（）()《》!?.]", "", body))
            if n > 40:
                warns.append(f"E20 动作单段{n}字(>40)，建议拆为两个△镜头")
            act_total += n
        else:
            d = _is_dialogue(s)
            if d is not None:
                dlg_total += len(re.sub(r"[\s，。！？；：、…—\-·“”\"‘’（）()《》!?.]", "", d))
    denom = dlg_total + act_total
    if denom > 0:
        ratio = dlg_total / denom
        pct = int(round(ratio * 100))
        if ratio > 0.70:
            warns.append(f"E21 对白占比{pct}%>70%，缺少肢体冲突与视听调度")
        else:
            _lo = 0.10 if mode == "行动型" else (0.15 if mode == "混合" else 0.25)
            if ratio < _lo:
                warns.append(f"E21 对白占比{pct}%<{int(_lo*100)}%，缺乏唇枪舌战" + (f"（{mode}已放宽）" if mode != "对话型" else ""))

    # ---- E22 台词用语/错别字（WARN，只提示不拦）----
    _hit = set()
    for _raw in text.splitlines():
        _s = _raw.strip()
        if not _s or _s.startswith(("【", "[", "#", ">", "△")):
            continue
        for _bad, _good in TYPO_LITERALS:
            if _bad in _s and _bad not in _hit:
                _hit.add(_bad)
                warns.append(f"E22 台词用语：『{_bad}』疑为『{_good}』")
        for _pat, _note in TYPO_REGEX:
            _m = re.search(_pat, _s)
            if _m and _pat not in _hit:
                _hit.add(_pat)
                warns.append(f"E22 台词用语：『{_m.group(0)}』——{_note}")

    return fails, warns, nc


_PUNCT = "，。！？；：、…—－·“”（）()《》!?."
_QUOTES = "\"'" + "\u2018\u2019"
_STRIP_RE = re.compile("[" + re.escape(_PUNCT + _QUOTES) + r"\s]")

FRAG_RUN = 5        # N12: 连续短对白行数阈值（每行净字数 <= 4）
FRAG_LEN = 4
DUMP_ACT = 12       # N13: 动作行数阈值
DUMP_AVG = 14       # N13: 动作行平均净字数上限
NEAR_LO = 15        # N14: "贴近下限"容差
BRK_MIN = 20        # N14: 断章段净字数下限


def collect_notes(text, profile="auto"):
    """保护性反例提示（NOTE 级）—— 明确不是缺陷，提示「可能过度修正了」。

    详见 references/protective-counterexamples.md。
    三级输出约定: FAIL 必须修 / WARN 需人工复核（可判定成立） / NOTE 不要求修改。
    """
    profile = resolve_profile(text, profile)
    prof = PROFILES[profile]
    mode = conflict_mode(text)
    notes = []

    # N12 碎句化：连续 >=FRAG_RUN 行对白，每行净字数 <=FRAG_LEN
    run, run_start = 0, ""
    for line in text.splitlines():
        d = _is_dialogue(line)
        if d is None:
            continue
        clean = _STRIP_RE.sub("", d)
        if len(clean) <= FRAG_LEN:
            if run == 0:
                run_start = clean
            run += 1
            if run >= FRAG_RUN:
                notes.append("N12 连续 %d 行以上短对白（≤%d 字），起于「%s」：疑为绕开单句上限而剁碎完整句。"
                             "完整直说不是缺陷——权力压制/羞耻/正式场合下话可能更客气更完整，而非更碎" % (FRAG_RUN, FRAG_LEN, run_start))
                break
        else:
            run = 0

    # N13 堆动作：动作行 >=DUMP_ACT 且均净字数 <=DUMP_AVG 且对白行 <= 本档下限
    act, dia = [], []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("△"):
            act.append(len(_STRIP_RE.sub("", re.sub(r"^△\s*", "", s))))
        else:
            d = _is_dialogue(s)
            if d is not None:
                dia.append(d)
    if mode == "对话型" and act and len(act) >= DUMP_ACT and (sum(act) / len(act)) <= DUMP_AVG and len(dia) <= prof["lines"]:
        notes.append("N13 动作行 %d 条、均 %.1f 字，对白仅 %d 行：疑为凑 E1 体量堆低信息动作行。"
                     "动作多不等于有戏——应合并重复证明、让同一动作兼任人物/线索/情绪" % (len(act), sum(act) / len(act), len(dia)))

    # N14 贴下限：体量 <= 下限+NEAR_LO 且断章段净字数 <BRK_MIN
    nc = net_chars(text)
    lo, _hi = net_band(text, profile)
    m = re.search(r"【本集断章卡点】\s*[:：]?\s*(.*)", text)
    brk = len(_STRIP_RE.sub("", m.group(1))) if m else 0
    if nc <= lo + NEAR_LO and brk < BRK_MIN:
        notes.append("N14 体量 %d 贴近本档下限 %d、断章段仅 %d 字：疑为达标而压掉必要过程或断章过干。"
                     "必要过程不能为卡线而删；若本集本身成立（余波集/快节奏转折集），在交付说明写明理由即可" % (nc, lo, brk))

    return notes


GOOD = """第【1】集：【龙王令·开局羞辱】
【黄金前3秒钩子】：极端羞辱
【情绪流变】：当众受辱 ➔ 隐忍握拳 ➔ 亮令反杀 ➔ 绝命断章
【本集时长】：105 秒
[场景]：内景·顶级私人会所·夜
[人物]：林辰（隐忍龙王）、陈峰（嚣张富二代）、苏清雪（未婚妻）

△ 特写：点燃的雪茄狠狠摁在林辰洗得发白的衣领上，青烟直冒，火星坠落。
△ 中景：陈峰搂着苏清雪，满脸鄙夷，包厢内保镖环立。
陈峰（吐出烟圈）：跪下，把这杯脏水喝了，十万块救命钱，本少当场转给你。
苏清雪（冷漠）：林辰，别不知好歹，认清你自己的身份。
△ 特写：林辰低垂的眼眸骤抬，垂在身侧的右拳缓缓握紧，指节泛白。
林辰（声音极低）：三年前你陈家跪着求我救命时，也是这副嘴脸？
陈峰（恼羞成怒）：你找死！给我废了他双手！
△ 四名保镖暴起扑上，林辰反手抓住领头手腕顺势一拧，骨裂声起，保镖倒飞砸碎整面酒柜。
△ 玻璃碎裂，酒水横流，全场死寂，陈峰踉跄后退撞翻茶几。
陈峰（色厉内荏）：你……你敢动手？你知道我爸是谁吗？
△ 中景：包厢门被推开，闻讯赶来的酒店经理满头大汗挤进人群，站在一旁不敢出声。
苏清雪（攥紧手包）：林辰，你今天要是踏出这个门，咱俩的婚事就算彻底完了。
林辰（掸了掸袖口）：婚事？当年你苏家跪着退婚的时候，怎么不记得提这两个字？
△ 苏清雪被噎得脸色一阵青一阵白，捏着包带的指节收紧，再没敢抬头。
林辰：在江城，能让我跪的，只有已故的先人。
△ 林辰从怀中掏出一枚九龙玄铁令，重重拍在桌上，震得酒杯齐齐炸裂。
林辰（字字如刀）：传我龙王令，十分钟内，让江城陈氏集团彻底破产。
△ 特写：陈峰死死盯着令牌上的九龙图腾，双腿剧烈发抖，手机疯狂震动，来电显示"父亲"。
林辰（声音极低）：三年了，你陈家欠的账，一笔一笔都在这儿。
陈峰（嘶哑）：我……我错了，我这就去给你赔罪。
林辰：赔罪的话，留着跟我的律师说。
△ 陈峰的膝盖一软，扶着茶几才没跪下去。
苏清雪（发颤）：林辰，我们好歹有过情分，你别赶尽杀绝。
林辰（淡淡）：情分？你踩着它上台的时候，忘了？
△ 满堂保镖谁也不敢上前，齐齐往门边退。
林辰：今天走出这扇门的，我一个都不追究。
△ 话音一落，保镖们争先恐后涌向门口。
陈峰（急）：你连他们也收买了？
林辰：我用不着收买。他们只是比你，看得清形势。
苏清雪：林辰，看在过去的情分上，放过陈家吧。
陈峰：爸……爸，你在哪儿啊……
苏清雪：这些事，我什么都不知道。
△ 陈峰把脸埋进手里，肩膀一抽一抽地抖。
△ 陈峰瘫坐在地，手机屏幕还亮着，来电仍在闪。

【本集断章卡点】：陈峰颤抖着接通电话，那头传来绝望哭嚎："逆子，你到底得罪了谁？陈家彻底完了！"林辰一步踏出，居高临下逼近。（黑屏：下滑立即解锁第2集）
"""

BAD = """第【1】集
清晨，林辰起床拉开窗帘，太阳升起。他在路上慢慢走。
陈峰：林辰，你要知道，三年前你害死了我父亲，侵占了我们家三千万的财产，今天我一定要让你血债血偿，把我的东西全部还回来！
林辰：好的。
△ 他把断肢捡起来。
"""


def self_test():
    ok = 1
    f, w, nc = validate(GOOD)
    if f:
        print("FAIL self-test: GOOD 样例不应 FAIL:", f); ok = 0
    if nc < 100:
        print("FAIL self-test: GOOD 净字数异常", nc); ok = 0
    f, w, _ = validate(BAD)
    if not any("E1" in x for x in f):
        print("FAIL self-test: BAD 应报 E1 或字数异常"); ok = 0
    if not any("E4" in x for x in f):
        print("FAIL self-test: BAD 应报 E4 前3秒无冲突"); ok = 0
    if not any("E6" in x for x in f):
        print("FAIL self-test: BAD 应报 E6 缺断章"); ok = 0
    if not any("E10" in x for x in f):
        print("FAIL self-test: BAD 应报 E10 红线词"); ok = 0
    if not any("E5" in x for x in w):
        print("FAIL self-test: BAD 应报 E5 开篇禁词"); ok = 0

    # 回归1: 字段行不应灌入 E1 体量
    hdr_only = "第【1】集\n【所属阶段】：第X幕・（第 1/80 集 ｜ 往返第 N 回合）\n【黄金前3秒钩子】：极端羞辱型（婚礼当众）\n【情绪流变】：受辱 ➔ 隐忍 ➔ 反杀 ➔ 绝命断章\n【本集时长】：108 秒\n[场景]：内景·会所·夜\n[人物]：林辰、陈峰\n"
    if net_chars(hdr_only) != 0:
        print("FAIL self-test: 纯字段/标记行应计 0 字，实得", net_chars(hdr_only)); ok = 0

    # 回归2: 以 △ 开场的废镜头剧本，E4 必须拦截
    boring = "第【1】集\n[场景]：内景·客厅·日\n[人物]：甲、乙\n△ 他慢慢走进客厅，端起茶杯喝了一口。\n△ 他看了看窗外。\n甲：今天天气不错。\n乙：是啊。\n甲：那先这样。\n乙：好。\n【本集断章卡点】：两人告别。（黑屏）\n"
    f, w, _ = validate(boring)
    if not any("E4" in x for x in f):
        print("FAIL self-test: △ 开场的废镜头剧本应报 E4"); ok = 0

    # 回归3: 漫剧档体量(480~700)应可用
    anime = "第【1】集：漫剧\n【情绪流变】：受辱 ➔ 隐忍 ➔ 反杀 ➔ 绝命断章\n[场景]：内景·堂·日\n[人物]：甲、乙\n" + "".join(f"△ 具体的物理动作行编号{i}，可被镜头拍到的行为事件推进本集冲突。\n" for i in range(18)) + "甲：你确定要这么做？\n乙：我确定。\n甲：那就别怪我。\n乙：来吧。\n【本集断章卡点】：灯灭人散，只余一击。（黑屏：下滑解锁）\n"
    f, w, _ = validate(anime)
    if any("E1" in x for x in f):
        print("FAIL self-test: 漫剧档不应报 E1 区冲突:", [x for x in f if 'E1' in x]); ok = 0

    # 回归4: 台词上限 25（WARN 非拦截）
    longline = "第【1】集\n[场景]：内景\n[人物]：甲\n△ 拍桌。\n甲：这是超过二十五个字的长复合句用来触发告警检查是否生效一二三四五六七八。\n【本集断章卡点】：黑屏（黑屏）\n"
    f, w, _ = validate(longline)
    if not any("E2" in x for x in w):
        print("FAIL self-test: >25 字台词应报 E2"); ok = 0

    # 回归5: 长档（150~195 秒弹性）—— 双回合 + 中段小钩 + 体量 1050~1400 + 台词为主体，auto 档自检
    long_body = ("".join(f"△ 受力事件{i}：巴掌扇到半空被反手抓住，冲突再升一级。\n" for i in range(10))
                 + "".join(f"林辰：第{i}句攻防台词，抛出新信息并抬价施压。\n" for i in range(48)))
    long_good = ("第【1】集：长档样例（长档·约3分钟）\n【本集时长】：180 秒\n"
                 "[场景]：内景·会所·夜\n[场景]：内景·走廊·夜\n[人物]：林辰、陈峰\n"
                 + long_body
                 + "【本集中段小钩】：手机亮起病危通知单，缴费截止今晚，对面按下挂断键。\n"
                 + "△ 林辰反手拧腕，骨裂声起，铁棍滚落。\n"
                 + "【本集断章卡点】：电话那头传来绝望哭嚎，陈峰双腿发抖。（黑屏：下滑解锁第2集）\n")
    f, w, nc = validate(long_good)
    if f:
        print("FAIL self-test: 长档样例不应 FAIL:", f, "体量", nc); ok = 0
    if not (NET_LONG_MIN <= nc <= NET_LONG_MAX):
        print(f"FAIL self-test: 长档样例体量 {nc} 应在 {NET_LONG_MIN}~{NET_LONG_MAX}"); ok = 0
    # 长档缺中段小钩 → E11
    f, _, _ = validate(long_good.replace("【本集中段小钩】", "【中段】"))
    if not any("E11" in x for x in f):
        print("FAIL self-test: 长档缺中段小钩应报 E11"); ok = 0
    # E16 时长虚标：台词量减半仍标 180 秒 → FAIL（动作行凑体量模式）
    f, _, _ = validate(long_good.replace(
        "".join(f"林辰：第{i}句攻防台词，抛出新信息并抬价施压。\n" for i in range(48)),
        "".join(f"林辰：第{i}句攻防台词，抛出新信息并抬价施压。\n" for i in range(16))))
    if not any("E16" in x for x in f):
        print("FAIL self-test: 台词量不足仍标 180 秒应报 E16 时长虚标:", f); ok = 0
    # E17 长档降级：同体量台词（可拆约 190 秒）却只标 110 秒 → FAIL（"诚实标短"的降级交付）
    f, _, _ = validate(long_good.replace("【本集时长】：180 秒", "【本集时长】：110 秒"), profile="long")
    if not any("E17" in x for x in f):
        print("FAIL self-test: 长档标 110 秒应报 E17 长档降级:", f); ok = 0
    # E17 反向：≥150 秒不应误报（150/180/195 三个合法点）
    for _d in (150, 180, 195):
        f, _, _ = validate(long_good.replace("【本集时长】：180 秒", f"【本集时长】：{_d} 秒"), profile="long")
        if any("E17" in x for x in f):
            print(f"FAIL self-test: 长档标 {_d} 秒不应报 E17:", [x for x in f if "E17" in x]); ok = 0
    # 显式 --format long 检标准档样本 → 长档缺中段小钩(E11)；极端空稿应报 E1
    f, w, _ = validate(GOOD, profile="long")
    if not any("E11" in x for x in f):
        print("FAIL self-test: 标准档样本按 long 显式机检应报 E11"); ok = 0
    f, _, _ = validate(BAD, profile="long")
    if not any("E1" in x for x in f):
        print("FAIL self-test: 极端空稿应报 E1"); ok = 0
    # 体量参考带随【本集时长】动态推导：超过参考带上限不应 FAIL（用户说多长就多长）
    f, _, _ = validate(long_good.replace("【本集时长】：180 秒", "【本集时长】：60 秒"), profile="manju")
    if any("E1" in x for x in f):
        print("FAIL self-test: 体量超参考带上限不应 FAIL:", [x for x in f if "E1" in x]); ok = 0
    # 长档场景上限 3：4 场应报 E3
    f, _, _ = validate(long_good + "[场景]：内景·车库·夜\n[场景]：内景·天台·夜\n")
    if not any("E3" in x for x in f):
        print("FAIL self-test: 长档 4 场景应报 E3"); ok = 0

    # ---- 保护性反例（NOTE 级）回归 ----
    # N0: 合格样稿不应产生任何 NOTE（防误报）
    n = collect_notes(GOOD)
    if n:
        print("FAIL self-test: GOOD 样例不应产生 NOTE:", n); ok = 0
    n = collect_notes(long_good)
    if n:
        print("FAIL self-test: 长档样例不应产生 NOTE:", n); ok = 0

    # N12: 连续 6 行 <=4 字对白 → 碎句化提示
    frag = ("第【1】集\n[场景]：内景·堂·日\n[人物]：甲、乙\n△ 巴掌扇到半空被反手抓住。\n"
            "甲：跪下。\n乙：凭什么。\n甲：闭嘴。\n乙：你敢。\n甲：再说。\n乙：罢了。\n"
            "【本集断章卡点】：巴掌落下，满堂死寂，门外脚步声骤起，全家齐齐转头望去，画面定住。（黑屏：下滑立即解锁第2集）\n")
    if not any("N12" in x for x in collect_notes(frag)):
        print("FAIL self-test: 连续短对白应报 N12 碎句化"); ok = 0

    # N13: 14 条低信息动作行 + 仅 1 行对白 → 堆动作提示
    dump = ("第【1】集\n[场景]：内景\n[人物]：甲\n"
            + "".join("△ 抬手。\n" for _ in range(14))
            + "甲：你来了。\n"
            + "【本集断章卡点】：门开，光涌进来，甲缓缓抬头，画面定住，下滑立即解锁下一集内容。\n")
    if not any("N13" in x for x in collect_notes(dump)):
        print("FAIL self-test: 堆低信息动作行应报 N13"); ok = 0

    # N14: 体量贴下限 + 断章段过干 → 压过程提示
    thin = ("第【1】集\n[场景]：内景\n[人物]：甲\n△ 把刀拍在桌上。\n甲：说。\n"
            "【本集断章卡点】：黑屏。\n")
    if not any("N14" in x for x in collect_notes(thin)):
        print("FAIL self-test: 体量贴下限且断章过干应报 N14"); ok = 0

    # NOTE 不得混入 FAIL 列表（NOTE 是「不要求修改」级，绝不能被当作拦截）
    for sample in (frag, dump, thin, GOOD):
        f, _, _ = validate(sample)
        bad = [x for x in f if re.match(r"^N\d", x)]
        if bad:
            print("FAIL self-test: NOTE 级不应出现在 FAIL 列表:", bad); ok = 0

    # ---- 独白 / 旁白（VO）回归 ----
    # V1: 独白不得充作对白行 —— 3 句真台词 + 1 处独白 + 1 处旁白，E9 应报不足（标准档下限 4）
    vo_fill = ("第【1】集\n[场景]：内景·堂屋·日\n[人物]：周韶华、二儿媳\n"
               "△ 巴掌扇到半空被反手抓住，满堂死寂。\n"
               "二儿媳：周韶华你说是不是。\n"
               "△ 周韶华的手攥紧围裙，指节发白。\n"
               "内心独白：我给他生了五个孩子。\n"
               "△ 二儿媳抬手指着她鼻尖。\n"
               "周韶华：我说是。\n"
               "△ 满堂人齐齐转头。\n"
               "旁白：老实人反抗了。\n"
               "二儿媳：你说。\n"
               "【本集断章卡点】：门被踹开，满堂死寂。（黑屏：下滑立即解锁第2集）\n")
    f, w, _ = validate(vo_fill)
    if not any("E9" in x for x in w):
        print("FAIL self-test: 独白不应计入对白行（应报 E9 不足）"); ok = 0
    if any("E12" in x or "E13" in x or "E15" in x for x in f):
        print("FAIL self-test: 合规的独白样本不应报 E12/E13/E15:", f); ok = 0

    # V2: 独白豁免台词 25 字上限（长档单处 ≤30）——28 字独白不应报 E2、也不应报 E12
    vo28 = "我这一辈子给他生了五个孩子，他走的那天我还在灯下缝他的棉袄。"
    vo_long = ("第【1】集：长档样例（长档·约3分钟）\n[场景]：内景·堂屋·日\n[人物]：周韶华\n"
               "△ 巴掌扇到半空被反手抓住，满堂死寂。\n"
               "周韶华：你回来了。\n"
               "△ 二儿媳抬手指着她鼻尖，满堂人齐齐转头，目光全部钉在她脸上。\n"
               + f"内心独白：{vo28}\n"
               + "【本集中段小钩】：手机亮起病危通知单，缴费截止今晚。\n"
               + "△ 反手拧腕，铁棍滚落。\n甲：跪下。\n"
               + "【本集断章卡点】：门被踹开，满堂死寂。（黑屏：下滑立即解锁第2集）\n")
    f, w, _ = validate(vo_long)
    if any(x.startswith("E2 ") for x in w):
        print("FAIL self-test: 独白不应按台词 25 字上限报 E2:", [x for x in w if x.startswith("E2 ")]); ok = 0
    if any("E12" in x for x in f):
        print("FAIL self-test: 长档 28 字独白不应报 E12(上限 30):", [x for x in f if "E12" in x]); ok = 0

    # V3: 超配额 —— 标准档 2 处内心独白 → E12
    f, _, _ = validate(vo_fill.replace("旁白：老实人反抗了。", "内心独白：这一世我谁都不欠了。"))
    if not any("E12" in x for x in f):
        print("FAIL self-test: 标准档 2 处内心独白应报 E12"); ok = 0

    # V4: 连排 —— 两条独白相邻 → E13
    f, _, _ = validate("第【1】集\n[场景]：内景·堂屋·日\n[人物]：甲\n△ 巴掌扇到半空被反手抓住。\n"
                       "内心独白：我给他生了五个孩子。\n旁白：老实人反抗了。\n"
                       "甲：你说是不是。\n乙：我说是。\n丙：我说不是。\n"
                       "【本集断章卡点】：门被踹开，满堂死寂。（黑屏：下滑立即解锁第2集）\n")
    if not any("E13" in x for x in f):
        print("FAIL self-test: 连续两条独白应报 E13"); ok = 0

    # V5: 独白紧贴断章 → E13
    f, _, _ = validate("第【1】集\n[场景]：内景·堂屋·日\n[人物]：甲\n△ 巴掌扇到半空被反手抓住。\n"
                       "甲：你说是不是。\n乙：我说是。\n丙：我说不是。\n丁：我说是。\n"
                       "内心独白：这一世我谁都不欠了。\n"
                       "【本集断章卡点】：门被踹开，满堂死寂。（黑屏：下滑立即解锁第2集）\n")
    if not any("E13" in x for x in f):
        print("FAIL self-test: 独白紧贴断章应报 E13"); ok = 0

    # V6: 前 3 秒独白 → E15
    f, _, _ = validate("第【1】集\n[场景]：内景·堂屋·日\n[人物]：甲\n"
                       "内心独白：我给他生了五个孩子。\n△ 巴掌扇到半空被反手抓住。\n"
                       "甲：你说是不是。\n乙：我说是。\n"
                       "【本集断章卡点】：门被踹开，满堂死寂。（黑屏：下滑立即解锁第2集）\n")
    if not any("E15" in x for x in f):
        print("FAIL self-test: 前3秒独白应报 E15"); ok = 0

    # V7: 独白交代设定 → E14
    f, w, _ = validate(vo_fill.replace("内心独白：我给他生了五个孩子。", "内心独白：这一切都要从三十年前说起。"))
    if not any("E14" in x for x in w):
        print("FAIL self-test: 独白交代设定应报 E14"); ok = 0

    # ---- 对白语气供给（E18 · v3.4.3）回归 ----
    # T1: 神态短语空泛情绪词 → E18a
    f, w, _ = validate(GOOD.replace("苏清雪（冷漠）：", "苏清雪（生气）："))
    if not any("E18a" in x for x in w):
        print("FAIL self-test: 神态短语空泛情绪词应报 E18a:", [x for x in w if "E18" in x]); ok = 0
    # T2: 全篇对白零语气词 → E18b（把 GOOD 的神态短语全部换成语气无关词并去掉带语气词的行）
    t2 = GOOD
    for a, b in (("（吐出烟圈）", "（把玩打火机）"), ("（冷漠）", "（抱臂）"),
                 ("（声音极低）", "（盯着他）"), ("（恼羞成怒）", "（踹翻椅子）"),
                 ("（字字如刀）", "（指着令牌）"), ("（色厉内荏）", "（后退半步）"),
                 ("（嘶哑）", "（攥拳）"), ("（发颤）", "（低头）"), ("（淡淡）", "（转开脸）")):
        t2 = t2.replace(a, b)
    f, w, _ = validate(t2)
    if not any("E18b" in x for x in w):
        print("FAIL self-test: 全篇对白零语气词应报 E18b:", [x for x in w if "E18" in x]); ok = 0
    # T3: 合规语气供给（含 ｜ 分界的混合式）不应报 E18a/E18b
    t3 = GOOD.replace("苏清雪（冷漠）：", "苏清雪（抱臂后退｜冷漠疏离）：")
    f, w, _ = validate(t3)
    if any("E18a" in x or "E18b" in x for x in w):
        print("FAIL self-test: 合规语气供给不应报 E18:", [x for x in w if "E18" in x]); ok = 0
    # T4: 台词用语/错别字 → E22 WARN（只提示不拦）
    t4 = GOOD.replace("林辰（声音极低）：三年前你陈家跪着求我救命时，也是这副嘴脸？",
                      "林辰：他竞然敢这么说话。")
    f, w, _ = validate(t4)
    if not any("E22" in x for x in w):
        print("FAIL self-test: 错别字应报 E22:", [x for x in w if "E22" in x]); ok = 0
    # T5: 行动型放宽（对白少但结构全）——去掉【冲突形态】标记应报 E9/E21，加上不应报
    _act_body = ("[场景]：内景·楼道·夜\n[人物]：陈默、张叔\n"
                 + "".join(f"△ 准备动作{i}：他把加固钢板一块块拧上去，火星四溅，处境又安全一层。\n" for i in range(14))
                 + "张叔（嗤笑）：你这是要把整栋楼拆了重盖一遍啊？\n△ 陈默没抬头，继续拧螺丝。\n"
                 + "张叔（扬声）：我跟物业打过招呼了，明天就来人拆。\n△ 陈默把螺丝拧到底，手背青筋绷起。\n"
                 + "张叔（敲了敲钢板）：一宿一宿折腾，你到底图个什么？\n△ 陈默弯腰，把最后一颗铆钉敲进去。\n"
                 + "陈默（平静）：明天要停电，你现在下楼还来得及。\n△ 陈默转身，把水桶推到门口。\n"
                 + "张叔（大笑）：停电？就你信这个，疯子。\n【本集中段小钩】：路灯全灭，整片小区陷入黑暗。\n"
                 + "【本集断章卡点】：楼下传来第二声闷响，备用发电机没响。（黑屏：下滑解锁）\n")
    _hdr = "第【1】集\n【质疑者配角】：楼下张叔\n【本集时长】：180 秒\n"
    f1, w1, _ = validate(_hdr + "【冲突形态】：行动型\n" + _act_body, profile="long")
    f2, w2, _ = validate(_hdr + _act_body, profile="long")
    if not any("E9" in x for x in w2) or not any("E21" in x for x in w2):
        print("FAIL self-test: 无形态标记的对白少年应报 E9/E21:", w2); ok = 0
    if any("E9" in x for x in w1) or any("E21" in x for x in w1):
        print("FAIL self-test: 行动型不应报 E9/E21:", w1); ok = 0
    # T6: 行动型动作拍权重（同一稿：标 150s，对话型应报 E16、行动型不应报）
    _t6 = ("第【1】集\n【质疑者配角】：张叔\n【本集时长】：150 秒\n[场景]：内景·楼顶\n[人物]：陈默、张叔\n"
           + "".join(f"△ 准备动作{i}：他把钢板一块块拧上去，火光四溅，处境又安全一层。\n" for i in range(20))
           + "".join(f"陈默：第{i}句台词，字数大概就是二十个字左右。\n" for i in range(20)))
    _fa, _, _ = validate(_t6, profile="long")
    _fb, _, _ = validate("【冲突形态】：行动型\n" + _t6, profile="long")
    if not any("E16" in x for x in _fa):
        print("FAIL self-test: 对话型台词少应报 E16"); ok = 0
    if any("E16" in x for x in _fb):
        print("FAIL self-test: 行动型不应报 E16（动作拍权重）×2.5:", [x for x in _fb if "E16" in x]); ok = 0
    # T7: 混合型中间档（6 行对白 / 低对白占比：对话型报 E9+E21，混合型不报）
    _t7 = ("第【1】集\n【质疑者配角】：张叔\n【本集时长】：150 秒\n[场景]：内景·楼顶\n[人物]：陈默、张叔\n"
           + "".join(f"△ 准备动作{i}：他把加固钢板一块块拧上去，火星四溅，处境又安全一层。\n" for i in range(14))
           + "".join(f"陈默：第{i}句话，说完我就接着干活。\n" for i in range(6)))
    _f7n, _w7n, _ = validate(_t7, profile="long")
    _f7m, _w7m, _ = validate("【冲突形态】：混合\n" + _t7, profile="long")
    if not any("E9" in x for x in _w7n) or not any("E21" in x for x in _w7n):
        print("FAIL self-test: 对话型应报 E9/E21:", _w7n); ok = 0
    if any("E9" in x for x in _w7m) or any("E21" in x for x in _w7m):
        print("FAIL self-test: 混合型不应报 E9/E21:", _w7m); ok = 0
    # T8: N13 豁免（行动型/混合型不报堆动作）
    _t8 = ("第【1】集\n【质疑者配角】：张叔\n[场景]：内景\n[人物]：陈默、张叔\n"
           + "".join("△ 他抬手。\n" for _ in range(14))
           + "张叔：你疯了。\n陈默：嗯。\n张叔：真的疯了。\n陈默：嗯。\n"
           + "【本集断章卡点】：门被风吹开，钢板在夜里晃了一下，灯灭了。（黑屏：下滑立即解锁第2集）\n")
    if not any("N13" in x for x in collect_notes(_t8, "long")):
        print("FAIL self-test: 对话型堆动作应报 N13"); ok = 0
    if any("N13" in x for x in collect_notes("【冲突形态】：行动型\n" + _t8, "long")):
        print("FAIL self-test: 行动型不应报 N13（堆动作豁免）"); ok = 0
    # T9: ②行动型的「反常动作」开场不应被 E4 误杀（对话型同文应报 E4）
    _t9 = ("第【1】集\n【本集时长】：150 秒\n[场景]：内景·楼道\n[人物]：陈默、张叔\n"
           "△ 他把三十箱矿泉水一箱箱搬上楼，垛在门口。\n"
           + "陈默：嗯。\n张叔：嗯。\n陈默：嗯。\n张叔：嗯。\n陈默：嗯。\n张叔：嗯。\n陈默：嗯。\n张叔：嗯。\n"
           "【本集断章卡点】：灯灭了，门却亮着。（黑屏：下滑解锁）\n")
    _f9a, _, _ = validate(_t9, profile="long")
    _f9b, _, _ = validate("【冲突形态】：行动坚持型\n" + _t9, profile="long")
    if not any("E4" in x for x in _f9a):
        print("FAIL self-test: 无形态标记时反常动作开场应报 E4"); ok = 0
    if any("E4" in x for x in _f9b):
        print("FAIL self-test: 行动型反常动作开场不应报 E4:", [x for x in _f9b if "E4" in x]); ok = 0

    # ---- E19 15秒窗口台词密度（v4.0·WARN 生产端建议）回归 ----
    # E19: 连续对白块 >95 字 → WARN（△动作行/独白/旁白即断点，重置累积）
    e19 = ("第【1】集\n[场景]：内景·堂·日\n[人物]：甲、乙\n△ 巴掌扇到半空被反手抓住。\n"
           + "".join(f"甲：第{i}轮连续攻防台词，把新证据新代价和施压一步一步讲透抬价压上。\n" for i in range(6))
           + "乙：我知道了。\n"
           + "【本集断章卡点】：满堂死寂，画面定住。（黑屏：下滑立即解锁第2集）\n")
    f, w, _ = validate(e19)
    if not any("E19" in x for x in w):
        print("FAIL self-test: 连续对白超95字应报 E19 WARN:", w); ok = 0
    # E19 反向：连续对白之间插 △动作行断点，每块均 <95 字 → 不应报 E19
    e19_ok = ("第【1】集\n[场景]：内景·堂·日\n[人物]：甲、乙\n△ 巴掌扇到半空被反手抓住。\n"
              "甲：第一轮连续攻防台词，把新证据新代价一步一步讲透抬价。\n△ 甲反手摁住对方手腕。\n"
              "乙：第二轮连续攻防台词，把新代价和施压一步一步讲透抬价。\n△ 乙后退半步。\n"
              "甲：第三轮连续攻防台词，把新证据一步一步讲透抬价压上。\n"
              "【本集断章卡点】：满堂死寂，画面定住。（黑屏：下滑立即解锁第2集）\n")
    f, w, _ = validate(e19_ok)
    if any("E19" in x for x in w):
        print("FAIL self-test: 带动作行断点的对白不应报 E19:", w); ok = 0

    # ---- E20 动作单段≤40字 / E21 对白动作黄金比（v4.2·WARN 软约束）回归 ----
    # E20 触发：单条 △ 镜头净字数 >40 → WARN
    e20 = ("第【1】集\n[场景]：内景·堂·日\n[人物]：甲、乙\n"
           "△ 特写：陈峰死死盯着桌上令牌上的九龙图腾，双腿剧烈发抖手机疯狂震动不停，来电显示父亲两个字整个人瘫软在地上再也站不起来。\n"
           "甲：跪下。\n乙：你敢。\n甲：闭嘴。\n乙：罢了。\n"
           "【本集断章卡点】：门被踹开，满堂死寂。（黑屏：下滑立即解锁第2集）\n")
    f, w, _ = validate(e20)
    if not any(x.startswith("E20 ") for x in w):
        print("FAIL self-test: 单条△动作>40字应报 E20 WARN:", w); ok = 0
    # E20/E21 双反向：△ 镜头均 ≤40 字 且 对白/动作比落在 25%~70% → 两者都不应报
    bal_ok = ("第【1】集\n[场景]：内景·堂·日\n[人物]：甲、乙\n△ 巴掌扇到半空被反手抓住。\n"
              "甲：你今天必须把这笔账给我算清楚。\n△ 甲反手摁住对方手腕。\n"
              "乙：我没什么好跟你算清楚的。\n△ 乙后退半步。\n"
              "甲：那就别怪我翻脸不认人。\n"
              "【本集断章卡点】：满堂死寂。（黑屏：下滑解锁）\n")
    f, w, _ = validate(bal_ok)
    if any(x.startswith("E20 ") for x in w):
        print("FAIL self-test: 短△镜头不应报 E20:", w); ok = 0
    if any(x.startswith("E21 ") for x in w):
        print("FAIL self-test: 均衡对白动作比不应报 E21:", w); ok = 0
    # E21 触发：对白占比 >70% → WARN
    e21_high = ("第【1】集\n[场景]：内景·堂·日\n[人物]：甲、乙\n△ 拍桌。\n"
                + "".join(f"甲：第{i}轮唇枪舌战，抛出新证据新代价并步步抬价施压。\n" for i in range(8))
                + "【本集断章卡点】：满堂死寂。（黑屏：下滑解锁）\n")
    f, w, _ = validate(e21_high)
    if not any(x.startswith("E21 ") and ">70%" in x for x in w):
        print("FAIL self-test: 对白占比>70%应报 E21 WARN:", w); ok = 0
    # E21 反向：对白占比 <25% → WARN（动作碾压、缺唇枪舌战）
    e21_low = ("第【1】集\n[场景]：内景·堂·日\n[人物]：甲、乙\n"
               + "".join(f"△ 第{i}拍具体物理动作，镜头可拍的行为事件推进冲突再升级。\n" for i in range(8))
               + "甲：来。\n"
               + "【本集断章卡点】：满堂死寂。（黑屏：下滑解锁）\n")
    f, w, _ = validate(e21_low)
    if not any(x.startswith("E21 ") and "<25%" in x for x in w):
        print("FAIL self-test: 对白占比<25%应报 E21 WARN:", w); ok = 0

    # ---- E24 单集配额【第一硬性规则】（场景数 + 人物数 ≤ N，默认 4）回归 ----
    # 2 场 + 4 人 = 6 > 4 → FAIL
    e24 = ("第【1】集\n[场景]：内景·客厅·日\n[场景]：内景·厨房·日\n"
           "[人物]：甲、乙、丙、丁\n△ 拍桌。\n甲：说。\n乙：说。\n丙：说。\n丁：说。\n"
           "【本集断章卡点】：满堂死寂。（黑屏：下滑解锁）\n")
    f, _, _ = validate(e24)
    if not any("E24" in x for x in f):
        print("FAIL self-test: 场景+人物>4 应报 E24"); ok = 0
    # 2 场 + 3 人 = 5 > 4 → 同样 FAIL（v4.5 旧边界 5 已收紧）
    f, _, _ = validate(e24.replace("[人物]：甲、乙、丙、丁", "[人物]：甲、乙、丙"))
    if not any("E24" in x for x in f):
        print("FAIL self-test: 场景+人物=5 应报 E24（默认已收紧为 4）"); ok = 0
    # 边界：2 场 + 2 人 = 4 → 不应报 E24
    f, _, _ = validate(e24.replace("[人物]：甲、乙、丙、丁", "[人物]：甲、乙"))
    if any("E24" in x for x in f):
        print("FAIL self-test: 场景+人物=4 不应报 E24:", [x for x in f if "E24" in x]); ok = 0
    # 边界：1 场 + 3 人 = 4 → 不应报 E24（长档常见构型）
    f, _, _ = validate(e24.replace("[场景]：内景·厨房·日\n", "")
                       .replace("[人物]：甲、乙、丙、丁", "[人物]：甲、乙、丙"))
    if any("E24" in x for x in f):
        print("FAIL self-test: 1场+3人=4 不应报 E24:", [x for x in f if "E24" in x]); ok = 0
    # --ref-images 0 关闭本项检查
    f, _, _ = validate(e24, ref_limit=0)
    if any("E24" in x for x in f):
        print("FAIL self-test: --ref-images 0 应关闭 E24"); ok = 0
    # 括号备注剔除后再计人物数：1 场 + 3 人（各带备注）= 4 → 不超
    _e24b = e24.replace("[场景]：内景·厨房·日\n", "").replace(
        "[人物]：甲、乙、丙、丁", "[人物]：甲（隐忍）、乙（嚣张）、丙（冷漠）")
    f, _, _ = validate(_e24b)
    if any("E24" in x for x in f):
        print("FAIL self-test: 括号备注应剔除后再计人物数:", [x for x in f if "E24" in x]); ok = 0

    # ---- 配额裁定（v4.5 第一规则配套）：长档集标注【配额裁定】配额优先 → 按 standard 交付，E11/E17 让位 ----
    ruled = ("第【1】集（长档·约3分钟）\n【配额裁定】：配额优先，本集压缩为 1 场 3 人，时长调整为 120 秒\n"
             "[场景]：内景·堂·日\n[人物]：甲、乙、丙\n△ 拍桌。\n甲：说。\n乙：说。\n丙：说。\n"
             "【本集时长】：120 秒\n【本集断章卡点】：满堂死寂。（黑屏：下滑解锁）\n")
    if resolve_profile(ruled) != "standard":
        print("FAIL self-test: 【配额裁定】长档应降级按 standard 识别"); ok = 0
    f, _, _ = validate(ruled)
    if any(("E17" in x) or ("E11" in x) for x in f):
        print("FAIL self-test: 配额裁定后 E17/E11 应让位:", f); ok = 0
    # 无裁定字段的长档标 120 秒 → E17 仍须 FAIL（裁定必须显式，不得默认发生）
    f, _, _ = validate(ruled.replace(
        "【配额裁定】：配额优先，本集压缩为 1 场 3 人，时长调整为 120 秒\n", ""))
    if not any("E17" in x for x in f):
        print("FAIL self-test: 无裁定字段的长档 120 秒仍应报 E17"); ok = 0

    print("[+] self-test PASSED" if ok else "[-] self-test FAILED")
    return 0 if ok else 1


def parse_args(args):
    """返回 (path, profile, prevs, ref_limit)；用法错误抛 SystemExit(2)"""
    path, profile, prevs, ref_limit = None, "auto", [], None
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--prev":
            i += 1
            while i < len(args) and not args[i].startswith("--"):
                prevs.append(args[i]); i += 1
            continue
        if a == "--long":
            profile = "long"
        elif a == "--manju":
            profile = "manju"
        elif a == "--format" or a.startswith("--format="):
            val = a.split("=", 1)[1] if "=" in a else (args[i + 1] if i + 1 < len(args) else "")
            if "=" not in a:
                i += 1
            if val not in PROFILES:
                print(f"[-] --format 只接受 {'/'.join(PROFILES)}，收到「{val}」"); raise SystemExit(2)
            profile = val
        elif a == "--ref-images" or a.startswith("--ref-images="):
            val = a.split("=", 1)[1] if "=" in a else (args[i + 1] if i + 1 < len(args) else "")
            if "=" not in a:
                i += 1
            if not val.isdigit():
                print(f"[-] --ref-images 需要非负整数（0=关闭），收到「{val}」"); raise SystemExit(2)
            ref_limit = int(val)
        elif a.startswith("--"):
            print(f"[-] 未知参数「{a}」"); raise SystemExit(2)
        elif path is None:
            path = a
        i += 1
    return path, profile, prevs, ref_limit


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); return 2
    if args[0] == "--self-test":
        return self_test()
    try:
        path, profile, prevs, ref_limit = parse_args(args)
    except SystemExit as e:
        return e.code or 2
    if not path:
        print(__doc__); return 2
    # 友好处理缺文件/编码错误（避免裸 traceback）
    try:
        text = open(path, encoding="utf-8").read()
    except FileNotFoundError:
        print(f"[-] 找不到剧本文件: {path}"); return 2
    except IsADirectoryError:
        print(f"[-] 路径是目录，不是剧本文件: {path}"); return 2
    except UnicodeDecodeError:
        print(f"[-] 文件不是 UTF-8 文本，无法读取: {path}"); return 2
    except OSError as e:
        print(f"[-] 无法读取剧本文件: {path}（{e}）"); return 2
    for p in prevs:
        try:
            open(p, encoding="utf-8").read()
        except FileNotFoundError:
            print(f"[-] 找不到前集文件: {p}"); return 2
        except (UnicodeDecodeError, OSError):
            print(f"[-] 无法读取前集文件: {p}"); return 2
    prev_texts = [open(p, encoding="utf-8").read() for p in prevs]
    profile_in = profile
    profile = resolve_profile(text, profile)
    fails, warns, nc = validate(text, prev_texts, profile, ref_limit)
    notes = collect_notes(text, profile)
    print(f"== {path}  [{profile} {PROFILES[profile]['label']}]  正文体量≈{nc} ==")
    if profile_in != profile and profile == "standard" and quota_ruling(text):
        print("   【配额裁定】第一硬性规则生效：保配额（场景+人物≤4），本集时长/档位已调整，按 standard 交付")
    _rl = REF_IMAGE_LIMIT if ref_limit is None else ref_limit
    if _rl:
        _sc, _ppl = scene_count(text), roster_count(text)
        print(f"   单集配额：场景 {_sc} + 人物 {_ppl} = {_sc + _ppl} / {_rl}（第一硬性规则，优先于时长）")
    for x in fails:
        print("[-] FAIL:", x)
    for x in warns:
        print("[!] WARN:", x)
    for x in notes:
        print("[i] NOTE:", x, "  ← 保护性反例，不要求修改")
    if fails:
        print("结果: FAILED（修复后重跑）"); return 1
    tail = []
    if warns:
        tail.append("含 WARN 请复核")
    if notes:
        tail.append("含 NOTE（非缺陷，勿过度修正）")
    print("结果: PASSED" + ("（" + "；".join(tail) + "）" if tail else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
