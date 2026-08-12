'''
oai

OpenAIWebSearchAction:
    pass

Source:
    type: Literal["url"] = "url"
    url: str = Field(default=Url)

Search(OpenAIWebSearchAction):
    type: Literal["search"] = "search"
    queries: list[str] | None = None
    sources: list[Source]

OpenPage(OpenAIWebSearchAction):
    type: Literal["open_page"] = "open_page"
    url: str | None = None


FindInPage(OpenAIWebSearchAction):
    type: Literal["find_in_page"] = "find_in_page"
    pattern: str
    url: str

WebSearchCall:

    type: Literal["web_search_call"] = "web_search_call"
    id: str
    action: Search | OpenPage | FindInPage
    status: Literal["in_progress", "searching", "completed", "failed"]
    agent: Agent | None = None

class WebSearchTool(HostedTool):
    type: Literal["web_search"] = "web_search"

class WebSearchSource(BaseModel):
    url: str
    title: str | None = None


class WebSearchResult(BaseModel):
    type: Literal["web_search_result"] = "web_search_result"

    call_id: str
    sources: list[WebSearchSource] = Field(default_factory=list)
    error: WebSearchError | None = None
'''