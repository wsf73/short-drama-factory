#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""export_net_band.py —— 批量导出各集「正文净字数 vs 动态参考带」对照表。

用途（连写时的高频痛点）：
  E1 体量参考带是**按每集自报的【本集时长】动态推导**的（对话型 t×5.0~7.6、
  混合 t×4.2~6.5、行动型 t×3.5~5.5）。写一集跑一次 validate_episode 只能看到
  「这一集超/低于参考带」，看不到**全体集数与带的关系**，于是「差 3 个字」这类
  问题要来回改好几轮。本脚本一次把所有集的 nc / 带宽 / 缺口 / 对白占比全列出来，
  哪集差几个字、差在哪一项，一眼看全，一轮改完。

用法：
  python scripts/export_net_band.py <episodes 目录或单个剧本文件> [--format standard]
  python scripts/export_net_band.py <目录> --csv out.csv     # 另存 CSV 便于比对

输出列：
  EP       集号（取文件名里的数字）
  时长     剧本自报的【本集时长】(秒)
  净字数   net_chars()：对白 + 独白/旁白 + △动作 + 断章画面（剔除【】字段行与 [场景]/[人物] 行）
  参考带   net_band()：按【本集时长】与冲突形态动态推导的 lo~hi
  缺口    净字数 - lo（负数 = 还差多少字才够下限；正数 = 已在线内）
  对白占比 E21 口径：对白净字数 /（对白净字数 + △动作净字数）× 100%，安全区 25%~70%
  最长对白块 E19 口径：连续对白块的最大净字数（上限 95）
  判定     OK / 低于下限 / 高于上限（与 E1 的 WARN 口径一致）

退出码：全部落在参考带内 → 0；有任一集出带 → 1（便于 CI / 批量脚本串联）。
"""
import argparse
import csv
import glob
import importlib.util
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load_validator():
    """复用 validate_episode.py 的 net_chars / net_band / _is_dialogue / _vo_line，
    保证本脚本与机检口径**永远同源**（改了机检，这里自动跟着变）。"""
    path = os.path.join(_HERE, "validate_episode.py")
    spec = importlib.util.spec_from_file_location("_sdv", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _strip(body):
    return re.sub(r"[\s，。！？；：、…—\-·“”\"'‘’（）()《》!?.]", "", body)


def collect(path, fmt="standard"):
    """返回单集指标 dict。"""
    v = _load_validator()
    with open(path, encoding="utf-8") as f:
        text = f.read()
    nc = v.net_chars(text)
    lo, hi = v.net_band(text, fmt)
    m = re.search(r"【本集时长】[：:]\s*(\d+)", text)
    dur = int(m.group(1)) if m else 0

    dlg_total = act_total = 0
    run = longest = 0
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("△"):
            act_total += len(_strip(re.sub(r"^△\s*", "", s)))
            longest = max(longest, run)
            run = 0
            continue
        vo = v._vo_line(s)
        if vo is not None:
            longest = max(longest, run)
            run = 0
            continue
        d = v._is_dialogue(s)
        if d is not None:
            dlg_total += len(_strip(d))
            run += len(_strip(d))
            continue
        longest = max(longest, run)
        run = 0
    longest = max(longest, run)

    denom = dlg_total + act_total
    pct = int(round(dlg_total / denom * 100)) if denom else 0
    gap = nc - lo
    verdict = "OK"
    if nc < lo:
        verdict = f"低于下限 {lo - nc} 字"
    elif nc > hi:
        verdict = f"高于上限 {nc - hi} 字"
    return {
        "ep": os.path.basename(path),
        "dur": dur, "nc": nc, "lo": lo, "hi": hi, "gap": gap,
        "dlg": dlg_total, "act": act_total, "pct": pct,
        "longest": longest, "verdict": verdict,
    }


def gather(target):
    if os.path.isdir(target):
        files = sorted(glob.glob(os.path.join(target, "*.md")))
    else:
        files = [target]
    return [f for f in files if os.path.isfile(f)]


def main():
    ap = argparse.ArgumentParser(description="批量导出正文净字数 vs 动态参考带")
    ap.add_argument("target", help="episodes 目录或单个剧本文件")
    ap.add_argument("--format", default="standard",
                    choices=["auto", "standard", "long", "manju"])
    ap.add_argument("--csv", default=None, help="另存 CSV 路径")
    args = ap.parse_args()

    rows = [collect(f, args.format) for f in gather(args.target)]
    if not rows:
        print("未找到可解析的剧本文件：", args.target)
        return 2

    head = f"{'EP':<10}{'时长':>6}{'净字数':>8}{'参考带':>14}{'缺口':>8}{'对白占比':>10}{'最长对白块':>12}  判定"
    print(head)
    print("-" * len(head))
    bad = 0
    for r in rows:
        band = f"{r['lo']}~{r['hi']}"
        flag = "" if r["verdict"] == "OK" else "  <-- 需处理"
        if r["verdict"] != "OK":
            bad += 1
        warn19 = "  E19!" if r["longest"] > 95 else ""
        warn21 = ""
        if r["pct"] > 70:
            warn21 = "  E21>70%"
        elif r["pct"] < 25:
            warn21 = "  E21<25%"
        print(f"{r['ep'][:9]:<10}{r['dur']:>6}{r['nc']:>8}{band:>14}{r['gap']:>+8}"
              f"{str(r['pct']) + '%':>10}{r['longest']:>12}{warn19}{warn21}{flag}")

    print("-" * len(head))
    ok = len(rows) - bad
    print(f"合计 {len(rows)} 集：落在参考带内 {ok} 集，出带 {bad} 集")
    if bad:
        print("提示：出带集直接看「缺口」列——差几字就补几字；补对白（涨体量也涨对白占比）"
              "优先于补 △ 行（只涨体量，可能压垮 E21 下限）。")

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print("CSV 已写入：", args.csv)

    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
