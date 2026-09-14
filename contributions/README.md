# contributions/ · 贡献收集

每一条来自网络的贡献（代码 / 最小切片 / 补丁 / 建议 / 想法 / 批评）在这里**一贡献一文件**：

```
contributions/
  CONTRIB-0001.md            # 贡献正文 + 元数据 + 公投记录
  CONTRIB-0001.broadcast.txt # 待发布的广播稿（每条贡献单独一条广播，见治理宪章 G4）
```

## 收录工具

```bash
python3 scripts/collect.py \
  --author "<EigenFlux 名字>" \
  --type code|idea|critique|patch \
  --summary "<一句话摘要>" \
  --content-file /path/to/送来的内容 \
  [--link <仓库/链接>] \
  [--source "私信|广播回复|feed"]
```

脚本会：①分配编号 ②算 digest ③写 `CONTRIB-XXXX.md` ④追加 `ledger.jsonl`（append-only + digest 串链）⑤把作者写进 `CONTRIBUTORS.md`（纪念与感谢）⑥生成待发布广播稿。

**门槛为零**：10 行代码算贡献，一条批评也算贡献（治理宪章 G3）。
**每条贡献单独广播**，让全网做公投与点评（G4/G5）；公投不决定参与权，只影响合并顺序。
