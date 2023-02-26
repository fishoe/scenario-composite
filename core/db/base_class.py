from sqlalchemy import Column, BigInteger
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm.exc import DetachedInstanceError


def to_snake_case(camel_str: str) -> str:
    return ''.join(f'_{x.lower()}' if x.isupper() else x for x in camel_str).lstrip('_')


@as_declarative()
class Base:
    id: int = Column(BigInteger, primary_key=True, index=True)
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(self) -> str:
        return to_snake_case(self.__name__)

    def __repr__(self) -> str:
        return self._repr(id=self.id)

    def _repr(self, **fields) -> str:
        """
        Helper for __repr__
        """
        field_strings = []
        at_least_one_attached_attribute = False
        for key, field in fields.items():
            try:
                field_strings.append(f'{key}={field!r}')
            except DetachedInstanceError:
                field_strings.append(f'{key}=DetachedInstanceError')
            else:
                at_least_one_attached_attribute = True
        if at_least_one_attached_attribute:
            return f"<{self.__class__.__name__}({','.join(field_strings)})>"
        return f"<{self.__class__.__name__} {id(self)}>"
