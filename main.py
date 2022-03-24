import requests
import time
import json
from jsonpath import jsonpath
import io
import sys
import os
import winreg

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')  # 改变标准输出的默认编码

millis = int(round(time.time() * 1000))  # 时间戳

# 汇总信息初始化
sum_list = {}

# diy place 1
# 课程ID，需根据实际设置
course_id = '238092'

# cookies，需根据实际设置
cookies = {
    # diy place 2
    # 这里填写你的 KKB cookies
}

# headers，需根据实际设置
headers = {
    # diy place 3
    # 这里填写 headers
}


# 获取桌面路径
def get_desktop():
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
    path = winreg.QueryValueEx(key, "Desktop")[0]
    print(path)
    return path


# 创建文件夹的函数
def mkdir(path):
    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")
    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists = os.path.exists(path)
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path)
        # print(path + ' 创建成功')
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        # print(path + ' 目录已存在')
        return False


# 获取 media_id, 即视频ID
def get_media_id(content_id):
    params = {
        'content_id': content_id,
    }
    response = requests.get('https://weblearn.kaikeba.com/student/course/content',
                            headers=headers,
                            params=params,
                            cookies=cookies)
    media_id = jsonpath(json.loads(response.text), '$.data.content[0].boot_params.media_id')[0]
    # print(media_id)
    return media_id


# 获取 m3u8 链接地址
def get_m3u8_url(media_id, accessToken):
    headers = {
        'authority': 'api-vod.baoshiyun.com',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
        'dnt': '1',
        'sec-ch-ua-mobile': '?0',
        'user-agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36',
        'sec-ch-ua-platform': '"Windows"',
        'content-type': 'application/json;charset=UTF-8',
        'accept': '*/*',
        'origin': 'https://learn.kaikeba.com',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://learn.kaikeba.com/',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    params = {
        'mediaId': media_id,
        'accessToken': accessToken,
    }
    response = requests.get('https://api-vod.baoshiyun.com/vod/v1/platform/media/detail', headers=headers, params=params)
    m3u8_url = jsonpath(json.loads(response.text), '$.data.mediaMetaInfo.videoGroup[0].playURL')[0]
    return m3u8_url


# 获取 access_token
def get_access_token():
    response = requests.get('https://weblearn.kaikeba.com/get/bsy_video/access_token', headers=headers, cookies=cookies)
    access_token = json.loads(response.text)['data']['access_token']
    # print(access_token)
    return access_token


# 提交参数
params = {
    'course_id': course_id,
    '__timestamp': millis,
}
response = requests.get('https://weblearn.kaikeba.com/student/courseinfo', headers=headers, params=params, cookies=cookies)
# print(response.text)

# 循环获取大章节信息
i = 0  # chapter_list 计数
sum_list['chapter_list'] = {}
for chapter_name, chapter_id in zip(jsonpath(json.loads(response.text), '$.data.chapter_list[*].chapter_name'),
                                    jsonpath(json.loads(response.text), '$.data.chapter_list[*].chapter_id')):
    i += 1
    sum_list['chapter_list'][i - 1] = {}
    sum_list['chapter_list'][i - 1]['chapter_sort'] = "第%s章" % (i)
    sum_list['chapter_list'][i - 1]['chapter_id'] = chapter_id
    sum_list['chapter_list'][i - 1]['chapter_name'] = chapter_name
    sum_list['chapter_list'][i - 1]['section_list'] = {}

    params = {
        'course_id': course_id,
        'chapter_id': chapter_id,
        '__timestamp': millis,
    }
    response = requests.get('https://weblearn.kaikeba.com/student/chapterinfo', headers=headers, params=params, cookies=cookies)
    # print(response.text)

    # 循环获取小节信息
    s = 0  # section_list 计数
    for section_id, section_name in zip(
            jsonpath(json.loads(response.text), '$.data.section_list[*].section_id'),
            jsonpath(json.loads(response.text), '$.data.section_list[*].section_name'),
    ):
        s += 1
        sum_list['chapter_list'][i - 1]['section_list'][s - 1] = {}
        sum_list['chapter_list'][i - 1]['section_list'][s - 1]['section_id'] = section_id
        if section_name == '':
            sum_list['chapter_list'][i - 1]['section_list'][s - 1]['section_name'] = jsonpath(
                json.loads(response.text), '$.data.section_list[%s].group_list[0].group_name' % (s - 1))[0]
        else:
            sum_list['chapter_list'][i - 1]['section_list'][s - 1]['section_name'] = section_name
        sum_list['chapter_list'][i - 1]['section_list'][s - 1]['content_list'] = {}

        # diy place 4
        # 定义要创建的目录. 默认保存在C盘根目录下,以课程ID命名文件夹.
        mkpath = "C:\\%s\\%s\\%s" % (course_id, "第%s章：%s" % (i, chapter_name), "第%s节：%s" % (s, section_name))

        # 创建 章节 和 小节 目录
        mkdir(mkpath)

        # 循环获取内容信息
        m = 1  # content_list 计数
        for content_id, content_title, content_type in zip(
                jsonpath(json.loads(response.text),
                         '$.data.section_list[%s].group_list[0].content_list[*].content_id' % (s - 1)),
                jsonpath(json.loads(response.text),
                         '$.data.section_list[%s].group_list[0].content_list[*].content_title' % (s - 1)),
                jsonpath(json.loads(response.text),
                         '$.data.section_list[%s].group_list[0].content_list[*].content_type' % (s - 1))):
            m += 1
            sum_list['chapter_list'][i - 1]['section_list'][s - 1]['content_list'][m - 1] = {}
            sum_list['chapter_list'][i - 1]['section_list'][s - 1]['content_list'][m - 1]['content_id'] = content_id
            sum_list['chapter_list'][i - 1]['section_list'][s - 1]['content_list'][m - 1]['content_title'] = content_title
            media_id = 'none'
            m3u8_url = 'none'
            if content_type == 3:
                content_type = str(content_type) + '-点播'
                media_id = get_media_id(content_id)
                m3u8_url = get_m3u8_url(media_id, get_access_token())
            elif content_type == 6:
                content_type = str(content_type) + '-资料'
            elif content_type == 7:
                content_type = str(content_type) + '-直播回放'
                media_id = get_media_id(content_id)
                m3u8_url = get_m3u8_url(media_id, get_access_token())
            elif content_type == 16:
                content_type = str(content_type) + '-直播待开播'
            else:
                pass
            sum_list['chapter_list'][i - 1]['section_list'][s - 1]['content_list'][m - 1]['content_type'] = content_type
            sum_list['chapter_list'][i - 1]['section_list'][s - 1]['content_list'][m - 1]['media_id'] = media_id
            sum_list['chapter_list'][i - 1]['section_list'][s - 1]['content_list'][m - 1]['m3u8_url'] = m3u8_url

print(sum_list)

# diy place 5
# 默认将信息保存在桌面 data.json 文件, 可自行修改
with open(get_desktop() + '\data.json', 'w') as f:
    json.dump(sum_list, f)