import json
from pathlib import Path
from tempfile import NamedTemporaryFile

import base58
import pytest
from dataclasses import dataclass, asdict

from nacl.signing import VerifyKey

from aleph_client.chains.common import get_verification_buffer
from aleph_client.chains.sol import SOLAccount, get_fallback_account


@dataclass
class Message:
    chain: str
    sender: str
    type: str
    item_hash: str


def test_get_fallback_account():
    with NamedTemporaryFile() as private_key_file:
        account: SOLAccount = get_fallback_account(path=Path(private_key_file.name))

        assert account.CHAIN == "SOL"
        assert account.CURVE == "curve25519"
        assert account._signing_key.verify_key
        assert type(account.private_key) == bytes
        assert len(account.private_key) == 32


@pytest.mark.asyncio
async def test_SOLAccount(solana_account):
    message = asdict(Message("SOL", solana_account.get_address(), "SomeType", "ItemHash"))
    initial_message = message.copy()
    await solana_account.sign_message(message)
    assert message["signature"]

    address = message["sender"]
    assert address
    assert type(address) == str
    # assert len(address) == 44  # can also be 43?
    signature = json.loads(message["signature"])

    pubkey = base58.b58decode(signature["publicKey"])
    assert type(pubkey) == bytes
    assert len(pubkey) == 32

    # modeled according to https://github.com/aleph-im/pyaleph/blob/master/src/aleph/chains/solana.py
    verify_key = VerifyKey(pubkey)
    verification_buffer = get_verification_buffer(message)
    assert get_verification_buffer(initial_message) == verification_buffer
    verif = verify_key.verify(
        verification_buffer, signature=base58.b58decode(signature["signature"])
    )

    assert verif == verification_buffer
    assert message["sender"] == signature["publicKey"]


@pytest.mark.asyncio
async def test_decrypt_curve25516(solana_account):
    assert solana_account.CURVE == "curve25519"
    content = b"SomeContent"

    encrypted = await solana_account.encrypt(content)
    assert type(encrypted) == bytes
    decrypted = await solana_account.decrypt(encrypted)
    assert type(decrypted) == bytes
    assert content == decrypted
