import yaml

# from message_handler_jinja import setRules, handleMessage
from message_processor import setRules, processMessage

def loadYaml(filename:str)->dict:
    result = {}
    with open(filename, "r") as stream:
        try:
            result = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return result


if __name__ == "__main__":
    config = loadYaml(filename="mapping.yaml")
    if config=={}:
        print("CONFIG LOADING ERROR")
        exit
    # print(config)
    setRules(config['rules'])
    testcases = loadYaml("tests.yaml")
    # print(testcases)
    
    n=0
    for testcase in testcases:
        n+=1
        result = processMessage(topic=testcase['topic'],payload=testcase['payload'])
        expected = testcase['expected'] if isinstance(testcase['expected'],list) else [testcase['expected']]
        if result == expected:
            print(f"test ok - {n}")
        else:
            print(f"test FAIL - {n}")
            print(f"expected: {expected}")
            print(f'received: {result}')
    

