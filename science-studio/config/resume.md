# 「继续上一期」操作步骤

1. `python3 /workspace/science-studio/scripts/state.py latest`：列出最新一期（按 `projects/INDEX.md` 和各期 `state.json.updated_at`）。用户点名编号时用那一期。
2. 读该期 `state.json`（以它为准）和 `STATE.md`：`stage`、`next_action`、`approved_decisions`、`script.latest`/`locked_paragraphs`、`storyboard.latest`、`shots[]` 状态、`failures[]`、`open_issues[]`。
3. 用 `ls`/`ffprobe` 核对 state 里写的文件真的存在；不一致就以磁盘为准修 state，并告诉用户。
4. 从 `next_action` 继续。已 `approved` 的稿、已 `done` 的镜头不重做；上游决策改了，按 `depends` 只重做受影响的下游。
5. 每完成一步：`state.py set <EP> <键> <值>` / `state.py log <EP> "<做了什么>"`，再刷新 `STATE.md`（脚本自动）。
6. 旧项目（`/workspace/optogenetics` 等，见 `projects/INDEX.md` 的 legacy 段）没有 state.json：要续做时先用 `new_episode.py --adopt <路径>` 建一期指向旧目录的 state，不搬文件。
