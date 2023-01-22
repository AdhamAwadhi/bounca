# Generated by Django 3.2.9 on 2021-12-30 08:18

import uuid

import django.contrib.postgres.fields
import django.core.validators
import django.db.models.deletion
import django_countries.fields
from django.conf import settings
from django.db import migrations, models

import x509_pki.models


class Migration(migrations.Migration):

    replaces = [('x509_pki', '0001_initial'), ('x509_pki', '0002_auto_20200719_2233'), ('x509_pki', '0003_auto_20200727_1007'), ('x509_pki', '0004_auto_20201002_2210'), ('x509_pki', '0005_auto_20201114_1830'), ('x509_pki', '0006_auto_20201114_2028'), ('x509_pki', '0007_auto_20201115_0939'), ('x509_pki', '0008_auto_20211016_2111'), ('x509_pki', '0009_auto_20211017_0921'), ('x509_pki', '0010_auto_20211017_0936'), ('x509_pki', '0011_alter_certificate_revoked_at'), ('x509_pki', '0012_crlstore_last_update'), ('x509_pki', '0013_alter_certificate_crl_distribution_url'), ('x509_pki', '0014_alter_certificate_unique_together'), ('x509_pki', '0015_keystore_p12')]

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DistinguishedName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('countryName', django_countries.fields.CountryField(blank=True, help_text='The two-character country name in ISO 3166 format.', max_length=2, null=True, verbose_name='Country')),
                ('stateOrProvinceName', models.CharField(blank=True, help_text="The state/region where your organization is located. This shouldn't be abbreviated. (1–128 characters)", max_length=128, null=True, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z@#$%^&+=\\_\\.\\-\\,\\ \\*]*$', 'Only alphanumeric characters and [@#$%^&+=_,-.] are allowed.')], verbose_name='State or Province Name')),
                ('localityName', models.CharField(blank=True, help_text='The city where your organization is located. (1–128 characters)', max_length=128, null=True, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z@#$%^&+=\\_\\.\\-\\,\\ \\*]*$', 'Only alphanumeric characters and [@#$%^&+=_,-.] are allowed.')], verbose_name='Locality Name')),
                ('organizationName', models.CharField(blank=True, help_text='The legal name of your organization. This should not be abbreviated and should include suffixes such as Inc, Corp, or LLC.', max_length=64, null=True, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z@#$%^&+=\\_\\.\\-\\,\\ \\*]*$', 'Only alphanumeric characters and [@#$%^&+=_,-.] are allowed.')], verbose_name='Organization Name')),
                ('organizationalUnitName', models.CharField(blank=True, help_text='The division of your organization handling the certificate.', max_length=64, null=True, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z@#$%^&+=\\_\\.\\-\\,\\ \\*]*$', 'Only alphanumeric characters and [@#$%^&+=_,-.] are allowed.')], verbose_name='Organization Unit Name')),
                ('emailAddress', models.EmailField(blank=True, help_text='The email address to contact your organization.', max_length=64, null=True, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z@#$%^&+=\\_\\.\\-\\,\\ \\*]*$', 'Only alphanumeric characters and [@#$%^&+=_,-.] are allowed.')], verbose_name='Email Address')),
                ('commonName', models.CharField(help_text='The fully qualified domain name (FQDN) of your server. This must match exactly what you type in your web browser or you will receive a name mismatch error.', max_length=64, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z@#$%^&+=\\_\\.\\-\\,\\ \\*]*$', 'Only alphanumeric characters and [@#$%^&+=_,-.] are allowed.')], verbose_name='Common Name')),
                # TODO Replace by switch in case Postgresql is used select ArrayField, otherwise Textfield
                # ('subjectAltNames', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=64, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z@#$%^&+=\\_\\.\\-\\,\\ \\*]*$', 'Only alphanumeric characters and [@#$%^&+=_,-.] are allowed.')]), blank=True, help_text='subjectAltName list, i.e. dns names for server certs and email adresses for client certs. (separate by comma)', null=True, size=None)),
                ('subjectAltNames', models.TextField(
                    validators=[
                        django.core.validators.RegexValidator(
                            '^[0-9a-zA-Z@#$%^&+=\\_\\.\\-\\,\\ \\*]*$',
                            'Only alphanumeric characters and [@#$%^&+=_,-.] are allowed.')],
                    blank=True,
                    help_text='subjectAltName list, i.e. dns names for server certs and email adresses for client certs. (separate by comma)',
                    null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('R', 'Root CA Certificate'), ('I', 'Intermediate CA Certificate'), ('S', 'Server Certificate'), ('C', 'Client Certificate'), ('O', 'OCSP Signing Certificate')], max_length=1)),
                ('name', models.CharField(blank=True, help_text='Name of your key, if not set will be equal to your CommonName.', max_length=128, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z@#$%^&+=\\_\\.\\-\\,\\ ]*$', 'Only alphanumeric characters and [@#$%^&+=_,-.] are allowed.')])),
                ('crl_distribution_url', models.URLField(blank=True, help_text='Base URL for certificate revocation list (CRL)', null=True, validators=[django.core.validators.RegexValidator('[^\\/]\\.crl\\.pem$', 'CRL url should end with <filename>.crl')], verbose_name='CRL distribution url')),
                ('ocsp_distribution_host', models.URLField(blank=True, help_text='Host URL for Online Certificate Status Protocol (OCSP)', null=True, verbose_name='OCSP distribution host')),
                ('created_at', models.DateField(auto_now_add=True)),
                ('expires_at', models.DateField(help_text='Select the date that the certificate will expire: for root typically 20 years, for intermediate 10 years for other types 1 year.', validators=[x509_pki.models.validate_in_future])),
                ('revoked_at', models.DateTimeField(blank=True, default=None, editable=False, null=True)),
                ('revoked_uuid', models.UUIDField(default=0)),
                ('serial', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('dn', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='x509_pki.distinguishedname')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(blank=True, help_text='The signing authority (None for root certificate)', null=True, on_delete=django.db.models.deletion.PROTECT, to='x509_pki.certificate')),
            ],
            options={
                'unique_together': {('dn', 'type', 'revoked_uuid'), ('name', 'owner', 'type', 'revoked_uuid')},
            },
        ),
        migrations.CreateModel(
            name='CrlStore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('crl', models.TextField(blank=True, null=True, verbose_name='Serialized CRL certificate')),
                ('certificate', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='x509_pki.certificate')),
                ('last_update', models.DateTimeField(auto_now=True, help_text='Date at which last crl has been generated')),
            ],
        ),
        migrations.CreateModel(
            name='KeyStore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.TextField(verbose_name='Serialized Private Key')),
                ('crt', models.TextField(verbose_name='Serialized signed certificate')),
                ('certificate', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='x509_pki.certificate')),
                ('p12', models.BinaryField(blank=True, default=None, null=True, verbose_name='Serialized PKCS 12 package with key and certificate')),
            ],
        ),
    ]
