from coincurve import PrivateKey

from aleph_client.chains.common import get_fallback_private_key
from aleph_client.chains.nuls1 import NulsSignature

SECRET = b"\xc4\xfe\xe65\x96\x14\xb4:\r: \x05;\x12j\x9bJ" \
         b"\x14\x0eY\xe3BY\x0f\xd6\xee\xfc\x9d\xfe\x8fv\xbc"


def test_sign_data_deprecated():
    data = None
    signature = NulsSignature(data=data)

    private_key = get_fallback_private_key()

    assert signature
    sign_deprecated: NulsSignature = NulsSignature.sign_data_deprecated(pri_key=private_key,
                                                                        digest_bytes=b"x" * (256//8))
    assert sign_deprecated


def test_sign_data():
    private_key = PrivateKey(SECRET)

    sign: NulsSignature = NulsSignature.sign_data(
        pri_key=private_key.secret,
        digest_bytes=b"x" * (256 // 8))

    assert sign


def test_compare_sign_data():
    private_key = PrivateKey(SECRET)

    sign: NulsSignature = NulsSignature.sign_data(
        pri_key=private_key.secret,
        digest_bytes=b"x" * (256 // 8))

    sign_deprecated: NulsSignature = NulsSignature.sign_data_deprecated(
        pri_key=private_key.secret,
        digest_bytes=b"x" * (256 // 8))

    assert len(sign.sig_ser) == len(sign_deprecated.sig_ser)
    assert sign.sig_ser == sign_deprecated.sig_ser
    assert sign == sign_deprecated


def test_compare_sign_message():
    private_key = PrivateKey(SECRET)
    message = b"GOOD"

    sign: NulsSignature = NulsSignature.sign_message(
        pri_key=private_key.secret,
        message=message)

    sign_deprecated: NulsSignature = NulsSignature.sign_message_deprecated(
        pri_key=private_key.secret,
        message=message)

    assert len(sign.sig_ser) == len(sign_deprecated.sig_ser)
    assert sign.sig_ser == sign_deprecated.sig_ser
    assert sign == sign_deprecated


def test_verify():
    private_key = PrivateKey(SECRET)
    message = b"GOOD"

    sign: NulsSignature = NulsSignature.sign_message(
        pri_key=private_key.secret,
        message=message)

    assert sign.verify(message=message)
    assert not sign.verify(message=b"BAD")

    assert sign.verify_deprecated(message=message)
    assert not sign.verify_deprecated(message=b"BAD")
