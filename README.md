# ComfyUI

ComfyUI

## Change Log

### 2024-10-25

**增加启动项的配置**

**修复 httpx 依赖问题**

### 2024-09-05

**autocomplete插件配置更新**

安装时如果安装扩展，自动下载文件 `https://gist.githubusercontent.com/pythongosssss/1d3efa6050356a08cea975183088159a/raw/a18fb2f94f9156cf4476b0c24a09544d6c0baec6/danbooru-tags.txt` 至 `./custom_nodes/ComfyUI-Custom-Scripts/user/autocomplete.txt`

> 注意如果 autocomplete 失效，可以手动更换这个文件

**默认配置更改**

* 语言默认为中文
* 搜索框默认为 litegraph (legacy)

`./user/default/comfy.settings.json`：
{
    "AGL.Locale": "zh-CN",
    "Comfy.NodeSearchBoxImpl": "litegraph (legacy)"
}

**rgthree插件配置更新**

* 进度条默认在底部

`./custom_nodes/rgthree-comfy/rgthree_config.json`
```
{
  "features": {
    "group_header_fast_toggle": {
      "enabled": false
    },
    "import_individual_nodes": {
      "enabled": false
    },
    "menu_auto_nest": {
      "subdirs": false
    },
    "progress_bar": {
      "position": "bottom"
    }
  }
}
```



## Development

开发不要使用 apphub，建议直接用 Code 远程连接进行开发。

```bash
# 在当前目录下
apphub dev
```

## Publish

目前没有自动化发布功能，可将代码推送至 GitHub，然后通知管理员审核。应用更新需要在 GitHub Repo 中 Release 一个版本，第一个版本也需要 Release。