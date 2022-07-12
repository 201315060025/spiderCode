
from copy import deepcopy
from tencentcloud.common import credential
from datetime import datetime
# 导入对应产品模块的client models。
from tencentcloud.sms.v20210111 import sms_client, models
# 导入可选配置类
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
# 导入数据
from config.config import SMSConfig, EmailConfig


class SendMessageTool(object):
    def __init__(self):
        pass

    @classmethod
    def send_message_by_sms(cls, message):
        cred = credential.Credential(SMSConfig.secretId, SMSConfig.secretKey)
        # 实例化一个http选项，可选的，没有特殊需求可以跳过。
        httpProfile = HttpProfile()
        # 如果需要指定proxy访问接口，可以按照如下方式初始化hp
        httpProfile.reqMethod = "POST"  # post请求(默认为post请求)
        httpProfile.reqTimeout = 30  # 请求超时时间，单位为秒(默认60秒)
        httpProfile.endpoint = "sms.tencentcloudapi.com"  # 指定接入地域域名(默认就近接入)
        # 实例化一个客户端配置对象，可以指定超时时间等配置
        clientProfile = ClientProfile()
        clientProfile.signMethod = "TC3-HMAC-SHA256"  # 指定签名算法
        clientProfile.language = "en-US"
        clientProfile.httpProfile = httpProfile
        # 第二个参数是地域信息，可以直接填写字符串ap-guangzhou，或者引用预设的常量
        client = sms_client.SmsClient(cred, "ap-guangzhou", clientProfile)
        req = models.SendSmsRequest()
        # 基本类型的设置:
        req.SmsSdkAppId = SMSConfig.SdkAppId
        # 短信签名内容: 使用 UTF-8 编码，必须填写已审核通过的签名，签名信息可登录 [短信控制台] 查看
        req.SignName = SMSConfig.signName
        # 短信码号扩展号: 默认未开通，如需开通请联系 [sms helper]
        req.ExtendCode = ""
        # 用户的 session 内容: 可以携带用户侧 ID 等上下文信息，server 会原样返回
        req.SessionContext = "xxx"
        # 国际/港澳台短信 senderid: 国内短信填空，默认未开通，如需开通请联系 [sms helper]
        req.SenderId = ""
        # 下发手机号码，采用 E.164 标准，+[国家或地区码][手机号]
        # 示例如：+8613711112222， 其中前面有一个+号 ，86为国家码，13711112222为手机号，最多不要超过200个手机号
        req.PhoneNumberSet = SMSConfig.sendPhone
        # 模板 ID: 必须填写已审核通过的模板 ID。模板ID可登录 [短信控制台] 查看
        req.TemplateId = SMSConfig.templateId
        # 模板参数: 若无模板参数，则设置为空
        req.TemplateParamSet = [i for i in message[0].split(',') if i]
        # 通过client对象调用DescribeInstances方法发起请求。注意请求方法名与请求对象是对应的。
        # 返回的resp是一个DescribeInstancesResponse类的实例，与请求对象对应。
        resp = client.SendSms(req)
        print(resp)

    @classmethod
    def send_message_by_email(cls, message):
        ret = True
        dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            new_message = """
            <table cellspacing="0" style='width: 700px;padding: 0; margin: 0;'>
            <caption style='padding: 0 0 5px 0; width: 700px;text-align: right; font: italic 11px "Trebuchet MS", Verdana, Arial, Helvetica, sans-serif; '> </caption>
            <tr>
            <th scope="col" style='color: #4f6b72; border-right: 1px solid #C1DAD7; border-bottom: 1px solid #C1DAD7; border-top: 1px solid #C1DAD7; letter-spacing: 2px; text-transform: uppercase; text-align: left; padding: 6px 6px 6px 12px; background: #CAE8EA  no-repeat;width:15px'></th> 
            <th scope="col" style='color: #4f6b72; border-right: 1px solid #C1DAD7; border-bottom: 1px solid #C1DAD7; border-top: 1px solid #C1DAD7; letter-spacing: 2px; text-transform: uppercase; text-align: left; padding: 6px 6px 6px 12px; background: #CAE8EA  no-repeat;'>货币名称</th>
            <th scope="col" style='color: #4f6b72; border-right: 1px solid #C1DAD7; border-bottom: 1px solid #C1DAD7; border-top: 1px solid #C1DAD7; letter-spacing: 2px; text-transform: uppercase; text-align: left; padding: 6px 6px 6px 12px; background: #CAE8EA  no-repeat;'>持有金额</th>
            <th scope="col" style='color: #4f6b72; border-right: 1px solid #C1DAD7; border-bottom: 1px solid #C1DAD7; border-top: 1px solid #C1DAD7; letter-spacing: 2px; text-transform: uppercase; text-align: left; padding: 6px 6px 6px 12px; background: #CAE8EA  no-repeat;'>持有时间</th>
            <th scope="col" style='color: #4f6b72; border-right: 1px solid #C1DAD7; border-bottom: 1px solid #C1DAD7; border-top: 1px solid #C1DAD7; letter-spacing: 2px; text-transform: uppercase; text-align: left; padding: 6px 6px 6px 12px; background: #CAE8EA  no-repeat;'>买入价</th>
            <th scope="col" style='color: #4f6b72; border-right: 1px solid #C1DAD7; border-bottom: 1px solid #C1DAD7; border-top: 1px solid #C1DAD7; letter-spacing: 2px; text-transform: uppercase; text-align: left; padding: 6px 6px 6px 12px; background: #CAE8EA  no-repeat;'>当前价格</th>
            <th scope="col" style='color: #4f6b72; border-right: 1px solid #C1DAD7; border-bottom: 1px solid #C1DAD7; border-top: 1px solid #C1DAD7; letter-spacing: 2px; text-transform: uppercase; text-align: left; padding: 6px 6px 6px 12px; background: #CAE8EA  no-repeat;'>增常率</th>
            </tr> 
            {row_datas}
            </table> 
            """
            # new_message = "<div><table><tr><tb>货币名称</td><tb>买入价</td><tb>当前价格</td><tb>增常率</td></tr>{0}</table></div>"
            tmp_msg = ""
            tmp_tag = """
            <tr>
            <td class="row" style='border-right: 1px solid #C1DAD7; border-bottom: 1px solid #C1DAD7; background: #fff; font-size:11px; padding: 6px 6px 6px 12px; color: #4f6b72;width:15px'>{0}</td>
            <td class="row" style='border-right: 1px solid #C1DAD7; border-bottom: 1px solid #C1DAD7; background: #fff; font-size:11px; padding: 6px 6px 6px 12px; color: #4f6b72;'>{1}</td>
            <td class="row" style='border-right: 1px solid #C1DAD7; border-bottom: 1px solid #C1DAD7; background: #fff; font-size:11px; padding: 6px 6px 6px 12px; color: #4f6b72;'>{2}</td>
            <td class="row" style='border-right: 1px solid #C1DAD7; border-bottom: 1px solid #C1DAD7; background: #fff; font-size:11px; padding: 6px 6px 6px 12px; color: #4f6b72;'>{3}</td>
            <td class="row" style='border-right: 1px solid #C1DAD7; border-bottom: 1px solid #C1DAD7; background: #fff; font-size:11px; padding: 6px 6px 6px 12px; color: #4f6b72;'>{4}</td>
            <td class="row" style='border-right: 1px solid #C1DAD7; border-bottom: 1px solid #C1DAD7; background: #fff; font-size:11px; padding: 6px 6px 6px 12px; color: #4f6b72;'>{5}</td>
            <td class="row" style='border-right: 1px solid #C1DAD7; border-bottom: 1px solid #C1DAD7; background: #fff; font-size:11px; padding: 6px 6px 6px 12px; color: #4f6b72;'>{6}</td>
            </tr>
            """
            for idx, i in enumerate(message):
                cp_tmp = deepcopy(tmp_tag)
                tmp_row = [str(j) for j in i.split(',') if j]
                tmp_row.insert(0, str(idx+1))
                tmp_msg += cp_tmp.format(*tmp_row)
            new_message = new_message.format(row_datas=tmp_msg)

            msg = MIMEText(new_message, 'html', 'utf-8')
            msg['From'] = formataddr(["***", EmailConfig.my_sender])
            # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['To'] = formataddr(["***", EmailConfig.my_user])
            # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            msg['Subject'] = f'{dt} 货币详情'
            # 邮件的主题，也可以说是标题
            server = smtplib.SMTP_SSL("smtp.qq.com", 465)
            # 发件人邮箱中的SMTP服务器，端口是465
            # server.login(my_sender, my_pass)
            server.login(EmailConfig.from_mail, EmailConfig.password)
            # 括号中对应的是发件人邮箱账号、邮箱密码
            server.sendmail(EmailConfig.my_sender, EmailConfig.my_user, msg.as_string())
            # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            server.quit()  # 关闭连接
        except Exception:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
            ret = False
        return ret