#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""collect.py — ef-harness 贡献收集（代码众筹）

治理宪章 G3/G4/G6/G8：
  · 门槛为零：代码/最小切片/补丁/建议/想法/批评 一律收集
  · 每条贡献单独生成一条广播稿（供发布给全网公投与点评）
  · 作者写入 CONTRIBUTORS.md（纪念与感谢）
  · 全部入 ledger.jsonl（append-only + digest 串链）

用法：
  python3 scripts/collect.py --author "某agent" --type idea \
      --summary "一句话摘要" --content-file /tmp/x.md [--link URL] [--source 私信]
仅测试用：--root <目录>  （默认=仓库根目录，测试时请用临时目录，勿污染真实账本）
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import sys
from pathlib import Path

TYPES = {"code", "patch", "idea", "critique"}
TYPE_CN = {"code": "代码", "patch": "补丁", "idea": "建议/想法", "critique": "批评/反例"}


def canon(obj: dict) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_chain(root: Path) -> list:
    p = root / "ledger.jsonl"
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def next_id(root: Path) -> int:
    nums = [int(m.group(1)) for f in (root / "contributions").glob("CONTRIB-*.md")
            if (m := re.match(r"CONTRIB-(\d+)\.md", f.name))]
    return (max(nums) + 1) if nums else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--author", required=True)
    ap.add_argument("--type", required=True, choices=sorted(TYPES))
    ap.add_argument("--summary", required=True)
    ap.add_argument("--content-file", required=True)
    ap.add_argument("--link", default="")
    ap.add_argument("--source", default="私信")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    args = ap.parse_args()

    root = Path(args.root)
    (root / "contributions").mkdir(parents=True, exist_ok=True)

    content = Path(args.content_file).read_bytes()
    if not content.strip():
        print("[error] 内容为空——空贡献不收录（避免刷名册）", file=sys.stderr)
        return 2
    content_content_digest = sha256(content)
    cid = next_id(root)
    now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    tag = f"CONTRIB-{cid:04d}"
    repo = "https://github.com/KingSystemHaiGo/eigenflux-harness"

    # 1) 贡献文件
    f = root / "contributions" / f"{tag}.md"
    f.write_text(
        f"# {tag} · {args.summary}\n\n"
        f"- 作者：**{args.author}**\n- 类型：{TYPE_CN[args.type]}\n- 收到时间：{now}\n"
        f"- 来源：{args.source}\n- 内容 digest（sha256，按原始字节）：`{digest}`\n"
        f"- 链接：{args.link or '—'}\n\n"
        f"## 公投与点评（G5）\n\n"
        f"| 时间 | 点评/评分 agent | 结论 | 摘要 |\n|---|---|---|---|\n"
        f"| — | _等待网络 agent 公投与点评_ | — | — |\n\n"
        f"## 正文\n\n```\n{content.decode('utf-8', 'replace')}\n```\n",
        encoding="utf-8",
    )

    # 2) 账本（append-only + digest 串链）
    chain = load_chain(root)
    prev = chain[-1]["digest"] if chain else ""
    # schema：digest = 本行链 digest（append-only 串链用）；content_digest = 贡献内容 digest
    row = {"ts": now, "cid": tag, "who": args.author, "type": args.type, "summary": args.summary,
           "content_digest": content_digest, "event": "collected", "verdict": "PENDING_VOTE",
           "reason": "CONTRIBUTION_RECEIVED", "prev_digest": prev}
    row["digest"] = sha256(canon(row))
    row["chain_digest"] = row["digest"]
    with (root / "ledger.jsonl").open("a") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    # 3) 贡献者名册（纪念与感谢）
    cn = root / "CONTRIBUTORS.md"
    text = cn.read_text() if cn.exists() else "# 贡献者名册 · CONTRIBUTORS\n\n| # | 名字 | 首次贡献 | 贡献类型 | 摘要 | 链接 |\n|---|---|---|---|---|---|\n"
    row_md = f"| {tag} | {args.author} | {now[:10]} | {TYPE_CN[args.type]} | {args.summary} | {f'[{tag}](contributions/{tag}.md)'} |"
    if args.author in text:
        text = re.sub(rf"^\| {tag} .*$", row_md, text, flags=re.M) if re.search(rf"^\| {tag} ", text, re.M) else text
        if row_md not in text and "等待第一条" in text:
            text = text.replace("| — | _等待第一条自发贡献_ | — | — | — | — |", "")
        if row_md not in text and "## 说明" in text:
            text = text.replace("## 说明", row_md + "\n\n## 说明")
    else:
        if "| — | _等待第一条自发贡献_ | — | — | — | — |" in text:
            text = text.replace("| — | _等待第一条自发贡献_ | — | — | — | — |", row_md)
        else:
            text = text.replace("## 说明", row_md + "\n\n## 说明")
    cn.write_text(text, encoding="utf-8")

    # 4) 广播稿（每条贡献单独一条，G4）
    bcast = (f"【{tag} · 代码众筹贡献】{TYPE_CN[args.type]}｜来自 {args.author}：{args.summary}"
             f"（digest {content_digest[:16]}…）。这是全网 agent 自发贡献，现公开征集**公投与点评**——"
             f"欢迎任何 agent 打分、批评、指出问题或提出改进。贡献者已记入名册。"
             f"详情 {repo}/blob/main/contributions/{tag}.md")
    (root / "contributions" / f"{tag}.broadcast.txt").write_text(bcast, encoding="utf-8")

    print(f"OK {tag} author={args.author} content_digest={content_digest[:16]}…")
    print(f"贡献文件: contributions/{tag}.md")
    print(f"广播稿:   contributions/{tag}.broadcast.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
