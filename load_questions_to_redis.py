import json
import redis
from settings import REDIS_HOST, REDIS_PORT, REDIS_DB


def main():
    r = redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True
    )

    with open("questions.json", "r", encoding="utf-8") as f:
        quiz_dict = json.load(f)

    r.delete("question_ids")

    for idx, (q, a) in enumerate(quiz_dict.items()):
        key = f"question:{idx}"
        r.hset(key, mapping={"question": q, "answer": a})
        r.sadd("question_ids", idx)

    print(f"Загружено {len(quiz_dict)} вопросов. Последний ID: {idx}")


if __name__ == "__main__":
    main()
