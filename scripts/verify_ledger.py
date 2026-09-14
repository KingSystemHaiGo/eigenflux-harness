#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_ledger.py — 校验 ef-harness 贡献账本（治理宪章 G8：记录不可篡改）

校验三件事：
  1. 每行能解析、必需字段齐全
  2. 每行 chain_digest == sha256(canonical(本行去掉 digest/chain_digest))
  3. prev_digest 与上一行的 digest 串链一致（链不裂）
任何 agent 都可以跑它复核——这就是"可被第三方审查"的实现。

用法：python3 scripts/verify_ledger.py [--ledger ledger.jsonl]
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path


def canon(o: dict) -> bytes:
    return json.dumps(o, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def digest_of(row: dict) -> str:
    body = {k: v for k, v in row.items() if k not in ("digest", "chain_digest")}
    return hashlib.sha256(canon(body)).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default=str(Path(__file__).resolve().parent.parent / "ledger.jsonl"))
    args = ap.parse_args()

    lines = [l for l in Path(args.ledger).read_text().splitlines() if l.strip()]
    if not lines:
        print("FAIL: 账本为空")
        return 1

    prev = ""
    bad = 0
    for i, line in enumerate(lines, 1):
        try:
            row = json.loads(line)
        except Exception as e:
            print(f"FAIL line {i}: JSON 解析失败 {e}")
            bad += 1
            continue
        for f in ("ts", "who", "event"):
            if f not in row:
                print(f"FAIL line {i}: 缺字段 {f}")
                bad += 1
        got = row.get("chain_digest") or row.get("digest", "")
        want = digest_of(row)
        if got != want:
            print(f"FAIL line {i}: digest 不符 got={got[:16]}… want={want[:16]}…")
            bad += 1
        if row.get("prev_digest", "") != prev:
            print(f"FAIL line {i}: 链断裂 prev={str(row.get('prev_digest'))[:16]}… 期望={prev[:16]}…")
            bad += 1
        prev = got

    print(f"审计结果：{len(lines)} 行，{'全部通过 ✅' if bad == 0 else f'{bad} 处异常 ❌'}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
