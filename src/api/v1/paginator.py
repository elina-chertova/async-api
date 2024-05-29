from fastapi import Query


class Paginator:
    def __init__(
            self,
            page_size: int = Query(
                ge=1,
                le=100,
                default=50,
                alias='page[size]',
                description='Page size',
            ),
            page_number: int = Query(
                default=1,
                alias='page[number]',
                description='Page number for pagination',
                ge=1),
    ):
        self.page_size = page_size
        self.page_number = page_number
