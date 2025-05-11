import random


def get_random_topic(file_path: str) -> str:
    with open(file_path, 'r') as file:
        topics = file.readlines()
    topics = [topic.strip() for topic in topics if topic.strip()]
    return random.choice(topics)