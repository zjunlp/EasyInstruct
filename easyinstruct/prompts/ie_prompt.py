from .base_prompt import BasePrompt

class IEPrompt(BasePrompt):
    """class for information extraction"""

    def __init__(self, task='ner'):
        super().__init__()
        if task not in ['ner', 're', 'ee', 'rte']:
            raise ValueError('The task name should be one of ner, re, ee and rte.')
        self.task = task

    def build_prompt(
        self,
        prompt,
        language='en',
        instruction=None,
        in_context=False,
        domain=None,
        labels=None,
        examples=None
    ):
        self.prompt = ''
        self.language = language
        self.instruction = instruction
        self.in_context = in_context
        self.domain = domain
        self.labels = labels
        self.examples = examples

        if self.language not in ['en', 'ch']:
            raise ValueError('Now we only support language of \'en\' (English) and \'ch\' (Chinese).')
        if in_context:
            assert examples is not None, 'Please provide some examples if in-context=True.'

        # customized task instruction
        if instruction:
            self.prompt += instruction
            self.prompt += '\n'
        # default task instruction
        elif self.language == 'en':
            # en ner task
            if self.task == 'ner':
                if self.domain and self.labels:
                    self.prompt += f"You are a highly intelligent and accurate {self.domain} domain Named-entity recognition(NER) system. You take Passage as input and your task is to recognize and extract specific types of {self.domain} domain named entities in that given passage and classify into a set of following predefined entity types:"
                    self.prompt += '\n'
                    self.prompt += ', '.join(self.labels)
                    self.prompt += '\n'
                elif self.domain:
                    self.prompt += f"You are a highly intelligent and accurate {self.domain} domain Named-entity recognition(NER) system. You take Passage as input and your task is to recognize and extract specific types of {self.domain} domain named entities in that given passage and classify into a set of entity types."
                    self.prompt += '\n'
                elif self.labels:
                    self.prompt += "You are a highly intelligent and accurate Named-entity recognition(NER) system. You take Passage as input and your task is to recognize and extract specific types of named entities in that given passage and classify into a set of following predefined entity types:"
                    self.prompt += '\n'
                    self.prompt += ', '.join(self.labels)
                    self.prompt += '\n'
                else:
                    self.prompt += "You are a highly intelligent and accurate Named-entity recognition(NER) system. You take Passage as input and your task is to recognize and extract specific types of named entities in that given passage and classify into a set of entity types."
                    self.prompt += '\n'
                self.prompt += "Your output format is only [{'E': type of entity from predefined entity types, 'W': entity in the input text},...] form, no other form."
                self.prompt += '\n\n'
            # en re task
            elif self.task == 're':
                if self.domain and self.labels:
                    self.prompt += f"You are a highly intelligent and accurate {self.domain} domain relation extraction(RE) system. Given a context, a pair of head and tail entities in the context, your task is to extract the specific type of {self.domain} domain relationship between the head and tail entities from candidate relations:"
                    self.prompt += '\n'
                    self.prompt += ', '.join(self.labels)
                    self.prompt += '\n'
                elif self.domain:
                    self.prompt += f"You are a highly intelligent and accurate {self.domain} domain relation extraction(RE) system. Given a context, a pair of head and tail entities in the context, your task is to extract the specific type of {self.domain} domain relationship between the head and tail entities."
                    self.prompt += '\n'
                elif self.labels:
                    self.prompt += "You are a highly intelligent and accurate relation extraction(RE) system. Given a context, a pair of head and tail entities in the context, your task is to extract the specific type of relationship between the head and tail entities from candidate relations:"
                    self.prompt += '\n'
                    self.prompt += ', '.join(self.labels)
                    self.prompt += '\n'
                else:
                    self.prompt += "You are a highly intelligent and accurate relation extraction(RE) system. Given a context, a pair of head and tail entities in the context, your task is to extract the specific type of relationship between the head and tail entities."
                    self.prompt += '\n'
                self.prompt += "Your output is only the relation type, no other words."
                self.prompt += '\n\n'
            # en ee task
            elif self.task == 'ee':
                if self.domain:
                    self.prompt += f"You are a highly intelligent and accurate {self.domain} domain event extraion model. You take Passage as input and convert it into {self.domain} domain events arguments.You can identify all events of target types mentioned in the sentence, and extract corresponding event arguments playing target roles."
                    self.prompt += '\n'
                else:
                    self.prompt += "You are a highly intelligent and accurate event extraion model. You take Passage as input and convert it into events arguments. You can identify all events of target types mentioned in the sentence, and extract corresponding event arguments playing target roles."
                    self.prompt += '\n'
                self.prompt += "Your output format is only [enent_list: [ event_type:[ arguments:[ role , argument ], ...], ...], ...], nothing else."
                self.prompt += '\n\n'
            # ch rte task
            elif self.task == 'rte':
                if self.domain:
                    self.prompt += f"You are a highly intelligent and accurate {self.domain} domain Resource Description Framework (RDF) data model. You take Passage as input and convert it into {self.domain} domain RDF triples. A triple is a set of three entities that codifies a statement about semantic data in the form of subject-predicate-object expressions."
                    self.prompt += '\n'
                else:
                    self.prompt += "You are a highly intelligent and accurate Resource Description Framework (RDF) data model. You take Passage as input and convert it into RDF triples. A triple is a set of three entities that codifies a statement about semantic data in the form of subject-predicate-object expressions."
                    self.prompt += '\n'
                self.prompt += "Your output format is only [[ subject, predicate, object ], ...], nothing else."
                self.prompt += '\n\n'
        elif self.language == 'ch':
            # ch ner task
            if self.task == 'ner':
                if self.domain and self.labels:
                    self.prompt += f"您是一个高度智能和精确的{self.domain}域命名实体识别（NER）系统。您将文本作为输入，您的任务是识别和提取给定段落中的特定类型的{self.domain}域名实体，并将其分类为一组预定义的实体类型："
                    self.prompt += '\n'
                    self.prompt += ', '.join(self.labels)
                    self.prompt += '\n'
                elif self.domain:
                    self.prompt += f"您是一个高度智能和精确的{self.domain}域命名实体识别（NER）系统。您将文本作为输入，您的任务是识别和提取给定文章中特定类型的{self.domain}域命名实体，并将其分类为一组实体类型。"
                    self.prompt += '\n'
                elif self.labels:
                    self.prompt += "您是一个高度智能和精确的命名实体识别（NER）系统。您将文本作为输入，您的任务是识别和提取给定段落中的特定类型的命名实体，并将其分类为一组预定义的实体类型："
                    self.prompt += '\n'
                    self.prompt += ', '.join(self.labels)
                    self.prompt += '\n'
                else:
                    self.prompt += "您是一个高度智能和精确的命名实体识别（NER）系统。您将文本作为输入，您的任务是识别和提取给定文章中特定类型的命名实体，并将其分类为一组实体类型。"
                    self.prompt += '\n'
                self.prompt += "您输出的格式需要为[{'E': type of entity from predefined entity types, 'W': entity in the input text},...]，没有其他格式要求。"
                self.prompt += '\n\n'
            # ch re task
            elif self.task == 're':
                if self.domain and self.labels:
                    self.prompt += f"您是一个高度智能和精确的{self.domain}域关系抽取（RE）系统。给定上下文以及上下文中包含的一对头实体和尾实体，您的任务是提取给定头实体和尾实体间特定类型的{self.domain}域关系，候选的关系类型如下："
                    self.prompt += '\n'
                    self.prompt += ', '.join(self.labels)
                    self.prompt += '\n'
                elif self.domain:
                    self.prompt += f"您是一个高度智能和精确的{self.domain}域关系抽取（RE）系统。给定上下文以及上下文中包含的一对头实体和尾实体，您的任务是提取给定头实体和尾实体间特定类型的{self.domain}域关系。"
                    self.prompt += '\n'
                elif self.labels:
                    self.prompt += "您是一个高度智能和精确的关系抽取（RE）系统。给定上下文以及上下文中包含的一对头实体和尾实体，您的任务是提取给定头实体和尾实体间特定类型的关系，候选的关系类型如下："
                    self.prompt += '\n'
                    self.prompt += ', '.join(self.labels)
                    self.prompt += '\n'
                else:
                    self.prompt += "您是一个高度智能和精确的关系抽取（RE）系统。给定上下文以及上下文中包含的一对头实体和尾实体，您的任务是提取给定头实体和尾实体间特定类型的关系。"
                    self.prompt += '\n'
                self.prompt += "您只需要输出关系的类型即可，不需要其他的文字输出。"
                self.prompt += '\n\n'
            # ch ee task
            elif self.task == 'ee':
                if self.domain:
                    self.prompt += f"您是一个高度智能和精确的{self.domain}域事件提取模型。您将文本作为输入并将其转换为{self.domain}域事件参数。您可以识别句子中提到的所有目标类型的事件，并提取扮演目标角色的相应事件参数。"
                    self.prompt += '\n'
                else:
                    self.prompt += "您是一个高度智能和精确的事件提取模型。您将文本作为输入并将其转换为事件参数。您可以识别句子中提到的所有目标类型的事件，并提取扮演目标角色的相应事件参数。"
                    self.prompt += '\n'
                self.prompt += "您的输出格式为[enent_list: [ event_type:[ arguments:[ role , argument ], ...], ...], ...]，没有其他要求。"
                self.prompt += '\n\n'
            # ch rte task
            elif self.task == 'rte':
                if self.domain:
                    self.prompt += f"您是一个高度智能和精确的{self.domain}域资源描述框架（RDF）数据模型。您将文本作为输入，并将其转换为{self.domain}域RDF三元组。三元组是由三个实体组成的集合，以主语-谓语-宾语表达式的形式对语义数据进行编码。"
                    self.prompt += '\n'
                else:
                    self.prompt += "您是一个高度智能和精确的资源描述框架（RDF）数据模型。您将文本作为输入，并将其转换为RDF三元组。三元组是由三个实体组成的集合，以主语-谓语-宾语表达式的形式对语义数据进行编码。"
                    self.prompt += '\n'
                self.prompt += "您输出的格式需要为[[ 主语, 谓语, 宾语 ], ...]，没有其他格式要求。"
                self.prompt += '\n\n'

        # in-context
        if self.in_context:
            if self.language == 'en':
                self.prompt += 'Examples:'
                self.prompt += '\n'
                for example in self.examples:
                    if self.task in ['ner', 'ee', 'rte']:
                        self.prompt += 'Input: '
                        self.prompt += example['input']
                        self.prompt += '\n'
                        self.prompt += 'Output: '
                        self.prompt += str(example['output'])
                    elif self.task == 're':
                        self.prompt += 'Context: '
                        self.prompt += example['context']
                        self.prompt += '\n'
                        self.prompt += f"The relation between ({example['head_type']}) '{example['head_entity']}' and ({example['tail_type']}) '{example['tail_entity']}' in the context is "
                        self.prompt += example['relation']
                    self.prompt += '\n\n'
            elif self.language == 'ch':
                self.prompt += '示例：'
                self.prompt += '\n'
                for example in self.examples:
                    if self.task in ['ner', 'ee', 'rte']:
                        self.prompt += '输入：'
                        self.prompt += example['input']
                        self.prompt += '\n'
                        self.prompt += '输出：'
                        self.prompt += str(example['output'])
                    elif self.task == 're':
                        self.prompt += '上下文：'
                        self.prompt += example['context']
                        self.prompt += '\n'
                        self.prompt += f"上下文头实体（{example['head_type']}）'{example['head_entity']}'和尾实体（{example['tail_type']}）'{example['tail_entity']}'间的关系类型是"
                        self.prompt += example['relation']
                    self.prompt += '\n\n'

        # prompt
        self.prompt += prompt
        return self.prompt