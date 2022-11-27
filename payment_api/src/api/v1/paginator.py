from fastapi import Query


class Paginator:
    def __init__(
        self,
        per_page: int = Query(
            default=50,  # noqa: WPS432
            alias='page[size]',
            description='Количество элементов на странице',
            ge=1,
            le=500,  # noqa: WPS432
        ),
            page: int = Query(default=1, alias='page[number]', description='Номер страницы', ge=1),
    ):
        self.per_page = per_page
        self.page = page
