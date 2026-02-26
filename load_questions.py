import os
import redis
from question import extract_questions_from_file
from settings import REDIS_HOST, REDIS_PORT, REDIS_DB


def main():
    questions_dir = "questions"
    client = redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True
    )
    client.delete("question_ids")

    total = 0
    for filename in os.listdir(questions_dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(questions_dir, filename)
            pairs = extract_questions_from_file(filepath)
            for q, a in pairs:
                key = f"question:{total}"
                client.hset(key, mapping={"question": q, "answer": a})
                client.sadd("question_ids", total)
                total += 1

    print(f"Загружено {total} вопросов в Redis.")


if __name__ == "__main__":
    main()
