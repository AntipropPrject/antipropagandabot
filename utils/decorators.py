from functools import wraps


def test_deco(fn):
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        print(f'Вызвана {fn}')
        await fn(*args, **kwargs)

    return wrapper


def for_all_methods(decorator):
    def decorate(cls):
        for attr in cls.__bases__[0].__dict__:
            if callable(getattr(cls, attr)) and not attr.startswith('_'):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls

    return decorate
