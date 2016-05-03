#video_convert.py

##1. 部署说明
文件目录形式如下

├── client  --上传视频用的客户端示例代码

│   ├── asset    --客户端使用的js/css/flash文件

│   │   ├── jquery-1.10.2.min.js    --jquery

│   │   ├── md5.js    --webuploader程序自带

│   │   ├── Uploader.swf    --webuploader程序自带

│   │   ├── webuploader.css    --webuploader程序自带

│   │   └── webuploader.js    --webuploader程序自带

│   ├──  api.php    --接收视频转码通知API的示例程序

│   └──  index.html    --上传文件的页面示例代码

├── convert    --转码程序

│   ├──  bin    --可执行文件目录

│   │   ├── ffmpeg    --转码工具（如果需要，可以点击[这里](http://pan.baidu.com/s/1jInjVMm)下载）

│   │   ├── ffprobe    --用于获取视频信息的程序（如果需要，可以点击[这里](http://pan.baidu.com/s/1kVgwpTH)下载）

│   │   ├── start.sh    --启动转码服务的脚本

│   │   └── stop.sh    --停止转码服务的脚本

│   ├──  logs    --log文件夹

│   ├──  watermark    --水印文件夹

│   │   ├── 1.png    --示例水印图片

│   │   ├── 2.png    --示例水印图片

│   │   └── 3.png    --示例水印图片

│   ├──  config.cfg    --转码程序配置文件

│   ├──  video.db    --转码程序使用的数据库（sqlite数据库）

│   └──  video.py    --转码程序

├── server    --流媒体服务器

│   ├──  output    --转码后视频输出目录（文件夹名可以自定义）

│   ├──  pic    --转码后图片输出目录（文件夹名可以自定义）

│   ├──  uploads    --上传视频存储目录

│   ├──  api.php    --视频转码API页面

│   ├──  config.php    --流媒体服务器配置文件

│   ├──  crossdomain.xml    --用于设置跨域的文件

│   └──  fileUpload.php    --处理视频上传的程序

└── README.md

服务器上需要存放convert文件夹里面的东西和server里面的东西，其中server里面的内容要部署在可以通过http访问的文件夹下面，而convert文件夹可以随意放，保证convert/bin文件夹下面的文件以及video.py文件有可执行权限，convert/logs文件夹以及video.db有读写权限，其余文件保证有可读权限。
server/output，server/pic以及server/uploads这三个文件夹也可以放在其他的地方，但是其中output，pic这两个文件夹因为需要能够进行web访问，所以虽然可以放在其他的地方，但是务必保证其在http服务器里面，而uploads文件夹就可以随意放在任何地方，但是需要保证其有读写权限。

##2. 转码工具配置文件说明(convert/config.cfg)

<table>
    <thead>
        <tr> 
            <th>项目</th>
            <th>类型</th>
            <th>说明</th>
            <th>示例</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>file_type</td>
            <td>string</td>
            <td>程序进行转码的文件类型，多个类型用"|"分隔</td>
            <td>"rmvb|flv|mp4|wmv|mpg|avi|mpeg"</td>
        </tr>
        <tr>
            <td>upload_dir</td>
            <td>string</td>
            <td>上传的视频文件存放的目录，同时也是程序定时检查是否有视频需要转码的目录，请使用绝对路径</td>
            <td>/home/sbin/www/test/uploads</td>
        <tr>
        <tr>
            <td>output_dir</td>
            <td>string</td>
            <td>转码后的视频输出的文件夹，请使用绝对路径。</td>
            <td>/home/sbin/www/test/output</td>
         </tr>
         <tr>
            <td>output_deep</td>
            <td>int</td>
            <td>使用host配置项替换output_dir配置项前x个字符</td>
            <td>15</td>
        </tr>
        <tr>
            <td>pic_dir</td>
            <td>string</td>
            <td>转码后视频截图输出的文件夹，请使用绝对路径。</td>
            <td>/home/sbin/www/test/pic</td>
        </tr>
        <tr>
            <td>pic_deep</td>
            <td>int</td>
            <td>使用host配置项替换pic_dir配置项前x个字符</td>
            <td>15</td>
        </tr>
        <tr>
            <td>output_resolution</td>
            <td>string</td>
            <td>转码后输出视频的分辨率，多个分辨率用"|"分隔</td>
            <td>"800x480|1280x720|1920x1080"</td>
        </tr>
        <tr>
            <td>output_bitrate</td>
            <td>string</td>
            <td>转码后输出视频的比特率，多个比特率用"|"分隔</td>
            <td>"675k|1800k|4050k"</td>
        </tr>
        <tr>
            <td>watermark_position</td>
            <td>int</td>
            <td>水印的位置，1：左上角；2：右上角；3：左下角；4：右上角</td>
            <td>2</td>
        </tr>
        <tr>
            <td>watermark_overlay</td>
            <td>string</td>
            <td>水印的位置，距离视频角的边缘的距离，单位是px</td>
            <td>10:10</td>
        </tr>
        <tr>
            <td>pic_resolution</td>
            <td>string</td>
            <td>截图的分辨率</td>
            <td>640x480</td>
        </tr>
        <tr>
            <td>pic_count</td>
            <td>int</td>
            <td>生成截图的数量</td>
            <td>5</td>
        </tr>
        <tr>
            <td>watermark</td>
            <td>string</td>
            <td>水印的名称，存放在watermark目录下，一个名称对应一种分辨率</td>
            <td>"1.png|2.png|3.png"</td>
        </tr>
        <tr>
            <td>db</td>
            <td>string</td>
            <td>数据库的位置，请使用绝对路径</td>
            <td>/home/sbin/develop/convert/video.db</td>
        </tr>
        <tr>
            <td>host</td>
            <td>string</td>
            <td>流媒体服务使用的域名，一定要保留最后的'/'</td>
            <td>http://t.org/</td>
        </tr>
        <tr>
            <td>text</td>
            <td>string</td>
            <td>不同的分辨率对应的名称</td>
            <td>"标清|高清|超清"</td>
        </tr>
        <tr>
            <td>API</td>
            <td>string</td>
            <td>API通知的地址</td>
            <td>http://t.org/test/api.php</td>
        </tr>
        <tr>
            <td>system_cmd</td>
            <td>int</td>
            <td>是使用系统的程序还是自带的程序，如果为0，则使用convert/bin下面的ffmpeg和ffprobe，如果文件夹下面没有这两个文件会报错。如果为1，请保证系统已安装ffmpeg，否则也会报错</td>
            <td>1</td>
        </tr>
    </tbody>
</table>


##3. 流媒体服务器配置说明(server/config.php)
里面只有一个配置项，用来配置转码程序配置文件的绝对路径。

##4. 使用说明
具体的使用流程是：上传视频->转码->通知配置好的URL转码完成->通过调用API来获取更多视频信息
基本上按照按照部署说明中的引导部署完毕之后，运行convert/bin/start.sh启动转码服务后就行了，然后上传视频，等转码完成之后，通过访问转码后生成的index.m3u8或者index.xml文件，结合ckplayer之类的网页视频播放器就可以进行视频播放了。

##5. 致谢
server端的代码中大量引用了[kazaff](https://github.com/kazaff)的[webuploaderDemo](https://github.com/kazaff/webuploaderDemo)这个项目的代码，在这里对您的指导表示衷心的感谢。