import OpenSSL
from dateutil import parser





def check_cer(cert_str):
    try:
        # cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, open(cert_str).read())
        cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert_str)
        subject = cert.get_subject()
        certIssue = cert.get_issuer()

        datetime_struct_start = parser.parse(cert.get_notBefore().decode("UTF-8"))
        datetime_struct_end = parser.parse(cert.get_notAfter().decode("UTF-8"))

        # for item in certIssue.get_components():
        #     print(item)
        # print("证书域名: ", subject.CN)
        # print("颁发机构: ", certIssue.CN)
        # print("证书版本: ", cert.get_version())
        # print("开始时间：", datetime_struct_start.strftime('%Y-%m-%d %H:%m:%S'))
        # print("到期时间：", datetime_struct_end.strftime('%Y-%m-%d %H:%m:%S'))
        # print("是否过期: ", cert.has_expired())
        # print("加密算法: ", cert.get_signature_algorithm().decode("UTF-8"))

        return {
            "domain": subject.CN,
            "start_date": datetime_struct_start.strftime('%Y-%m-%d %H:%m:%S'),
            "expire_date": datetime_struct_end.strftime('%Y-%m-%d %H:%m:%S'),
            "is_expired": cert.has_expired(),
            "issuer": certIssue.CN.encode('UTF-8'),
            "tls_version": cert.get_version(),
            "encryption": cert.get_signature_algorithm().decode("UTF-8")
        }

    except Exception as e:
        print(e)
        return False

