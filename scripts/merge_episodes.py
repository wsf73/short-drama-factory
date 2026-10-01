#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""merge_episodes.py —— 把散装分集正文合并成一份合订剧本（连写收尾的最后一步）。

用法
----
    python scripts/merge_episodes.py <episodes 目录> \
        [--title "剧名"] \
        [--header 自定义头部.md] \
        [--plan 02-分集规划-80集.md] \
        [--outdir 输出目录] \
        [--clean-only]

产出（默认写到 episodes 的父目录）
----
    1) <剧名>全<N>集合订剧本.md    —— 完整版：保留全部制作字段，供导演端转分镜提示词
    2) <剧名>纯正文版-<N>集.md      —— 阅读版：剔除制作字段，只留场景/人物/动作/对白/独白/断章

设计要点
----
* 集数、集名、时长全部**从正文里读**（不依赖规划文件），所以正文改了合订就是新的。
* 阅读版剔除的字段由 `META_PREFIX` 定义；正文里的 `[场景]` / `[人物]` 行**保留**（阅读也要用），
  只是转成 markdown 粗体；`【本集断章卡点】` 保留（它是剧本的一部分）。
* `--plan` 传入分集规划文件时，会自动抽取每集"核心冲突"列做成总目录摘要；不给也能跑。
* `--header` 传入自定义头部（如立项卡的人物圣经章节），会插在剧名之后、目录之前。

