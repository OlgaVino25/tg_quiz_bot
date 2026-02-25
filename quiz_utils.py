import re


def normalize_answer(answer: str) -> str:
    """
    Приводит ответ к нормальной форме для сравнения.
    Удаляет пояснения в скобках, обрезает до точки,
    убирает кавычки и лишние пробелы, приводит к нижнему регистру.
    """
    answer = re.sub(r"\([^)]*\)", "", answer)
    if "." in answer:
        answer = answer.split(".")[0]
    answer = re.sub(r"[\'\"«»]", "", answer)
    return answer.strip().lower()
