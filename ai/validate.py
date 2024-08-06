from openai import OpenAI, AuthenticationError


def is_valid_openai_key(openai_key):
    if not openai_key:
        return False
    client = OpenAI(api_key=openai_key)
    try:
        client.models.list()
    except AuthenticationError:
        return False
    else:
        return True
