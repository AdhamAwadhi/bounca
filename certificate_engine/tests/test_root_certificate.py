# coding: utf-8
import datetime
from cryptography import x509
from cryptography.x509 import ExtensionOID
from cryptography.x509.extensions import ExtensionNotFound, _key_identifier_from_public_key
from cryptography.x509.oid import AuthorityInformationAccessOID, NameOID

from certificate_engine.ssl.certificate import Certificate, PassPhraseError
from certificate_engine.ssl.key import Key
from certificate_engine.tests.helpers import CertificateTestCase
from x509_pki.tests.factories import CertificateFactory, DistinguishedNameFactory


class RootCertificateTest(CertificateTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.key = Key().create_key(4096)

    def test_generate_minimal_root_ca(self):
        dn = DistinguishedNameFactory(countryName=None,
                                      stateOrProvinceName=None,
                                      localityName=None,
                                      organizationName=None,
                                      organizationalUnitName=None,
                                      emailAddress=None,
                                      subjectAltNames=None)
        certificate_request = CertificateFactory(key=self.key.serialize(), dn=dn)
        certhandler = Certificate()
        certhandler.create_certificate(certificate_request)

        crt = certhandler.certificate

        self.assertEqual(crt.serial_number, int(certificate_request.serial))
        self.assertEqual(crt.public_key().public_numbers(), self.key.key.public_key().public_numbers())
        self.assertEqual(crt.not_valid_before, datetime.datetime(
            year=certificate_request.created_at.year,
            month=certificate_request.created_at.month,
            day=certificate_request.created_at.day
        ))

        self.assertEqual(crt.not_valid_after, datetime.datetime(
            year=certificate_request.expires_at.year,
            month=certificate_request.expires_at.month,
            day=certificate_request.expires_at.day
        ))

        # subject
        self.assertIsInstance(crt.subject, x509.Name)
        self.assertListEqual(list(crt.subject), [
            x509.NameAttribute(NameOID.COMMON_NAME, certificate_request.dn.commonName),
        ])
        # issuer
        self.assertIsInstance(crt.issuer, x509.Name)
        self.assertListEqual(list(crt.issuer), [
            x509.NameAttribute(NameOID.COMMON_NAME, certificate_request.dn.commonName),
        ])
        self.assert_crl_distribution(crt, certificate_request)
        self.assert_root_authority(crt, certificate_request)

        # OCSP
        # authorityInfoAccess = OCSP;URI:{{cert.ocsp_distribution_host}}
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.AUTHORITY_INFORMATION_ACCESS)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value[0], x509.AccessDescription(
            AuthorityInformationAccessOID.OCSP,
            x509.UniformResourceIdentifier(certificate_request.ocsp_distribution_host)
        ))

        # authorityKeyIdentifier = keyid:always, issuer
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.AUTHORITY_KEY_IDENTIFIER)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value.key_identifier, _key_identifier_from_public_key(self.key.key.public_key()))

        # subjectKeyIdentifier = hash
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_KEY_IDENTIFIER)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value.digest, _key_identifier_from_public_key(self.key.key.public_key()))

    def test_generate_root_ca(self):
        certificate_request = CertificateFactory(key=self.key.serialize())
        certhandler = Certificate()
        certhandler.create_certificate(certificate_request)

        crt = certhandler.certificate

        self.assertEqual(crt.serial_number, int(certificate_request.serial))
        self.assertEqual(crt.public_key().public_numbers(), self.key.key.public_key().public_numbers())
        self.assertEqual(crt.not_valid_before, datetime.datetime(
            year=certificate_request.created_at.year,
            month=certificate_request.created_at.month,
            day=certificate_request.created_at.day
        ))

        self.assertEqual(crt.not_valid_after, datetime.datetime(
            year=certificate_request.expires_at.year,
            month=certificate_request.expires_at.month,
            day=certificate_request.expires_at.day
        ))

        # subject
        self.assert_subject(crt.subject, certificate_request)
        # issuer
        self.assert_subject(crt.issuer, certificate_request)
        self.assert_crl_distribution(crt, certificate_request)
        self.assert_root_authority(crt, certificate_request)

        # OCSP
        # authorityInfoAccess = OCSP;URI:{{cert.ocsp_distribution_host}}
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.AUTHORITY_INFORMATION_ACCESS)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value[0], x509.AccessDescription(
            AuthorityInformationAccessOID.OCSP,
            x509.UniformResourceIdentifier(certificate_request.ocsp_distribution_host)
        ))

        # authorityKeyIdentifier = keyid:always, issuer
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.AUTHORITY_KEY_IDENTIFIER)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value.key_identifier, _key_identifier_from_public_key(self.key.key.public_key()))

        # subjectKeyIdentifier = hash
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_KEY_IDENTIFIER)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value.digest, _key_identifier_from_public_key(self.key.key.public_key()))

    def test_generate_root_ca_no_crl_distribution(self):
        certificate_request = CertificateFactory(crl_distribution_url=None, key=self.key.serialize())
        certhandler = Certificate()
        certhandler.create_certificate(certificate_request)

        crt = certhandler.certificate

        # subject
        self.assert_subject(crt.subject, certificate_request)
        # issuer
        self.assert_subject(crt.issuer, certificate_request)
        self.assert_root_authority(crt, certificate_request)

        self.assertEqual(crt.serial_number, int(certificate_request.serial))
        self.assertEqual(crt.public_key().public_numbers(), self.key.key.public_key().public_numbers())

        # crlDistributionspoints
        with self.assertRaisesMessage(ExtensionNotFound, "No <ObjectIdentifier(oid=2.5.29.31, name=c"
                                                         "RLDistributionPoints)> extension was found"):
            crt.extensions.get_extension_for_oid(ExtensionOID.CRL_DISTRIBUTION_POINTS)

    def test_generate_root_ca_no_ocsp(self):
        certificate_request = CertificateFactory(ocsp_distribution_host=None, key=self.key.serialize())
        certhandler = Certificate()
        certhandler.create_certificate(certificate_request)

        crt = certhandler.certificate

        # subject
        self.assert_subject(crt.subject, certificate_request)
        # issuer
        self.assert_subject(crt.issuer, certificate_request)
        self.assert_crl_distribution(crt, certificate_request)
        self.assert_root_authority(crt, certificate_request)

        self.assertEqual(crt.serial_number, int(certificate_request.serial))
        self.assertEqual(crt.public_key().public_numbers(), self.key.key.public_key().public_numbers())

        # OCSP
        # authorityInfoAccess = OCSP;URI:{{cert.ocsp_distribution_host}}
        with self.assertRaisesMessage(ExtensionNotFound, "No <ObjectIdentifier(oid=1.3.6.1.5.5.7.1.1"
                                                         ", name=authorityInfoAccess)> extension was found"):
            crt.extensions.get_extension_for_oid(ExtensionOID.AUTHORITY_INFORMATION_ACCESS)

    def test_generate_root_ca_passphrase(self):
        certificate_request = CertificateFactory(key=self.key.serialize(passphrase=b"superSecret"))
        certhandler = Certificate()
        certhandler.create_certificate(certificate_request, passphrase=b"superSecret")

        crt = certhandler.certificate
        # subject
        self.assert_subject(crt.subject, certificate_request)
        # issuer
        self.assert_subject(crt.issuer, certificate_request)
        self.assert_crl_distribution(crt, certificate_request)
        self.assert_root_authority(crt, certificate_request)

        self.assertEqual(crt.serial_number, int(certificate_request.serial))
        self.assertEqual(crt.public_key().public_numbers(), self.key.key.public_key().public_numbers())

    def test_generate_root_ca_wrong_passphrase(self):
        certificate = CertificateFactory(key=self.key.serialize(passphrase=b"superSecret"))
        certhandler = Certificate()
        with self.assertRaisesMessage(PassPhraseError, "Bad passphrase, could not decode private key"):
            certhandler.create_certificate(certificate, passphrase=b"superSecret_wrong")

    def test_serialize_root_certificate(self):
        certificate = CertificateFactory(key=self.key.serialize())
        certhandler = Certificate()
        certhandler.create_certificate(certificate)

        pem = certhandler.serialize()

        crt = certhandler.load(pem).certificate

        self.assertEqual(crt.serial_number, int(certificate.serial))
        self.assertEqual(crt.public_key().public_numbers(), self.key.key.public_key().public_numbers())
        self.assertEqual(crt.not_valid_before, datetime.datetime(
            year=certificate.created_at.year,
            month=certificate.created_at.month,
            day=certificate.created_at.day
        ))

    def test_serialize_no_certificate(self):
        certhandler = Certificate()
        with self.assertRaisesMessage(RuntimeError, "No certificate object"):
            certhandler.serialize('test_root_Ca.pem')
