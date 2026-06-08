"""Tests para AES-256-GCM encryption (RED → GREEN → TRIANGULATE)."""

import os

import pytest

from app.core.exceptions import EncryptionError
from app.core.security import decrypt, encrypt


class TestEncryptionRoundTrip:
    def test_round_trip_basic(self):
        key = os.urandom(32)
        ciphertext = encrypt("hola", key=key)
        assert decrypt(ciphertext, key=key) == "hola"

    def test_round_trip_empty_string(self):
        key = os.urandom(32)
        ciphertext = encrypt("", key=key)
        assert decrypt(ciphertext, key=key) == ""

    def test_round_trip_unicode(self):
        key = os.urandom(32)
        plaintext = "ñandú — 🧉 mate"
        ciphertext = encrypt(plaintext, key=key)
        assert decrypt(ciphertext, key=key) == plaintext

    def test_round_trip_long_string(self):
        key = os.urandom(32)
        plaintext = "a" * 10_000
        ciphertext = encrypt(plaintext, key=key)
        assert decrypt(ciphertext, key=key) == plaintext


class TestEncryptionNonce:
    def test_different_nonces(self):
        key = os.urandom(32)
        plaintext = "mismo texto"
        c1 = encrypt(plaintext, key=key)
        c2 = encrypt(plaintext, key=key)
        assert c1 != c2


class TestEncryptionKeyValidation:
    def test_key_16_bytes_raises(self):
        short_key = os.urandom(16)
        with pytest.raises(EncryptionError):
            encrypt("hola", key=short_key)

    def test_key_32_bytes_works(self):
        key = os.urandom(32)
        ciphertext = encrypt("hola", key=key)
        assert decrypt(ciphertext, key=key) == "hola"


class TestEncryptionCorruption:
    def test_corrupted_ciphertext_raises(self):
        key = os.urandom(32)
        ciphertext = encrypt("secreto", key=key)
        corrupted = ciphertext[:-3] + "abc"
        with pytest.raises(EncryptionError):
            decrypt(corrupted, key=key)

    def test_truncated_ciphertext_raises(self):
        key = os.urandom(32)
        ciphertext = encrypt("secreto", key=key)
        truncated = ciphertext[:10]
        with pytest.raises(EncryptionError):
            decrypt(truncated, key=key)

    def test_invalid_base64_raises(self):
        key = os.urandom(32)
        with pytest.raises(EncryptionError):
            decrypt("!!!not-base64!!!", key=key)

    def test_wrong_key_raises(self):
        key_a = os.urandom(32)
        key_b = os.urandom(32)
        ciphertext = encrypt("mensaje", key=key_a)
        with pytest.raises(EncryptionError):
            decrypt(ciphertext, key=key_b)
