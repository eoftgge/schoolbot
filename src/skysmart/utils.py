import re

from src.skysmart.models.xml import ExerciseMeta
from src.skysmart.parser.exercise import ExerciseParser
from src.skysmart.session import SkySmartSession

COMPILED_CODE = re.compile(r"edu\.skysmart\.ru/student/(\S+)")


def get_task_code(link_or_code: str) -> str:
    if hash_code := COMPILED_CODE.findall(link_or_code):
        return hash_code[0]
    return link_or_code


async def get_str_result(
    exercise: ExerciseMeta, code: str, session: SkySmartSession
) -> str:
    parser = ExerciseParser(code, exercise)

    for uuid in exercise.meta.uuids:
        number = parser.increment_number()
        xml = await session.get_answer_xml(uuid, exercise)
        xml_parser = parser.get_xml_parser(xml)
        xml_parser.set_result(number)
        parser.push_ident()
        parser.push_result(xml_parser.get_result())

    return parser.get_result()
