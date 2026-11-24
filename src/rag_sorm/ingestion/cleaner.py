import re

PUNKT = re.compile(r'^[ \t\xa0]*(\d+(?:\.\d+)*)\.?[ \t\xa0]+(?=[А-ЯЁA-Z«"(])', re.M)

ROMAN = r"(?=[IVXLC])[IVXLC]+"

# III. Требования...
SECTION = re.compile(rf"^[ \t\xa0]*({ROMAN})\.[ \t\xa0]+(?=[А-ЯЁ])")

# только "17." (одно число, точка, пробел). "17.1." сюда не попадёт,
# потому что после первой точки идёт цифра, а не пробел
PUNKT = re.compile(r"^[ \t\xa0]*(\d+)\.[ \t\xa0]+(?=\S)")

# подпункты "17.1." / "17.1.1." нужны только в clean_text,
# чтобы они начинались с новой строки, но пунктами не считаются
SUBPOINT = re.compile(r"^[ \t\xa0]*\d+(?:\.\d+)+\.?[ \t\xa0]+(?=\S)")

# подпункты "1) 2)"  для переноса на новую строку, но не выделения в отдельный пункт
LIST_ITEM = re.compile(r"^\d+\)\s+\S")

# Приложение, отделение от предыдущих пунктов
APPENDIX = re.compile(r"^[ \t]*(?:Приложение|ПРИЛОЖЕНИЕ)[ \t]*(?:№|N)[ \t]*\d+")


def clean_text(text: str) -> str:
    # 1. Неразрывные пробелы и мягкие переносы
    text = text.replace("\xa0", " ").replace("\u00ad", "")
    text = re.sub(r"(?<=[;:])\s+(?=\d{1,2}\)\s)", "\n", text)

    # 2. Номера страниц на отдельных строках: удаляем вместе с переводом строки,
    #    чтобы не разрывать абзац, который продолжается на следующей странице
    text = re.sub(r"(?m)^[ \t]*\d{1,3}[ \t]*(?:\n|$)", "", text)
    # 3. Пробелы в конце строк
    text = re.sub(r"[ \t]+\n", "\n", text)

    # 4. Слова, разорванные дефисом на конце строки: "переда-\nча" -> "передача"
    text = re.sub(r"(?<=[а-яёa-z])-\n(?=[а-яёa-z])", "", text)

    # перенос строки перед пунктом
    text = re.sub(r"(?<=[.;:])[ \t]+(?=\d{1,3}\.[ \t]+[А-ЯЁ])", "\n", text)

    # отделение приложения от предыдущего текста
    text = re.sub(
        r"(?<=[.;:])[ \t]+(?=(?:Приложение|ПРИЛОЖЕНИЕ)[ \t]*(?:№|N)[ \t]*\d)",
        "\n",
        text,
    )

    # 5. Склейка строк внутри абзаца
    result = []
    for line in text.split("\n"):
        line = line.strip()

        if not line:
            result.append("")  # граница абзаца
        elif not result or result[-1] == "":
            result.append(line)  # начало абзаца
        elif (
            PUNKT.match(line)
            or SUBPOINT.match(line)
            or LIST_ITEM.match(line)
            or SECTION.match(line)
            or APPENDIX.match(line)
            or line.startswith("|")
        ):
            result.append(line)  # пункт, подпункт, раздел или строка таблицы
        elif result[-1].startswith("|"):
            result.append(line)  # текст после таблицы
        else:
            result[-1] += " " + line  # продолжение строки

    text = "\n".join(result)

    # 6. Лишние пробелы и пустые строки
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def parse_points(text):
    section, points, current = None, [], None

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue

        if APPENDIX.match(line):
            section = line
            current = {"point": "преамбула", "section": section, "text": line}
            points.append(current)
        elif SECTION.match(line):
            section, current = line, None
        elif m := PUNKT.match(line):
            current = {"point": m.group(1), "section": section, "text": line}
            points.append(current)
        elif current is not None:
            current["text"] += "\n" + line
    return points
