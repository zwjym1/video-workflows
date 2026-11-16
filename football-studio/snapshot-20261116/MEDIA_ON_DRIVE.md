# 大媒体与已归档网盘指针

本源码快照**不包含**对标原片、成片、独立混音长音频、解码大图帧或巨型 cache。这些已在同一 Google Drive 文件夹，请用稳定文件 ID 访问，不要为 GitHub 再上传。

文件夹：[https://drive.google.com/drive/folders/1ESUqsHNUNQJTGpkROGVv_QLL-ub4FKbz](https://drive.google.com/drive/folders/1ESUqsHNUNQJTGpkROGVv_QLL-ub4FKbz)  
文件夹 ID：`1ESUqsHNUNQJTGpkROGVv_QLL-ub4FKbz`

## 合并工程包 / 对标资料包

`cursor.UploadFile` 单文件上限 100 MB，因此完整工程 zip 与对标 zip 以 90 MiB 分卷保存。下载全部分卷后，在该文件夹运行 `JOIN_ARCHIVES.sh` 或 `JOIN_ARCHIVES.ps1`，再校验：

- `03_最新制作工程_full-phase-production.zip`：307466937 字节，SHA256 `5aad172427b01dc290773866f3844d2533203ef3d3f6122e965899c931332199`，分卷 4 个。
- `04_对标视听与分析资料.zip`：387575458 字节，SHA256 `d0a78d5b523715008a51310f3dd5138e279726cdee7ccb615b4b4cca67c1b430`，分卷 5 个。

## 关键对象

| 对象 | Drive 文件 | 文件 ID | SHA256（本地归档时） |
| --- | --- | --- | --- |
| 最新成片主版 99.36s（可直接预览） | [01_最新成片主版_arsenal_full_phase_main.mp4](https://drive.google.com/file/d/1KCp9qu0lL_n6golZMOgn0lJRfOSr2yz1/view?usp=drivesdk) | `1KCp9qu0lL_n6golZMOgn0lJRfOSr2yz1` | `8c7a245b35b70e2f3369516fa42280e79cc3b306f322967e1092c64781bab287` |
| 完整知识库 zip（媒体归档，与本快照内源码目录并行） | [02_完整知识库_football-knowledge-base.zip](https://drive.google.com/file/d/1FZKelr76kFXfOFFt6rQ2-CxtWqXuMlwP/view?usp=drivesdk) | `1FZKelr76kFXfOFFt6rQ2-CxtWqXuMlwP` | `02320e2b2f35bf225af612eacc2c844b1e00b12edf622bd561671496fbf28f51` |

完整逐文件原路径与 sha256 还记载于同文件夹已有的 `MANIFEST.json`（媒体归档）以及本快照内的 `MANIFEST.json`（源码清单）。精修方案 9 个文件（`05_双对标精修_*`）已在该目录，本轮不再重复上传；其源码/文字也收录在本 zip 的 `football-demo/two-reference-refinement/`，便于 Git 提交。

参考原片仅为私有学习存档，不是独立版权资产，不能当作可再发布母版。
