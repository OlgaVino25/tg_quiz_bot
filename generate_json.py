import json
import os
from question import extract_questions_from_file


def main():
    questions_dir = "questions"
    quiz_dict = {}

    for filename in os.listdir(questions_dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(questions_dir, filename)
            pairs = extract_questions_from_file(filepath)
            for q, a in pairs:
                quiz_dict[q] = a

    with open("questions.json", "w", encoding="utf-8") as f:
        json.dump(quiz_dict, f, ensure_ascii=False, indent=2)

    print(f"Сохранено {len(quiz_dict)} вопросов в questions.json")


if __name__ == "__main__":
    main()
