import os
import traceback
import pyotp
from qrcode import QRCode, constants
from api.configs.config import BaseConfig

class GoogleAuthenticatorClient:
    def __init__(self):
        self.secret_key = BaseConfig.GOOGLE_KEY

    def create_secret(self):
        """
        生成google auth 需要的密钥
        :return:
        """
        self.secret_key = pyotp.random_base32(64)
        return self.secret_key

    def create_secret_qrcode(self, name=None, issuer_name=None, save_to_file=True):
        """
        根据用户名及密钥生成二维码图片
        :param name:用户名
        :param issuer_name:发行人
        :param save_to_file: 保存至文件
        :return:
        """
        data = pyotp.totp.TOTP(self.secret_key).provisioning_uri(
            name=name, issuer_name=issuer_name)
        qr = QRCode(
            version=1,
            error_correction=constants.ERROR_CORRECT_L,
            box_size=6,
            border=4, )
        try:
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image()
            if save_to_file:
                base_dir = os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__)))
                dir_path = os.path.join(base_dir, 'static', 'image')
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)
                filepath = dir_path + os.sep + self.secret_key + '.png'
                img.save(filepath)  # 保存条形码图片
                return True, filepath
            else:
                return img.get_image()
        except Exception as e:
            traceback.print_exc()
            return False, None

    def verify_code_func(self, verify_code):
        # print(str(self.secret_key))

        t = pyotp.TOTP(self.secret_key)
        result = t.verify(verify_code)
        return result



# 如果开启，则生成图片保存在本地
def saveGoogleAuthImage():
    # print("Google is open %s" % BaseConfig.GOOGLE_ENABLE)
    if BaseConfig.GOOGLE_ENABLE:
        google_auth_ = GoogleAuthenticatorClient()
        status, path = google_auth_.create_secret_qrcode(
            name=BaseConfig.GOOGLE_NAME, issuer_name=BaseConfig.GOOGLE_ISSUER_NAME, save_to_file=True)
        if status:
            print("*"*30)
            print("\n")
            print("Google OR code save in {0}".format(path))
            print("\n")
            print("*"*30)
            return google_auth_
        print("Google OR code save is error, Please check")
        

def init_google():
    saveGoogleAuthImage()
        
# if __name__ == '__main__':
#     secret_key = 'PU6PY6FWPVQ4BXE7ZP6X7YMVM3BH3ODS7SW53GL3LJPED7AAQUVF2EKP6AGNFFOX'
#     google_auth_ = GoogleAuthenticatorClient(secret_key=secret_key)

#     # 随机秘钥生成
#     # secret = google_auth_.create_secret()
#     # print('秘钥', secret)

#     # # 生成图片二维码， save_to_file=True, 图片保存在本地， False 表示不保存，并显示在当前
#     image = google_auth_.create_secret_qrcode(name='slp', issuer_name='GoldBull', save_to_file=True)
#     print(image.show())

#     # 通过谷歌验证码器验证， 返回 True，表示通过， False 表示不通过
#     res = google_auth_.verify_code_func(verify_code='138914')
#     print(res)
