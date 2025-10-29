# function and comprehensions made with chatGPT https://chatgpt.com/c/68f1060a-82ec-832e-a6f5-eb0440eb8d45
"""
    Converts a list of or a single ORM model result into a list of dicts or a dict.
    Params: 
        - result (a list of ORM model results, or a single ORM model result. e.g. [<Product 1>, <Product 2>])
        - execute_keys = [] (what keys to package the result in starting with the second key, 
                                as the first will be at root)
    Return: a list of dicts OR a dict
    Example Return:
        [{<column_1>: <value_1>, execute_key[1]: {<column_1>: <value_1B>} ...} ...]
            OR
        {<column_1>: <value_1>, execute_key[1]: {<column_1>: <value_1B>} ...}
"""
def package_result(result, execute_keys = []):
    # Helper function
    def package_row(rslt):
        package_dict = lambda r : {column.name: getattr(r, column.name) for column in r.__table__.columns}
        row = {}
        for j in range(len(rslt)):
            if j == 0:
                row = package_dict(rslt[j])
            else:
                try:
                    rslt[j].__table__
                except AttributeError:
                    # if nontable (e.g. str) rslt, add
                    row[execute_keys[j-1]] = rslt[j]
                else:
                    # if table rslt, package and add
                    row[execute_keys[j-1]] = package_dict(rslt[j])
        return row

    if not result:
        # No Result
        # print('no rslt')
        return []
      
    else: 
        if type(result) == list:
            # List Result
            # print('list exe')

            if len(result[0]) - 1 != len(execute_keys):
                # using code from https://www.w3schools.com/python/gloss_python_raise.asp
                raise Exception("execute_keys must define keys for each execute column beyond the first")

            rows = []
            for r in result:
                rows.append(
                    package_row(r)
                )
            return rows
        
        # Dict Result
        # print('obj exe')

        if len(result) - 1 != len(execute_keys):
                # using code from https://www.w3schools.com/python/gloss_python_raise.asp
                raise Exception("execute_keys must define keys for each execute column beyond the first")
        
        return package_row(result)