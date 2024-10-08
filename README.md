# online_ocr
在线ocr，做一些文字识别以及衍生服务


## 一、基础镜像

使用<https://hub.docker.com/r/tesseractshadow/tesseract4re>作为基础镜像，镜像的操作系统为Ubuntu 18.04.3 LTS。里面自带了python3.6.9，但是没有安装pip，这里安装pip的时候报错没有足够的空间，输入`df -h`命令发现根目录空间不足。

```bash
root@b53ef79998ec:/home/work# df -h
Filesystem      Size  Used Avail Use% Mounted on
overlay          59G   57G     0 100% /
tmpfs            64M     0   64M   0% /dev
shm              64M     0   64M   0% /dev/shm
/dev/vda1        59G   57G     0 100% /etc/hosts
tmpfs           3.9G     0  3.9G   0% /sys/firmware
```

解决方案，`docker system prune -a` 来删除未使用的镜像、容器和网络，完成删除后根目录已经缩小了

```bash
root@b53ef79998ec:/# df -h
Filesystem      Size  Used Avail Use% Mounted on
overlay          59G  3.2G   53G   6% /
tmpfs            64M     0   64M   0% /dev
shm              64M     0   64M   0% /dev/shm
/dev/vda1        59G  3.2G   53G   6% /etc/hosts
tmpfs           3.9G     0  3.9G   0% /sys/firmware
```

## 二、软件安装

### 1. vim

直接安装即可，`apt install vim`

### 2. pip3

直接使用命令`apt install python3-pip`安装过程可能会有一些报错，例如

```bash
E: Failed to fetch http://security.ubuntu.com/ubuntu/pool/main/p/perl/libperl5.26_5.26.1-6ubuntu0.3_amd64.deb  404  Not Found [IP: 185.125.190.83 80]
E: Failed to fetch http://security.ubuntu.com/ubuntu/pool/main/p/perl/perl_5.26.1-6ubuntu0.3_amd64.deb  404  Not Found [IP: 185.125.190.83 80]
E: Failed to fetch http://security.ubuntu.com/ubuntu/pool/main/b/binutils/binutils-common_2.30-21ubuntu1~18.04.2_amd64.deb  404  Not Found [IP: 185.125.190.83 80]
E: Failed to fetch http://security.ubuntu.com/ubuntu/pool/main/b/binutils/libbinutils_2.30-21ubuntu1~18.04.2_amd64.deb  404  Not Found [IP: 185.125.190.83 80]
```

将老的apt源备份
```bash
mv /etc/apt/sources.list /etc/apt/sources.list.bak
```
 换成国内的apt源
```bash
deb http://mirrors.aliyun.com/ubuntu/ focal main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ focal-security main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ focal-updates main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ focal-backports main restricted universe multiverse
```
更新源
```bash
apt-get update
```
再来重新安装即可

## 三、镜像制作

安装好vim和pip3之后，可以将镜像重新制作一下，然后再上传到docker hub
```bash
docker commit b53ef79998ec shuhaojie/online_ocr:v1
docker push shuhaojie/online_ocr:v1
```

## 四、Dockerfile

Dockerfile不复杂
```Dockerfile
FROM shuhaojie/online_ocr:v1

COPY start.py .
COPY templates/ ./templates
COPY static/ ./static
COPY data/ ./data

EXPOSE 5001

ENTRYPOINT ["python", "start.py"]
```

制作镜像的时候碰到如下问题

(1) 报错1:

```bash
ERROR: open /Users/haojie/.docker/buildx/activity/desktop-linux: permission denied
```

解决: 加上sudo即可, sudo docker build -t shuhaojie/online_ocr:v2 .

(2) 报错2:

```bash
ERROR: failed to solve: shuhaojie/online_ocr:v1: error getting credentials - err: exit status 1, out: ``
```

解决: 参考<https://forums.docker.com/t/error-failed-to-solve-error-getting-credentials-err-exit-status-1-out/136124/6?u=shuhaojie>

(3) 报错3:

```bash
ERROR: failed to solve: DeadlineExceeded: DeadlineExceeded: DeadlineExceeded: shuhaojie/online_ocr:v1: failed to authorize: DeadlineExceeded: failed to fetch oauth token: Post "https://auth.docker.io/token": dial tcp 108.160.165.141:443: i/o timeout
```

解决: 参考https://blog.csdn.net/fwzzzzz/article/details/142333600

## 五、docker-compose

启动的时候，需要对内部端口5001做映射，在浏览器中输入<http://127.0.0.1:5001/> 即可访问