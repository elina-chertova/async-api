from fastapi import Query


class Paginator:
    def __init__(
            self,
            page_size: int = Query(
                ge=1,
                le=100,
                default=10,
                alias='page[size]',
                description='Page size',
            ),
            page_number: int = Query(
                default=0,
                alias='page[number]',
                description='Page number for pagination',
                ge=0),
    ):
        self.page_size = page_size
        self.page_number = page_number