退出码：0 成功；1 未找到任何 EP*.md。
"""
import argparse
import os
import re
import sys

# 阅读版要剔除的制作字段（每集元数据块）
META_PREFIX = (
    "【所属阶段】", "【黄金前3秒钩子】", "【冲突形态】", "【情绪流变】",
    "【本集物证】", "【质疑者配角】", "【本集执念】", "【对手要什么】",
    "【本集主角主动目标】", "【本集改变了什么】", "【本集结算】", "【本集时长】",
)

EP_RE = re.compile(r"^EP(\d+)\.md$", re.I)
TITLE_RE = re.compile(r"^第【(\d+)】集[：:]\s*【(.+?)】")
DUR_RE = re.compile(r"【本集时长】[：:]\s*(\d+)")


def collect(epdir):
    """按集号排序读入所有 EP*.md。"""
    files = []
    for name in os.listdir(epdir):
        m = EP_RE.match(name)
        if m:
            files.append((int(m.group(1)), os.path.join(epdir, name)))
    files.sort()
    eps = []
    for n, path in files:
        with open(path, encoding="utf-8") as f:
            text = f.read().strip()
        lines = text.splitlines()
        m = TITLE_RE.match(lines[0].strip()) if lines else None
        title = m.group(2) if m else ""
        d = DUR_RE.search(text)
        eps.append({
            "n": n,
            "title": title,
            "dur": int(d.group(1)) if d else 0,
            "lines": lines[1:] if lines else [],   # 剔除原首行标题（由 ## 标题承担）
            "raw": text,
        })
    return eps


def plan_map(path):
    """从分集规划表里抽每集核心冲突（第 3 列）。"""
    out = {}
    if not path or not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^\|\s*(\d+)\s*\|([^|]*)\|([^|]*)\|", line)
            if m:
                out[int(m.group(1))] = m.group(3).strip()
    return out


def clean_ep(ep):
    """阅读版：剔制作字段，保留场景/人物/动作/对白/独白/断章。"""
    keep = []
    for line in ep["lines"]:
        s = line.strip()
        if not s:
            continue
        if TITLE_RE.match(s) or s.startswith("第【"):
            continue
        if s.startswith(META_PREFIX):
            continue
        if s.startswith("[场景]"):
            keep.append("**" + s.replace("[场景]", "场景").replace("：", "**：", 1))
            continue
        if s.startswith("[人物]"):
            keep.append("**" + s.replace("[人物]", "人物").replace("：", "**：", 1))
            continue
        keep.append(s)
    return "\n".join(keep)


def build(eps, title, header, plan, total):
    head = [f"# {title} · 全 {len(eps)} 集合订剧本", ""]
    head.append(
        f"> **集数**：{len(eps)} 集 ｜ **总时长**：{total} 秒 ≈ **{total / 60:.1f} 分钟**"
        f" ｜ 平均 {total / max(len(eps), 1):.1f} 秒/集"
    )
    head.append("")
    if header:
        head.append(header.strip())
        head.append("")

    # 目录
    head.append("---")
    head.append("")
    head.append("## 全剧目录")
    head.append("")
    if plan:
        head.append("| 集 | 集名 | 核心冲突 | 时长 |")
        head.append("|---|---|---|---|")
        for e in eps:
            head.append(f"| {e['n']:02d} | {e['title']} | {plan.get(e['n'], '')} | {e['dur']} 秒 |")
    else:
        head.append("| 集 | 集名 | 时长 |")
        head.append("|---|---|---|")
        for e in eps:
            head.append(f"| {e['n']:02d} | {e['title']} | {e['dur']} 秒 |")
    head.append("")

    # 完整版正文
    full_sec = ["---", "", "## 剧本正文", "",
                "> 每集含制作字段（所属阶段／黄金前3秒钩子／冲突形态／情绪流变／物证／质疑者配角／"
                "执念／对手要什么／主角目标／本集改变了什么／结算／时长），可直接投喂导演端转分镜提示词。", ""]
    full_body = []
    for e in eps:
        h = f"## 第{e['n']:02d}集 · {e['title']}"
        full_body.append(h + "\n\n" + "\n".join(e["lines"]).strip())

    # 阅读版正文
    clean_sec = ["---", "", "## 剧本正文（阅读版）", "",
                 "> 已剔除制作字段，只保留场景、人物、动作、对白、独白与断章卡点。", ""]
    clean_body = []
    for e in eps:
        h = f"## 第{e['n']:02d}集 · {e['title']}"
        clean_body.append(h + "\n\n" + clean_ep(e))

    full = "\n".join(head) + "\n" + "\n".join(full_sec) + "\n\n" + "\n\n---\n\n".join(full_body) + "\n"
    clean = "\n".join(head) + "\n" + "\n".join(clean_sec) + "\n\n" + "\n\n---\n\n".join(clean_body) + "\n"
    return full, clean


def main():
    ap = argparse.ArgumentParser(description="合并分集正文为合订剧本")
    ap.add_argument("epdir", help="episodes 目录")
    ap.add_argument("--title", default=None, help="剧名（默认取 episodes 的父目录名）")
    ap.add_argument("--header", default=None, help="自定义头部 md（插在剧名后、目录前）")
    ap.add_argument("--plan", default=None, help="分集规划文件（用于生成目录摘要）")
    ap.add_argument("--outdir", default=None, help="输出目录（默认 episodes 的父目录）")
    ap.add_argument("--clean-only", action="store_true", help="只输出阅读版")
    args = ap.parse_args()

    epdir = os.path.abspath(args.epdir)
    if not os.path.isdir(epdir):
        print(f"[X] 不是目录：{epdir}")
        return 1
    eps = collect(epdir)
    if not eps:
        print(f"[X] 在 {epdir} 下没找到 EP*.md")
        return 1

    parent = os.path.dirname(epdir)
    title = args.title or os.path.basename(parent) or "合订剧本"
    outdir = os.path.abspath(args.outdir) if args.outdir else parent
    os.makedirs(outdir, exist_ok=True)

    header = None
    if args.header and os.path.exists(args.header):
        with open(args.header, encoding="utf-8") as f:
            header = f.read()
    plan = plan_map(args.plan) if args.plan else {}
    total = sum(e["dur"] for e in eps)

    full, clean = build(eps, title, header, plan, total)

    made = []
    if not args.clean_only:
        p1 = os.path.join(outdir, f"{title}全{len(eps)}集合订剧本.md")
        with open(p1, "w", encoding="utf-8") as f:
            f.write(full)
        made.append(("完整版", p1, len(full)))
    p2 = os.path.join(outdir, f"{title}纯正文版-{len(eps)}集.md")
    with open(p2, "w", encoding="utf-8") as f:
        f.write(clean)
    made.append(("阅读版", p2, len(clean)))

    print(f"集数 {len(eps)}  总时长 {total} 秒 = {total / 60:.1f} 分钟  平均 {total / len(eps):.1f} 秒/集")
    for tag, path, size in made:
        print(f"{tag}  {path}  {size} 字符")
    return 0


if __name__ == "__main__":
    sys.exit(main())
