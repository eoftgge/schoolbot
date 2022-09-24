import re

COMPILED_CODE = re.compile(r"edu\.skysmart\.ru\/student\/(\S+)")


def get_task_code(link_or_code: str) -> str:
    if hash_code := COMPILED_CODE.findall(link_or_code):
        return hash_code[0]
    return link_or_code
