from src.skysmart.models.xml import ExerciseMeta, ExerciseXml
from src.skysmart.parser.xml import XmlParser


class ExerciseParser:
    def __init__(self, code_task: str, exercise: ExerciseMeta):
        self._result = str()
        self._code_task = code_task
        self._exercise = exercise
        self._number = 0

    def get_result(self) -> str:
        return self._result

    def get_link(self) -> str:
        return f"https://edu.skysmart.ru/student/{self._code_task}"

    def increment_number(self) -> int:
        self._number += 1
        return self._number

    def push_ident(self) -> "ExerciseParser":
        self._result += "\n"
        return self

    def push_result(self, result: str) -> "ExerciseParser":
        self._result += result
        return self

    def get_xml_parser(self, xml: ExerciseXml) -> XmlParser:
        return XmlParser(xml, exercise=self._exercise)
