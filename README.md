# bilibili 下载

- [ ] 合集下载

## 功能

- [x] 单视频下载
- [x] 收藏夹下载

```json
{
    "download_dir": "C:/Users/xxx/Videos/",
    "favorite_list": [
        {
            "fid": "3098863103",
            "out_dir":"./out",
            "download_video": false
        }
    ],
    "video_list": [
        {
            "bvid": "BV1kS421w7xe"
        }
    ],
    "channel_series":[
        {
            "sid": "3164316",
            "download_video": false
        }
    ]
}
```

### 配置参数

```json
{
    "id":"1111",
    "out_dir":"./out",
    "download_video":true
}
```

## 使用

- 需要Chrome浏览器
- 需要有登录状态，在浏览器中登录（自动获取cookies）
- 下载配置要到 download.json 中
- 需要下载ffmpeg压缩包，并解压到当前ffmpeg文件夹中
- 推荐使用vscode
