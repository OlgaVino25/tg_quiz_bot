import os


questions_dir = "questions"
quiz_dict = {}


def extract_questions_from_file(filepath):
    """Извлекает все пары (вопрос, ответ) из одного файла."""
    with open(filepath, "r", encoding="KOI8-R") as f:
        lines = f.readlines()

    questions = []
    current_question = []
    current_answer = []
    mode = None

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("Вопрос ") and ":" in stripped:
            if mode == "a" and current_question and current_answer:
                questions.append(
                    ("\n".join(current_question), "\n".join(current_answer))
                )
                current_question, current_answer = [], []

            parts = stripped.split(":", 1)
            if len(parts) > 1 and parts[1].strip():
                current_question = [parts[1].strip()]
            else:
                current_question = []
            mode = "q"

        elif stripped.startswith("Ответ:"):
            if mode == "q":
                parts = stripped.split(":", 1)
                if len(parts) > 1 and parts[1].strip():
                    current_answer = [parts[1].strip()]
                else:
                    current_answer = []
                mode = "a"

        elif stripped.startswith(("Автор:", "Источник:", "Комментарий:", "Зачет:")):
            if mode == "a" and current_question and current_answer:
                questions.append(
                    ("\n".join(current_question), "\n".join(current_answer))
                )
                current_question, current_answer = [], []
                mode = None

        else:
            if mode == "q" and stripped:
                current_question.append(stripped)
            elif mode == "a" and stripped:
                current_answer.append(stripped)

    if mode == "a" and current_question and current_answer:
        questions.append(("\n".join(current_question), "\n".join(current_answer)))

    return questions


for filename in os.listdir(questions_dir):
    if filename.endswith(".txt"):
        filepath = os.path.join(questions_dir, filename)
        try:
            pairs = extract_questions_from_file(filepath)
            for q, a in pairs:
                quiz_dict[q] = a
        except Exception as e:
            print(f"Ошибка при обработке файла {filename}: {e}")

print(f"Загружено вопросов: {len(quiz_dict)}")

for i, (q, a) in enumerate(list(quiz_dict.items())[:5]):
    print(f"\n--- Вопрос {i+1} ---")
    print(f"Вопрос: {q}")
    print(f"Ответ: {a}")
