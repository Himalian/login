# 莆田学院校园网登录脚本

莆田学院中国移动校园网(北区宿舍、校区内`CMCC-PTU`，其它校区暂未测试)的自动登录脚本

# 使用方法

克隆此项目到本地

```shell
# path 可选
git clone https://github.com/Himalian/login path/to/repo
```

运行 `uv run env.py`，这个脚本会生成一个`.env`文件，在里面填入校园网的账号密码（默认为学生证号与身份证后六位）。

运行登录脚本
```sh
uv run main.py
# 如果安装了just， 也可以用just运行
just login
```

# 原理

