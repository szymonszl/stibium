import attr

@attr.s
class Message():
    mid = attr.ib()
    text = attr.ib()
    args = attr.ib(init=False)
    uid = attr.ib()
    thread_id = attr.ib()
    thread_type = attr.ib()
