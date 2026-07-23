from enum import Enum

class OpenAIModelSelector(Enum):
    pass

class OpenAIReasoningModels(OpenAIModelSelector):
    GPT_5_6_SOL = "gpt-5.6-sol"
    GPT_5_6_TERRA = "gpt-5.6-terra"
    GPT_5_6_LUNA = "gpt-5.6-luna"
    GPT_5_5 = "gpt-5.5"
    GPT_5_4 = "gpt-5.4"
    GPT_5_4_MINI = "gpt-5.4-mini"
    GPT_5_4_NANO = "gpt-5.4-nano"

class OpenAIProReasoningModels(OpenAIModelSelector):
    GPT_5_5_PRO = "gpt-5.5-pro"
    GPT_5_4_PRO = "gpt-5.4-pro"

class OpenAIChatModels(OpenAIModelSelector):
    pass

class OpenAIImageModels(OpenAIModelSelector):
    pass

class OpenAIAudioModels(OpenAIModelSelector):
    pass

class OpenAIOpenWeightsModels(OpenAIModelSelector):
    pass

class _CustomOpenAIModels():
    def __init__(self, model_name, model_id, model_class):
        self.model_name = model_name
        self.model_id = model_id
        self.model_class = model_class
    

    @property
    def model_name(self):
        return self._model_name

    @model_name.setter
    def model_name(self, value: str):
        self._model_name = value

def registerOpenAIModel(model_alias, model_id, model_class: OpenAIModelSelector):
    

