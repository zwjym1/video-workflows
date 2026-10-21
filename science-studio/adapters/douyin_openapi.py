"""抖音开放平台适配接口（stub，未接入）。
用户决定（2026-10-21）：个人号拿不到 video.list / video.data / data.external.item / item.comment 授权，本版不接。
正式数据源：创作者中心截图（scripts/ingest_screenshot.py）+ xlsx 导出（scripts/ingest_metrics.py）。
以后拿到授权：实现下面四个函数，返回值结构与 ingest_metrics.store() 的 metrics 字典一致（字段名见 ingest_metrics.COLS），
source 写「douyin_openapi:<接口名> <调用时间>」，verified=1（平台接口原值）。令牌只从环境变量/系统密钥读取，不写进仓库。
不得用 cookie、抓包签名或任何绕过授权的方式实现这些函数。"""

class NotAuthorized(Exception):
    """开放平台未授权（个人号目前申请不到相关 scope）。调用方应退回截图/xlsx 导入。"""

SCOPES = {"video.list": "作品列表", "video.data": "作品数据（播放/点赞/评论/分享）", "data.external.item": "作品分析（含均播、完播等）", "item.comment": "作品评论"}
_MSG = "抖音开放平台未授权（{scope}）：个人号拿不到该权限。请改用 ingest_screenshot.py（创作者中心截图）或 ingest_metrics.py（xlsx 导出）。"

def is_authorized() -> bool:
    return False

def list_videos(open_id: str | None = None, cursor: int = 0, count: int = 20):
    raise NotAuthorized(_MSG.format(scope="video.list"))

def video_data(item_ids: list[str]):
    raise NotAuthorized(_MSG.format(scope="video.data"))

def external_item(item_id: str, date_type: int = 7):
    raise NotAuthorized(_MSG.format(scope="data.external.item"))

def item_comments(item_id: str, cursor: int = 0, count: int = 50):
    raise NotAuthorized(_MSG.format(scope="item.comment"))
