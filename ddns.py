import json
import requests
from requests.adapters import HTTPAdapter

# dnspod api 动态域名解析————只需要定时执行此脚本
s = requests.session()
s.mount('https://', HTTPAdapter(max_retries=5))  # 超时重传次数
login_token = '366561,334c67995bc8b9dd1c1aacb90bbadddc'  # API_ID,TOKEN
domain = 'koader.top'   # 根域名
hostname = 'db.test'    # 主机名/子域(www)


def get_ip(ipv6: bool = True):
    if ipv6:
        url = 'https://api6.ipify.org'
    else:
        url = 'https://api4.ipify.org'
    return requests.get(url)


def get_record_id(ip):
    print("获取dns记录ing，可能会卡")
    login = None
    url = 'https://dnsapi.cn/Record.List'
    form = {
        'domain': domain,
        'login_token': login_token
    }
    try:
        login = s.post(url=url, data=form, timeout=2)
    except requests.exceptions.RequestException:
        print("请求超时，请重试")
    rs = json.loads(login.text)  # 转为dict
    for i in rs['records']:
        if i['name'] == hostname:
            if i['value'] != ip:
                record_id = i['id']
                print("dns记录id:" + record_id)
                return record_id
            else:
                print('ip没有发生变化，停止运行')
                exit()


def update_record(ip):
    rs = None
    record_id = get_record_id(ip)
    print("更改解析ing，可能会卡")
    url = 'https://dnsapi.cn/Record.Ddns'
    form = {
        'domain': domain,
        'sub_domain': hostname,
        'login_token': login_token,
        'record_line': '默认',
        'value': ip,
        'record_id': record_id
    }
    try:
        rs = s.post(url=url, data=form, timeout=2)
    except requests.exceptions.RequestException:
        print("请求超时，请重试！")
    if json.loads(rs.text)['status']['code'] == '1':
        print(json.loads(rs.text)['status']['message'], '域名解析已更改为' + ip)
    else:
        print("操作失败")


update_record(get_ip(False))
