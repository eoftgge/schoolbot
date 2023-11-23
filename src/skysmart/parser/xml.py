import base64

from typing import List, Self
from logging import getLogger
from bs4.element import Tag, NavigableString

from src.skysmart.models.xml import ExerciseXml, ExerciseMeta

logger = getLogger(__name__)


class XmlParser:
    def __init__(self, xml: ExerciseXml, exercise: ExerciseMeta):
        self._result = str()
        self._xml = xml
        self._list_of_nodes: List[Tag] = self._xml.soup.div
        self._exercise = exercise

    def get_result(self) -> str:
        return self._result

    def push_text(self, text: str):
        self._result += text + "\n"

    def set_title(self, number: int) -> Self:
        self.push_text(f"Задание №{number} ({self._xml.title.strip()}):")
        return self

    def set_result(self, number: int) -> Self:
        self.set_title(number)

        for node in self._list_of_nodes:
            if isinstance(node, NavigableString) or node.is_empty_element:
                continue

            logger.debug(f"Node ({node.name}): {node}")

            match node.name:
                case "vim-iframe":
                    self.push_text("К сожалению, этот вопрос является видеоигрой. Мы не умеем решать это")
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
                case "vim-strike-out":
                    self.set_strike_out_item(node)

            if vim_input_many := node.find_all("vim-input"):
                for vim_input in vim_input_many:
                    self.set_input(vim_input)
            elif vim_strike_many := node.find_all("vim-strike-out-item", striked=True):
                for vim_strike in vim_strike_many:
                    self.set_strike_out_item(vim_strike)
            elif vim_select_many := node.find_all("vim-select"):
                for vim_select in vim_select_many:
                    self.set_select(vim_select)

        return self

    def set_strike_out_item(self, node: Tag) -> Self:
        self.push_text(f"Зачеркни: {node.text}")
        return self

    def set_groups(self, node: Tag) -> Self:
        for vim in node.find_all("vim-groups-row"):
            items = vim.find_all("vim-groups-item")
            one = base64.decodebytes(items[0]["text"].encode("utf-8"))
            two = base64.decodebytes(items[1]["text"].encode("utf-8"))
            self.push_text(f"Сопоставьте «{one.decode('utf-8')}» -> «{two.decode('utf-8')}»")

        return self

    def set_test(self, node: Tag) -> Self:
        number = 1
        self.push_text(node.find("vim-test-question-text").get_text(strip=True).removesuffix(".") + ":")

        for answer in node.find_all("vim-test-item", correct=True):
            self.push_text(f"{number} - {answer.get_text()}")
            number += 1

        return self

    def set_input(self, node: Tag) -> Self:
        if node.is_empty_element:
            return

        list_of_inputs = []

        for answer in node.find_all("vim-input-item"):
            list_of_inputs.append(answer.get_text(strip=True))

        self.push_text("Введи: " + " ИЛИ ".join(list_of_inputs))
        return self

    def set_select(self, node: Tag) -> Self:
        element = node.find("vim-select-item", correct=True).find("vim-select-item-title").get_text(strip=True)
        self.push_text(f"Выбери: {element}")
        return self

    def set_dnd_text(self, node: Tag) -> Self:
        number = 1
        drags: Tag = node.find("vim-dnd-text-drags")
        nodes: List[Tag] = node.find_all("vim-dnd-text-drop")

        for item in nodes:
            ids = item.get("drag-ids").split(",")
            list_of_ids = []

            for answer_id in ids:
                list_of_ids.append(drags.find(attrs={"answer-id": answer_id}).get_text())

            self.push_text(f"{number} - {' /ИЛИ/ '.join(list_of_ids)}")
            number += 1

        return self
