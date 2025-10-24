# function and comprehensions made with chatGPT https://chatgpt.com/c/68f1060a-82ec-832e-a6f5-eb0440eb8d45
"""
    Converts a list of or a single ORM model result into a list of dicts or a dict.
    Params: result (a list of ORM model results, or a single ORM model result. e.g. [<Product 1>, <Product 2>])
    Return: a list of dicts OR a dict
    Example Return:
        [{<column_1>: <value_1> ...} ...]
            OR
        {<column_1>: <value_1> ...}
"""
def package_result(result):
    if not result:
        print('no rslt')
        return []
    if type(result) == list:
        print('list')
        return [{column.name: getattr(r, column.name) for column in r.__table__.columns} for r in result]
    print('obj')
    return {column.name: getattr(result, column.name) for column in result.__table__.columns}