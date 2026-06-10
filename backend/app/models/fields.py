from app.core.security import decrypt, encrypt


class EncryptedField:
    """Descriptor que almacena el valor cifrado en una columna `{attr}_encrypted`.

    Uso::

        class MiModelo(Base):
            dni_encrypted = mapped_column(sa.String(512), nullable=True)
            dni = EncryptedField()
    """

    def __set_name__(self, owner, name) -> None:
        self._attr = name
        self._encrypted_attr = f"{name}_encrypted"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        encrypted_value = getattr(instance, self._encrypted_attr, None)
        if encrypted_value is None:
            return None
        return decrypt(encrypted_value)

    def __set__(self, instance, value) -> None:
        if value is None:
            setattr(instance, self._encrypted_attr, None)
        else:
            setattr(instance, self._encrypted_attr, encrypt(value))
