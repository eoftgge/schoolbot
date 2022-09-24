import base64

from typing import List
from logging import getLogger
from bs4.element import Tag, NavigableString

from ...skysmart.models.xml import ExerciseXml, ExerciseMeta

logger = getLogger(__name__)


class XmlParser:
    def __init__(self, xml: ExerciseXml, exercise: ExerciseMeta):
        self._result = str()
        self._xml = xml
        self._list_of_nodes: List[Tag] = self._xml.soup.div
        self._exercise = exercise

    def get_result(self) -> str:
        return self._result

    def push_ident(self) -> "XmlParser":
        self._result += "\n"
        return self

    def set_info_task(self, number: int) -> "XmlParser":
        self._result += f"""
Информация о задании №{number}:
UUID - {self._xml.uuid}
TaskID - {self._xml.exercise_id}
IsRandom - {"Да" if self._xml.is_random else "Нет"}
IsInteractive - {"Да" if self._xml.is_interactive else "Нет"}
        """.strip()
        return self

    def set_title(self, number: int) -> "XmlParser":
        self._result += f"Задание №{number} ({self._xml.title})\n"
        return self

    def set_result(self, number: int) -> "XmlParser":
        self.set_title(number)

        for node in self._list_of_nodes:
            if isinstance(node, NavigableString) or node.is_empty_element:
                continue

            logger.debug(f"Node: {node}")

            match node.name:
                case "vim-iframe":
                    self._result += "К сожалению эта видеоигра, мы не умеем решать это\n"
                case "vim-groups":
                    self.set_groups(node)
                case "vim-test":
                    self.set_test(node)
                case "vim-input":
                    self.set_input(node)
                case "vim-select":
                    self.set_select(node)
                case "vim-dnd-text":
                    self.set_dnd_text(node)

            if vim_input_many := node.find_all("vim-input"):
                for vim_input in vim_input_many:
                    self.set_input(vim_input)
            elif vim_select_many := node.find_all("vim-select"):
                for vim_select in vim_select_many:
                    self.set_select(vim_select)

        return self

    def set_groups(self, node: Tag) -> "XmlParser":
        for vim in node.find_all("vim-groups-row"):
            items = vim.find_all("vim-groups-item")
            one = base64.decodebytes(items[0]["text"].encode("utf-8"))
            two = base64.decodebytes(items[1]["text"].encode("utf-8"))
            self._result += f"Сопоставьте «{one.decode('utf-8')}» -> «{two.decode('utf-8')}»\n"

        return self

    def set_test(self, node: Tag) -> "XmlParser":
        number = 1
        self._result += node.find("vim-test-question-text").get_text(strip=True).removesuffix(".") + ":\n"

        for answer in node.find_all("vim-test-item", correct=True):
            self._result += f"{number} - {answer.get_text()}\n"
            number += 1

        return self

    def set_input(self, node: Tag) -> "XmlParser":
        if node.is_empty_element:
            return

        list_of_inputs = []

        for answer in node.find_all("vim-input-item"):
            list_of_inputs.append(answer.get_text(strip=True))

        self._result += "Введи: " + " ИЛИ ".join(list_of_inputs) + "\n"
        return self

    def set_select(self, node: Tag) -> "XmlParser":
        element = node.find("vim-select-item", correct=True).find("vim-select-item-title").get_text(strip=True)
        self._result += f"Выбери: {element}\n"
        return self

    def set_dnd_text(self, node: Tag) -> "XmlParser":
        number = 1
        drags: Tag = node.find("vim-dnd-text-drags")
        nodes: List[Tag] = node.find_all("vim-dnd-text-drop")

        for item in nodes:
            ids = item.get("drag-ids").split(",")
            list_of_ids = []

            for answer_id in ids:
                list_of_ids.append(drags.find(attrs={"answer-id": answer_id}).get_text())

            self._result += f"{number} - {' /ИЛИ/ '.join(list_of_ids)}\n"
            number += 1

        return self


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

    def set_info_room(self) -> "ExerciseParser":
        self._result += f"""
Информация о комнате:
ФИ учителя - {self._exercise.meta.teacher.name}
Предмет - {self._exercise.meta.subject.title}
Ссылка на задание - <a href="{self.get_link()}">жмяк</a>
        """.strip()
        return self

    def get_xml_parser(self, xml: ExerciseXml) -> XmlParser:
        return XmlParser(xml, exercise=self._exercise)
