# Шаблонизатор настроек ffmpeg

Используется для создания настроек ffmpeg в yaml формате

## Конфигурация

Конфигурация указывается либо в файле config.yaml в директории программы, через передачу аргумента Config(app_cfg: dict)

Конфиг должен содержать два поля:

`presets` - путь к директории с пресетами

`streams` - путь к директории с файлами стримов. Будет использоваться, если стримы создаются из них, а не через передачу параметра.

Так же можно запускать программу без конфигурационного файла, указав пути к presets и streams через аргументы -pp и -sp соотв.

Можно запускать без этих аргументов, если в директории запуска программы лежит presets/ и presets/streams/

## Шаблоны

Директория с шаблонами должна содержать директории:

- video - настройки видео
- audio - настройки аудио
- ffmpeg - настройки ffmpeg

### Видео шаблон

Ниже указан пример видео шаблона со всеми поддерживаемыми параметрами и флагами, в которые они преобразуются

```yaml

vframes: 20             # -vframes 20
fps: 20                 # -r 20
fps:                    # -r:0 20
  stream_number: 0
  value: 20
size: 1920x1080         # -s 1920x1068
codec: tratata          # -vcodec tratata
profile: baseline       # -profile:v baseline
level: 3.0              # -level 3.0
refs: 1                 # -refs 1
gop: 250                # -g 250
no_scenecut: true		# -no-scenecut 1
aspect: 16:9            # -aspect 16:9
aspect:                 # -aspect:0 16:9
  stream_number: 0
  value: 16x9
preset: high            # -preset hight
preset:                 # -preset:0 high
  stream_number: 0
  value: high
qscale: 1               # -qscale 1
qscale:                 # -qscale:0 1
  stream_number: 0
  value: 1
bf: 2                   # -bf 2
crf: 25                 # -crf 25
bitrate: 200k           # -b:v 200k
maxrate: 25             # -maxrate 25
bufsize: 45             # -bufsize 45M
rc: vbr_hq              # -rc:v (NVENC)
rc-lookahead: 32        # -rc-lookahead:v (int) (NVENC)
zerolatency: yes        # -tune zerolatency for all and -zerolatency for h264_hvenc and h265_nvenc
forced_idr: yes			# -forced_idr 1 (NVENC)
cbr: yes				# -cbr 1 (NVENC)
cq: 20                  # -cq 20 (NVENC)
spatial-aq: 1           # -spatial-aq:v Может быть равен только 1 (NVENC)
aq-strength: 12         # -aq-strength:v (int) (NVENC)
coder: 'cabac'          # -coder:v cabac (NVENC)
x264_params:            # -x264_opts level=31:ref=3:no-scenecut:vbv_maxrate=6096
  - level: 31           # Параметры внутри не проверяются на тип и передаются как есть
  - ref: 3
  - no-scenecut
  - vbv_maxrate: 6096
x265_params:            # -x265_opts level=31:ref=3:no-scenecut:vbv_maxrate=6096
  - level: 31           # Параметры внутри не проверяются на тип и передаются как есть
  - ref: 3
  - no-scenecut
  - vbv_maxrate: 6096
# Подробнее о фильтрах читайте в документации ffmpeg
filter_chains:          # -vf yadif=0:0:0,drawtext=text=hey,pullup;some_filter
  - name: chain1
    filters:
      - name: yadif
        values:
          - 0
          - 0
          - 0
      - name: drawtext
        values:
          - text: hey
      - pullup
  - name: chain2
    filters:
      - my_custom_filter
```

### Аудио шаблон

```yaml
bitrate: 128k           #  -b:a 128k - если указывается без 'k' или другой размерности - оберните число в кавычки
codec: 'libfdk_aac'     # -acodec libfdk_aac
sample_rate: 44100      # -ar 44100
ac: 1                   # -ac 1
```

### Шаблон стрима
Шаблон (настройки) можно передавать через аргумент preset - Stream(name, config, `preset`)

Пример:

```yaml
name : uvelirochka_navsegda # Используется как имя flashline, обязательное поле
ffmpeg_params:                  # -deinterlace -fflags +genpts  
  - deinterlace
  - fflags: "+genpts"
hwaccel: cuda                   # -hwaccel cuda 
vdecoder: h264_cuvid            # -c:v h264_cuvid

# -i http://input -map 0 -map 0:0 -map 0:v -map 0:p:1344 -map i:0x401 -i http://input2 
input:        
  - addr: "http://input1"
    maps:
      - 0
      - 0: 0
      - 0: v
      - 0: "p:1344"
      - i: "0x401"
  - "http://input2"

#-vcodec tratata -crf 25 -vframes 20 -r 20 -s 1920x1080 -b:v 200k -maxrate 25m -profile:v baseline -level 3.0 -refs 1 -g 250 -aspect 16:9 -preset high -qscale 1 -bf 2 -x264opts level=31:keyint=25:fps=25:ref=3:no-scenecut:vbv_maxrate=6096:vbv_bufsize=6096 -vf yadif=0:0:0,drawtext=text=hey,pullup;some_filter -acodec libfdk_aac -b:a 128k -ar 44100 -ac 1 -hls_param1 123 -hls_param2 456 -f tee "[select=\'v:0,a\':f=:onfail=ignore]local0|[select=\'v:0,a\':f=flv]rtmp://server0/app/instance"
# Требуется указать либо output_addr и format с соотв. адресом той ноды, в которую мы отправляем поток и форматом
# Или указать outputs, тогда будет создана tee. В каждом output этой tee нужно указать addr и опционально select, onfail и format
output:       # 
    - video_preset: 'fullhd_tests'
      audio_preset: 'aac_tests'
      format: 'flv'
      output_addr "http://flashline1
      outputs: 
        - select: "v:0,a"
          addr: local0
          onfail: ignore
        - select: "v:0,a"
          format: flv
          addr: rtmp://server0/app/instance
      hls_params:
        hls_param1: 123
        hls_param2: 456
```

