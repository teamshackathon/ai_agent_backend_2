from typing import Any

from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    id: Any
    __name__: str
    
    # テーブル名を自動生成するためのクラスメソッド
    @declared_attr
    def __tablename__(self, cls) -> str:
        return cls.__name__.lower()