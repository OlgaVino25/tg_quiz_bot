import redis
from settings import REDIS_HOST, REDIS_PORT, REDIS_DB


r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True,
)


def get_random_question_id():
    """Возвращает случайный ID вопроса из множества question_ids  в Redis."""
    return r.srandmember("question_ids")


def get_question_by_id(question_id):
    """Возвращает кортеж (вопрос, ответ) по ID.
    Если вопрос не найден, возвращает (None, None).
    """
    question_data = r.hgetall(f"question:{question_id}")
    return question_data.get("question"), question_data.get("answer")
