#!//usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import json
import Image
import urllib
import urllib2
import hashlib
import sqlite3
import ConfigParser
from string import Template  

class video:
    def __init__(self):
        self.convert_list = []
        config = ConfigParser.ConfigParser();
        with open('config.cfg', 'r') as cfgfile:
            config.readfp(cfgfile) 
            self.file_type = config.get('config', 'file_type').replace('"', '').split('|')
            self.upload_dir = config.get('config', 'upload_dir')
            self.output_dir = config.get('config', 'output_dir')
            self.pic_dir = config.get('config', 'pic_dir')
            self.output_resolution = config.get('config', 'output_resolution').replace('"', '').split('|')
            self.output_bitrate = config.get('config', 'output_bitrate').replace('"', '').split('|')
            self.watermark_position = config.get('config', 'watermark_position')
            self.watermark_overlay = config.get('config', 'watermark_overlay')
            self.watermark = config.get('config', 'watermark').replace('"', '').split('|')
            self.pic_resolution = config.get('config', 'pic_resolution').split('x')
            self.pic_count = int(config.get('config', 'pic_count'))
            self.text = config.get('config', 'text').replace('"', '').split('|')
            self.host = config.get('config', 'host')
            self.db = config.get('config', 'db')
            self.output_deep = config.get('config', 'output_deep')
            self.pic_deep = config.get('config', 'pic_deep')
            self.API = config.get('config', 'API')
            system_cmd = config.get('config', 'system_cmd')
            if system_cmd:
                self.ffmpeg_cmd = 'ffmpeg'
                self.ffprobe_cmd = 'ffprobe'
            else:
                self.ffmpeg_cmd = './bin/ffmpeg'
                self.ffprobe_cmd = './bin/ffprobe'

    def getFile(self):
        upload_files = os.listdir(self.upload_dir)
        if not upload_files:
            return False
        for f in upload_files:
            (name,ext) = os.path.splitext(f);
            if ext[1:].lower() not in self.file_type:
                continue
            if name + '.scan' in upload_files:
                continue
            self.convert_list.append(f)
            
    def convert(self):
        if not self.convert_list:
            return False;
        filelist = self.convert_list[:]
        for filename in filelist:
            self.__setConvertedFlag(filename)
            input_fullname = self.upload_dir + os.path.sep + filename
            video_info = self.__getVideoInfo(input_fullname)
            original_bitrate = video_info["format"]["bit_rate"]
            #话说把浮点型的字符串转为整数型的字符串没有更好的办法吗？
            video_duration = str(int(float(video_info["format"]["duration"])))
            (name,ext) = os.path.splitext(filename);
            
            #进行转码
            i = 0
            m3u8 = '#EXTM3U\n'
            xml_m3u8 = '';
            xml_text = '';
            output_path = ''
            info = []
            for data in self.output_bitrate:
                if int(data.replace('k', '000')) > int(original_bitrate):
                    continue
                output_path = self.__creatDir(self.output_dir, name + os.path.sep + str(i + 1)) 
                output_file = output_path + os.path.sep + name + '.mp4'
                watermark = self.__getWatermark(self.watermark[i])
                cmd_mp4 = self.__getMp4(input_fullname, self.output_resolution[i], watermark, data, output_file)
                os.system(cmd_mp4)
                cmd_m3u8 = self.__getM3u8(output_file, 10, output_path)
                os.system(cmd_m3u8)
                m3u8 = m3u8 + '#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=' + data.replace('k', '000') +',RESOLUTION=' + self.output_resolution[i] + '\n'
                m3u8 = m3u8 + str(i + 1) + '/index.m3u8\n'
                xml_m3u8 = xml_m3u8 + str(i + 1) + '/index.m3u8|'
                xml_text = xml_text + self.text[i]+'|'
                os.remove(output_file)
                info_item = {'path':output_path+"/index.m3u8", 'bitrate':data, 'resolution':self.output_resolution[i]}
                info.append(info_item)
                i = i + 1
                
            #生成多码率的m3u8文件
            pos = output_path.rfind(os.path.sep)    
            self.__createM3u8(m3u8, output_path[:pos] + os.path.sep + 'index.m3u8')
            
            #生成视频截图
            for i in range(0, self.pic_count):
                pic_output_path = self.__creatDir(self.pic_dir, name) 
                start_time = int(video_duration) / self.pic_count * i
                pic_filename = pic_output_path + os.path.sep + str(i + 1) + '.jpg'
                video_time = start_time + 3
                if video_time >= int(video_duration):
                    video_time = int(video_duration) - 1
                cmd_pic = self.__getPic(input_fullname, video_time, pic_filename)
                os.system(cmd_pic)
                im = Image.open(pic_filename)  
                im_ss = im.resize((int(self.pic_resolution[0]),int(self.pic_resolution[1])))  
                im_ss.save(pic_filename)
            
            #生成xml文件
            year = time.strftime("%Y", time.localtime())
            month = time.strftime("%m", time.localtime())
            xml_dir = os.path.sep + year + os.path.sep + month + os.path.sep + name
            xml_url = self.host + self.output_dir[int(self.output_deep):] + xml_dir
            self.__getXML(xml_m3u8[:-1], xml_text[:-1], xml_url, self.output_dir + xml_dir)
            
            #将转码后的数据存入数据库中
            conn = sqlite3.connect(self.db)
            md5 = self.__getFileMd5(input_fullname)
            sql = "update video set duration=" + video_duration + ", info='" + json.dumps(info) + "' where local_md5='"+md5+"'"
            conn.execute(sql)
            conn.commit()
            
            #通知API
            if self.API:
                self.__notify(md5)

    
    #对已经处理过的视频文件作标记        
    def __setConvertedFlag(self, filename):
        if filename not in self.convert_list:
            return False
        (name,ext) = os.path.splitext(filename);
        fullpath = self.upload_dir + os.path.sep + name + '.scan'
        f = open(fullpath, 'w')
        f.close()
        self.convert_list.remove(filename)
    
    #创建文件夹    
    def __creatDir(self, filepath, dirname):
        year = time.strftime("%Y", time.localtime())
        month = time.strftime("%m", time.localtime())
        create_dir = filepath + os.path.sep + year + os.path.sep + month + os.path.sep + dirname
        if not os.path.exists(create_dir):
            os.makedirs(create_dir)
        return create_dir
    
    #获取水印参数    
    def __getWatermark(self, watermark):
        if not self.watermark_overlay:
            return ''
        overlay = self.watermark_overlay.split(':')
        watermark_str = '-vf "movie=' + 'watermark' + os.path.sep + watermark + ' [watermark]; [in][watermark]'
        if self.watermark_position == '1':
            return watermark_str + ' overlay=' + self.watermark_overlay + ' [out]"'
        if self.watermark_position == '2':
            return watermark_str + ' overlay=main_w-overlay_w-' + self.watermark_overlay + '    [out]"'
        if self.watermark_position == '3':
            return watermark_str + ' overlay=' + overlay[0] + ':main_h-overlay_h-' + overlay[1] + ' [out]"'
        if self.watermark_position == '4':
            return watermark_str + ' overlay=main_w-overlay_w-' + overlay[0] + ':main_h-overlay_h-' + overlay[1] + ' [out]"'
    
    #获取转mp4的命令
    def __getMp4(self, _input_file, _output_resolution, _watermark, _bitrate, _output_file):
        cmd_mp4 = Template(self.ffmpeg + ' -i ${input_file} -s ${output_resolution} ${watermark} -ab 128k -acodec libmp3lame -ac 1 -ar 22050 -r 29.97 -b ${bitrate} -y ${output_file}')
        return cmd_mp4.substitute(input_file = _input_file, output_resolution = _output_resolution, watermark = _watermark, bitrate = _bitrate, output_file = _output_file)
    
    #获取生成hls切片和m3u8文件的命令
    def __getM3u8(self, _input_file, _hls_time, _output_path):
        cmd_m3u8 = Template(self.ffmpeg + ' -i ${input_file} -codec copy -bsf:v h264_mp4toannexb -hls_time ${hls_time} -hls_list_size 0 -hls_segment_filename "${output_path}/index%04d.ts" ${output_path}/index.m3u8')
        return cmd_m3u8.substitute(input_file = _input_file, hls_time = _hls_time, output_path = _output_path)
    
    #获取生成视频截图的命令    
    def __getPic(self, _input_file, _from_time, _output_file):
        cmd_pic = Template(self.ffmpeg + ' -i ${input_file} -y -f image2 -ss ${from_time} -vframes 1 ${output_file}')
        return cmd_pic.substitute(input_file = _input_file, from_time = _from_time, output_file = _output_file)

    #创建目录型m3u8
    def __createM3u8(self, content, output_file):
        f = open(output_file, 'w')
        f.write(content)
        f.close() 
    
    #获取视频文件的md5值    
    def __getFileMd5(self, filename):
        if not os.path.isfile(filename):
            return
        h = hashlib.md5()
        f = file(filename,'rb')
        while True:
            b = f.read(8096)
            if not b :
                break
            h.update(b)
        f.close()
        return h.hexdigest()
        
    #获取视频信息    
    def __getVideoInfo(self, filename):
        cmd_info = self.ffprobe_cmd + ' -v quiet -print_format json -show_format -i ' + filename
        result = os.popen(cmd_info).read()
        return json.loads(result)
        
    def __getXML(self, _m3u8, _text, _url, path):
        xml = Template('<?xml version="1.0" encoding="utf-8"?><videodata><defa><![CDATA[${m3u8}}]]></defa><deft><![CDATA[${text}}]]></deft><preurl><![CDATA[${url}}]]></preurl></videodata>')
        result = xml.substitute(m3u8 = _m3u8, text = _text, url = _url)
        f = open(path + '/index.xml', 'w')
        f.write(result)
        f.close() 
        
    def __notify(self, md5):
        post = {'md5':md5}
        post_urlencode = urllib.urlencode(post)
        result = urllib2.Request(url = self.API,data = post_urlencode)
        urllib2.urlopen(result)
        
if __name__=="__main__":
    video = video()
    while(True):
        video.getFile()
        video.convert()
        time.sleep(30)

