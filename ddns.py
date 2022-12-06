import json
import requests
from requests.adapters import HTTPAdapter

# dnspod api 动态域名解析————只需要定时执行此脚本
s = requests.session()
s.mount('https://', HTTPAdapter(max_retries=5))  # 超时重传次数
config = json.load(open('ddns.json', 'r', encoding='utf8'))
login_token = config['API_ID']+','+config['TOKEN']  # API_ID,TOKEN
domain = config['domain']   # 根域名
hostname = config['hostname']    # 主机名/子域(www)


def get_ip(ipv6: bool = True):
    if ipv6:
        url = 'https://api6.ipify.org?format=json'
    else:
        url = 'https://api4.ipify.org?format=json'
    res = requests.get(url)
    d = json.loads(res.text)
    return d['ip']


def get_record_id():
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
    record_id = None
    for i in rs['records']:
        if i['name'] == hostname:
            record_id = i['id']
    print("dns记录id:" + record_id)
    return record_id


def update_record(ip):
    rs = None
    record_id = get_record_id()
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
