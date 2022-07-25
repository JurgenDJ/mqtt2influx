from simpleeval import FunctionNotDefined, NameNotDefined, SimpleEval
import re
import json
import logging

globalRules: dict = None

def setRules(rules: dict):
    global globalRules
    globalRules = rules

def parseAllfields(fieldlist:dict, se:SimpleEval, logger:logging.Logger)->dict:
    output = {}
    for k in fieldlist.keys():
        value=None
        try:
            expression = str(fieldlist[k])
            logger.debug("evaluating expression {expression}")
            value=se.eval(expression)
        except FunctionNotDefined:
            logger.warning(f'failed evaluating expression(Function not defined) {str(fieldlist[k])}')
        except NameNotDefined:
            logger.warning(f'failed evaluating expression(Name not defined) {str(fieldlist[k])}')
        except SyntaxError:
            logger.warning(f'failed evaluating expression(Syntax Error) {str(fieldlist[k])}')
        except Exception as e:
            logger.warning('failed evaluating expression(other error)')
        else:
            output[k] = value
            logger.debug(f"evaluating expression Success {expression}")
    return output

def processMessage(topic: str, payload: str, logger:logging.Logger = None) -> list:
    global globalRules
    _logger = logger or logging.getLogger()

    def try_json(param:str)->dict:
        result = {}
        try:
            result = json.loads(param)
        except ValueError:
            logger.warning(f"failed parsing json, topic: {topic}, payload: {payload}")
        return result

    se = SimpleEval(names={"fulltopic":topic,"payload":payload,"topic":topic.split('/')}, functions={"json":try_json, "float":float, "int":int})

    output = []
    for rule in globalRules:
        if re.search(rule['topic'], topic):
            tagsRules = rule.get('tags') or {}
            _logger.debug(f"processing fields for topic: {topic}, payload: {payload}")
            processed_fields = parseAllfields(rule['fields'], se, logger=_logger) 
            if processed_fields != {}:
                _logger.debug(f"processing tags for topic: {topic}, payload: {payload}")
                output.append(
                    {
                        "measurement": rule["measurement"],
                        "fields": processed_fields,
                        "tags": parseAllfields(tagsRules, se,  logger=_logger)
                    }
                )
    return output
