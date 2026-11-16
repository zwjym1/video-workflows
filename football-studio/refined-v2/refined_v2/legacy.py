"""2018 阿森纳对莱斯特回归包允许出现的身份。其它场次一律拒绝。"""

KNOWN_IDS = {
    "A19", "A16", "A34", "A11", "A10", "A29", "A2", "A17", "A9", "A14", "A20",
    "L14", "L10", "L24", "L3", "L25", "L15", "L6", "L1", "L18",
    "F1", "F2",
}

# 长名字放前面，扫描时仍按子串判断。
KNOWN_TOKENS = (
    "奥巴梅扬",
    "拉卡泽特",
    "穆斯塔菲",
    "贝莱林",
    "托雷拉",
    "贡多齐",
    "伊沃比",
    "佩雷拉",
    "麦迪逊",
    "霍尔丁",
    "厄齐尔",
    "阿森纳",
    "莱斯特",
    "扎卡",
    "奥巴",
    "门迪",
    "莱诺",
)

EXTRA_SUFFIXES = ("_origin", "_next")


def regression_id_allowed(identifier: str) -> bool:
    if identifier in KNOWN_IDS:
        return True
    for suffix in EXTRA_SUFFIXES:
        if identifier.endswith(suffix) and identifier[: -len(suffix)] in KNOWN_IDS:
            return True
    return False


def find_legacy(text: str):
    """返回出现在文本里的旧场次身份。按完整编号匹配，避免 A2 命中 A20。"""
    import re

    found = []
    for identifier in sorted(KNOWN_IDS, key=len, reverse=True):
        if re.search(rf"(?<![A-Za-z0-9]){re.escape(identifier)}(?![A-Za-z0-9])", text):
            found.append(identifier)
    for token in KNOWN_TOKENS:
        if token in text:
            found.append(token)
    return found
