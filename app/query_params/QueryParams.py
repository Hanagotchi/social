from fastapi import Query
from typing import Optional


def get_query_params(query_params_dic: dict):
    filters = {}
    for filterName, value in query_params_dic.items():
        if value is not None:
            filters[filterName] = value.lower() if value is str else value
    return filters


class SocialFollowersQueryParams:
    def __init__(
        self,
        offset: Optional[int] = Query(0, ge=0),
        limit: Optional[int] = Query(200, le=200),
        user_id: Optional[int] = None,
        query: Optional[str] = None
    ):
        self.query_params = {
            'offset': offset,
            'limit': limit,
            'user_id': user_id,
            'query': query
        }

    def get_query_params(self):
        return get_query_params(self.query_params)


class SocialUsersQueryParams:
    def __init__(
        self,
        offset: Optional[int] = Query(0, ge=0),
        limit: Optional[int] = Query(200, le=200),
        query: Optional[str] = None
    ):
        self.query_params = {
            'offset': offset,
            'limit': limit,
            'query': query
        }

    def get_query_params(self):
        return get_query_params(self.query_params)
