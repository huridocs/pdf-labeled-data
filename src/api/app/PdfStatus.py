from pydantic import BaseModel


class PdfStatus(BaseModel):
    name: str
    finished: bool
    junk: bool

    @staticmethod
    def empty(name: str):
        return PdfStatus(
            name=name,
            finished=False,
            junk=False,
        )
