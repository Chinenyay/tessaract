from pydantic import BaseModel


class ClientTool:
    pass

class ProviderTool(BaseModel):
    pass

class ProviderExecutedTool(ProviderTool):
    pass

class ClientExecutedProviderTool(ProviderTool):
    pass