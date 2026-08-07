class ClientTool:
    pass

class ProviderTool:
    pass

class ProviderExecutedTool(ProviderTool):
    pass

class ClientExecutedProviderTool(ProviderTool):
    pass

class ClientExecutedShellTool(ClientExecutedProviderTool):
    pass

class ProviderExecutedShellTool(ProviderExecutedTool):
    pass