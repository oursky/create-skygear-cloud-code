from .helloworld import includeme


def skygear_includeme(settings):
    includeme()


skygear_includeme(None)
