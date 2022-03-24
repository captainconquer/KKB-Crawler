# KKB课程爬虫

总共有5处需要手动修改一下，均备注了  `# diy place`

diy信息获取方法如下：

- cookies、headers、course_id 获取方法

进入一个已购课程的目录页，随意点开一个章节，找到类似链接

![image-01](https://raw.githubusercontent.com/renugarm/KKB-Crawler/main/pic/image-01.png)



右键，复制bash格式的curl

![image-02](https://raw.githubusercontent.com/renugarm/KKB-Crawler/main/pic/image-02.png)



将复制到的curl，粘贴到网站  [https://curlconverter.com/#python](https://curlconverter.com/#python)

自动转换成python格式的代码。把cookies、headers、course_id复制替换到脚本当中即可。

- diy place 4 对应设置自动创建课程目录的位置，默认是C盘，会自动创建一个已课程ID命名的文件夹，这里可以自行修改。

- diy place 5是保存输出信息的位置，默认是桌面的data.json文件，可以自行修改。

