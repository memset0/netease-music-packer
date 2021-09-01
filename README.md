# netease-music-packer

网易云音乐本地文件打包器

### Usage

复制 `config.sample.yml` 为 `config.yml`，按照填写配置文件。

```shell
pip install requests pycryptodome mutagen ncmdump
python main.py
```

### Attention

为了绕过网易限制爬取歌单详情，需要用到 [Binaryify/NeteaseCloudMusicApi](https://github.com/Binaryify/NeteaseCloudMusicApi)，并输入您的账号密码。您应已完整审阅开源代码并自行部署的上述 API 服务运行本程序以保证个人用户数据安全。