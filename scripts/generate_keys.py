from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

KEYS = Path(__file__).resolve().parents[1] / "keys"
PRIVATE = KEYS / "rsa_key.p8"
PUBLIC = KEYS / "rsa_key.pub"


def main() -> int:
    KEYS.mkdir(exist_ok=True)
    if PRIVATE.exists():
        print(f"{PRIVATE} already exists. Delete it first if you really want a new key.")
        return 1

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    PRIVATE.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    public_pem = key.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    PUBLIC.write_bytes(public_pem)

    body = "".join(
        line for line in public_pem.decode().splitlines() if not line.startswith("-----")
    )
    print(f"Private key saved to {PRIVATE} (never share or commit this file)")
    print(f"Public key saved to  {PUBLIC}\n")
    print("Paste this into the RSA_PUBLIC_KEY field in sql/snowflake_setup.sql:\n")
    print(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())