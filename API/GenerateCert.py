from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from datetime import datetime, timedelta
import ipaddress
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_selfsigned_cert(hostname, rootkey, subcertkey, ip_addresses=None):
    """Generates self signed certificate for a hostname, and optional IP addresses."""
    name = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, f"RootCert")
    ])

    # best practice seem to be to include the hostname in the SAN, which *SHOULD* mean COMMON_NAME is ignored.
    #x509.DNSName(hostname)
    alt_names = []

    # allow addressing by IP, for when you don't have real DNS (common in most testing scenarios
    if ip_addresses:
        for addr in ip_addresses:
            # openssl wants DNSnames for ips...
            alt_names.append(x509.DNSName(addr))
            # ... whereas golang's crypto/tls is stricter, and needs IPAddresses
            # note: older versions of cryptography do not understand ip_address objects
            alt_names.append(x509.IPAddress(ipaddress.ip_address(addr)))

    san = x509.SubjectAlternativeName(alt_names)

    # path_len=0 means this cert can only sign itself, not other certs.
    basic_contraints = x509.BasicConstraints(ca=True, path_length=1)
    now = datetime.utcnow()
    rootcert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(rootkey.public_key())
        .serial_number(1000)
        .not_valid_before(now)
        .not_valid_after(now + timedelta(days=10 * 365))
        .add_extension(basic_contraints, False)
        .add_extension(san, False)
        .sign(rootkey, hashes.SHA256(), default_backend())
    )
    rootcert_pem = rootcert.public_bytes(encoding=serialization.Encoding.PEM)
    rootcert_der = rootcert.public_bytes(encoding=serialization.Encoding.DER)


    basic_contraints = x509.BasicConstraints(ca=False, path_length=None)
    subcertname = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, f"SubCertificate")
    ])

    signed_with_ca = (x509.CertificateBuilder()
        .subject_name(subcertname)
        .issuer_name(name)
        .public_key(subcertkey.public_key())
        .serial_number(9999)
        .not_valid_before(now)
        .not_valid_after(now + timedelta(days=10 * 365))
        .add_extension(basic_contraints, False)
        .add_extension(san, False)
        .sign(rootkey, hashes.SHA256(), default_backend()))


    signed_with_ca_pem = signed_with_ca.public_bytes(encoding=serialization.Encoding.PEM)
    signed_with_ca_der = signed_with_ca.public_bytes(encoding=serialization.Encoding.DER)

    return rootcert_pem, rootcert_der, signed_with_ca_pem, signed_with_ca_der


def exportkeytoboth(key, name:str):
    with open(f"{name}.pem", "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    with open(f"{name}.der", "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

if __name__=="__main__":
    rootkey = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    othercertkey = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    exportkeytoboth(rootkey, "root")
    exportkeytoboth(othercertkey, "sub")

    cert, cert_der, subcert, subcertder = generate_selfsigned_cert("nodmainnodomain.noip", rootkey, othercertkey, ['192.168.0.82'],)
    # Write our certificate out to disk.
    with open("rootcertificate.pem", "wb") as f:
        f.write(cert)
    with open("rootcertificate.der", "wb") as f:
        f.write(cert_der)
    with open("subcertificate.pem", "wb") as f:
        f.write(subcert)
    with open("subcertificate.der", "wb") as f:
        f.write(subcertder)

