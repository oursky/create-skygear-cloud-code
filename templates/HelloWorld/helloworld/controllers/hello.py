import skygear


def includeme():
    @skygear.op('hello')
    def hello_world():
        return {
            'message': 'world',
        }
