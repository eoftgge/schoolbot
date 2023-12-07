import base64
import itertools
from logging import getLogger
from typing import List, Self

from bs4.element import NavigableString, Tag

from src.skysmart.models.xml import ExerciseMeta, ExerciseXml

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
                    self.push_text(
                        r"К сожалению (или к счастью?), этот вопрос является видеоигрой. Бот неспособен решать это"
                    )
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
                case "vim-dnd-group":
                    self.set_dnd_group(node)
                case "vim-test-image":
                    self.set_test_image(node)

            if math_input_many := node.find_all("math-input"):
                for math_input in math_input_many:
                    self.set_math_input(math_input)  # ебучая матеша
            elif vim_input_many := node.find_all("vim-input"):
                for vim_input in vim_input_many:
                    self.set_input(vim_input)
            elif vim_strike_many := node.find_all("vim-strike-out-item", striked=True):
                for vim_strike in vim_strike_many:
                    self.set_strike_out_item(vim_strike)
            elif vim_select_many := node.find_all("vim-select"):
                for vim_select in vim_select_many:
                    self.set_select(vim_select)

        return self

    def set_test_image(self, node: Tag) -> Self:
        self.push_text("Выбери перечисленные варианты с текстами и картинками:")
        for number, item in zip(
            itertools.count(1), node.find_all("vim-test-image-item", correct=True)
        ):
            self.push_text(f"{number}) `{item.get_text(strip=True)}`")
        return self

    def set_dnd_group(self, node: Tag) -> Self:
        drags: dict[str, str] = {}
        for drag in node.find_all("vim-dnd-group-drag"):
            drags[drag["answer-id"]] = drag.get_text(strip=True)
        for group in node.find_all("vim-dnd-group-item"):
            self.push_text(
                "— "
                + group.find("vim-dnd-group-item-caption").get_text(strip=True)
                + ":"
            )
            for number, drag_id in zip(
                itertools.count(1), group["drag-ids"].split(",")
            ):
                self.push_text(f"{number}) `{drags[drag_id]}`")
        return self

    def set_math_input(self, node: Tag) -> Self:
        answer = node.find("math-input-answer").get_text(strip=True)
        self.push_text(f"Напиши: `{answer}`")
        return self

    def set_strike_out_item(self, node: Tag) -> Self:
        self.push_text(f"Зачеркни: `{node.text}`")
        return self

    def set_groups(self, node: Tag) -> Self:
        for vim in node.find_all("vim-groups-row"):
            items = vim.find_all("vim-groups-item")
            one = base64.decodebytes(items[0]["text"].encode("utf-8"))
            two = base64.decodebytes(items[1]["text"].encode("utf-8"))
            self.push_text(
                rf"Сопоставь `{one.decode('utf-8')}` с `{two.decode('utf-8')}`"
            )

        return self

    def set_test(self, node: Tag) -> Self:
        for number, answer in zip(
            itertools.count(1), node.find_all("vim-test-item", correct=True)
        ):
            self.push_text(f"{number}) `{answer.get_text()}`")
        return self

    def set_input(self, node: Tag) -> Self:
        if node.is_empty_element:
            return

        list_of_inputs = []

        for answer in node.find_all("vim-input-item"):
            list_of_inputs.append(f"`{answer.get_text(strip=True)}`")

        self.push_text("Введи: " + " или ".join(list_of_inputs))
        return self

    def set_select(self, node: Tag) -> Self:
        element = (
            node.find("vim-select-item", correct=True)
            .find("vim-select-item-title")
            .get_text(strip=True)
        )
        self.push_text(f"Выбери: `{element}`")
        return self

    def set_dnd_text(self, node: Tag) -> Self:
        drags: Tag = node.find("vim-dnd-text-drags")
        nodes: List[Tag] = node.find_all("vim-dnd-text-drop")

        for number, item in zip(itertools.count(1), nodes):
            ids = item.get("drag-ids").split(",")
            list_of_ids = []

            for answer_id in ids:
                list_of_ids.append(
                    f"`{drags.find(attrs={'answer-id': answer_id}).get_text()}`"
                )

            self.push_text(f"{number}) {' или '.join(list_of_ids)}")

        return self
