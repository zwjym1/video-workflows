class EpisodeRejected(Exception):
    """场次包不能渲染。调用方应把这句话交给操作者，不要改画旧场次。"""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")
