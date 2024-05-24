from typing import Optional


class SociaFollowersQueryParams:
    def __init__(
        self,
        user_id: Optional[int] = None,
        query: Optional[str] = None
    ):
        self.user_id = user_id
        self.query = query

    def get_query_params(self):
        filters = {}
        if self.user_id is not None:
            filters['user_id'] = self.user_id
        if self.query is not None:
            filters['query'] = self.query
        return filters
