import os
from pathlib import Path
from apphub.helper import wait_for_port

import gradio as gr

from apphub.app import App, AppOption


class Comfyui(App):

    @property
    def key(self):
        """key 是应用的唯一标识，用于在数据库中查找应用，所以这个值应该是唯一的"""
        return "comfyui"

    @property
    def port(self):
        """应用的端口号"""
        return 23810

    @property
    def op_port(self):
        """应用管理端口号"""
        return 38965

    @property
    def name(self):
        """应用名称"""
        return "ComfyUI"

    class ComfyuiOption(AppOption):
        """App 都可以在 Class 内部创建一个类，并且该类需要继承自 AppOption，
        这样这个类则表示该 App 的配置项，配置项根据 App 的不同则不同，比如对于一个
        TensorBoard 的 App，可能需要配置的是 TensorBoard 的 event logs 的路径。

        父类默认提供了两个配置项：

        install_location 安装路径
        version 安装版本
        """
        pass

    cfg: ComfyuiOption

    def render_installation_page(self) -> "gr.Blocks":
        """这个方法定义了如何渲染安装页面，这个页面会展示给用户，让用户安装应用

        页面使用 Gradio 来渲染，所以这里只需要返回一个 Gradio 的 Blocks 对象即可
        """

        with gr.Blocks() as demo:
            # 首选可以渲染一些 Markdown 文本，用于介绍应用
            gr.Markdown(
                """# 安装 ComfyUI

若选择安装在云盘，并且安装所有插件，大约需要 7GB 空间，整个安装过程大概持续 10 分钟。

如果安装在云盘，退还实例后下次无需重复安装。

我们准备了大概 200GB 的各种模型文件，可以在启动应用的时候选择挂载，挂载模型文件并不会占用云盘空间。
"""
            )
            # 应用安装的位置，支持两个选项，云盘或数据盘
            #
            # 如果用户选择了 ~/work/apps/${key}，则 self.in_work 会返回 true，表示
            # 用户希望把应用存放在云盘中以方便下次使用实例时不需要重复安装，这样应用本身
            # 最好也将产生的数据放置在云盘中，以便用户下次使用时可以继续使用
            #
            # NOTE：所有应用都需要先渲染这个组建，这个组建会让用户选择 App 将被安装的位置
            # 选项也是固定的，只有两个：~/work/apps/${key} 和 ~/apps/${key}
            # 应用应该将所有应用本身的文件放置在这两个目录内，用户在使用应用所产生的其他数据
            # 则不受限制，可以放置在这个目录内，也可以放在其他地方。
            #
            # NOTE：就算没有任何文件需要安装，也需要渲染这个组建
            #
            # NOTE：应用开发者在开发时应该先测试将应用安装在云盘中，因为云盘的文件系统所支持
            # 的操作并不完备，对于大多数应用来说，可能都是支持云盘安装的，但是也有一些应用
            # 需要用到很高级的文件系统操作（例如一部分文件锁），allow_work 默认为 False
            # 如果开发者发现安装在云盘没有问题，则这里可以将 allow_work 设置为 True
            install_location = self.render_install_location(
                allow_work=True,
                default="work",
            )

            install_extension = gr.Dropdown(
                label="安装常用插件",
                info="安装常用的模型或插件",
                allow_custom_value=False,
                value="v1",
                choices=[
                    ("纯净版（仅 comfyui 本身）", "bare"),
                    ("常用插件", "v1"),
                ]
            )

            # 这里使用一个帮助方法来渲染提交按钮，注意 inputs 的参数
            self.render_installation_button(
                inputs=[install_location, install_extension]
            )
            # 渲染日志组件，将安装过程展示给用户
            self.render_log()
        return demo

    def installation(self, install_location, install_extension):
        """该函数会在用户点击安装按钮后被触发（前提是用了 self.render_isntallation_button，开
        发者也可以完全自己发挥），用于执行安装的逻辑，比如下载源码、安装依赖等，其参数和
        self.render_installation_button 中的 inputs 保持一致。
        """
        # 调用该方法后，可以以 self.cfg.xxx 来访问所有配置项
        # NOTE：installation 的参数和这里都不要用 *args 的方式传参
        super().installation(install_location)

        if self.in_work:
            self.execute_command(f"conda create -y --prefix /home/featurize/work/app/{self.key}/env python=3.11")
    
        with self.conda_activate(self.env_name):
            self.execute_command("git clone https://github.com/comfyanonymous/ComfyUI")
            self.execute_command("pip install -r requirements.txt", "ComfyUI")
            self.execute_command("pip install facexlib opencv-python timm accelerate "
                                 "deepdiff matplotlib google diffusers omegaconf supervision "
                                 "numexpr blend-modes bitsandbytes vtracer rembg openai "
                                 "surrealist lpips numba einops")
        
        if install_extension == "v1":
            pass
            # self.execute_command(f"featurize dataset extract bf2877db-408d-4a3f-856d-3d718c027b27 ./ComfyUI/custom_nodes/")
            # self.execute_command(f"mv ./ComfyUI/custom_nodes/comfyui-extensions-collection/* ./ComfyUI/custom_nodes/")
            # self.execute_command(f"rm -rf ./ComfyUI/custom_nodes/comfyui-extensions-collection")

        # 通常在安装过程中都会运行大量的 bash 命令，强烈建议使用 `self.execute_command` 来运行
        # 更稳妥的办法这里可能最好先创建一个虚拟环境，或者可以做得更好，把是否创建虚拟环境加到配置项
        # 中，让用户自己来选择使用已有的虚拟环境还是创建新的虚拟环境。
        # NOTE：所有命令，或是其他的根路径相关的参数等都建议使用绝对路径
        # TODO：在这里写安装逻辑，一般都会调用 execute_command 来执行
        # self.execute_command("{command to be executed}")

        # 因为起应用还会根据安装的扩展来安装其他的包，所以这里直接启动应用，等端口通了之后，Kill 应用，再通知前端启动成功
        # self.execute_command(f"python main.py --listen 127.0.0.1 --port {self.port}", "ComfyUI", daemon=True)
        # wait_for_port(self.port)
        # self.close()

        # 调用 app_installed，标准流程，该函数会通知前端安装已经完成，切换到应用的页面
        self.app_installed()

    @property
    def env_name(self):
        return "base" if not self.in_work else f"/home/featurize/work/app/{self.key}/env"

    def render_start_page(self):
        with gr.Blocks() as demo:
            gr.Markdown(
                f"""# {self.name} 尚未启动

请点击下方按钮启动 {self.name}。

当前 ComfyUI 被安装在 {os.path.join(self.cfg.install_location, "ComfyUI")} 中，你可以使用下方的「文件」应用访问这个目录手动管理文件。

如果使用遇到问题，请及时关注公众号后向我们反馈：https://docs.featurize.cn 中可扫码联系我们。
"""
            )
            mount_models = gr.Dropdown(
                label="挂载模型（不占用云端硬盘空间）",
                info="我们会定期更新常用的挂载模型内容，如果你有其他建议，也欢迎向我们反馈。",
                value="v1",
                choices=[
                    ("挂载常用模型", "v1"),
                    ("不挂载", "bare"),
                ]
            )
            button = self.render_start_button(inputs=[mount_models])
            self.render_log()
        return demo

    def start(self, mount_models):
        """安装完成后，应用并不会立即开始运行，而是调用这个 start 函数。"""

        # 跟安装逻辑一样，start 里一般来说也是使用 execute_command 来启用应用
        # 这里有一点不同，如果运行的某一个命令是一个「服务」，也就是他不会退出，
        # 则在调用 execute_command 时候需要传入 daemon=True，否则命令会
        # 卡住不动，self.execute_command("uvicorn app:main", daemon=True)
        # TODO: 写应用启动的逻辑
        if mount_models != "bare":
            Path("/home/featurize/.public/comfyui").mkdir(parents=True, exist_ok=True)
            self.execute_command(
                f"sudo mount -t nfs -o ro,acregmin=600,acregmax=3600,rsize=1048576,wsize=1048576,noatime,tcp 172.16.0.227:/featurize-public/comfyui/assets_{mount_models} /home/featurize/.public/comfyui"
            )
            model_path = "/home/featurize/.public/comfyui/models/"
            for model_type in os.listdir(model_path):
                for file in os.listdir(f"{model_path}{model_type}"):
                    target = os.path.join(self.cfg.install_location, "ComfyUI/models", model_type, file)
                    if not os.path.exists(target):
                        src = os.path.join(model_path, model_type, file)
                        Path(target).parent.mkdir(parents=True, exist_ok=True)
                        self.logger.info(f"link {src} to {target}")
                        if os.path.isdir(src):
                            os.symlink(src, target, target_is_directory=True)
                        else:
                            os.symlink(src, target)

        with self.conda_activate(self.env_name):
            self.execute_command(f"python main.py --listen 0.0.0.0 --port {self.port}", "ComfyUI", daemon=True)

        # 调用 app_started，标准流程，该函数会通知前端应用已经开始运行
        self.app_started()

    def close(self):
        """关闭应用的逻辑"""
        # 如果服务启动使用了 shell=True，则系统会自动记录 pid，close 的逻辑就是
        # kill group pid，因此对于很多应用来说不需要自己写这个函数，但也有很多例外
        # 例如如果应用是 docker 起的，则需要在这里手动 docker stop container

        # TODO: 写关闭应用的逻辑
        super().close()

    def uninstall(self):
        """卸载应用会调用该方法"""

        # 主要是清理用户云盘或机器磁盘上的文件，至于安装的包，或是用户在使用应用
        # 产生的其他文件，则可选择性处理。一般来说直接用父类的逻辑即可。
        # 父类会先调用 close，然后再删除 install_directory

        # TODO: 卸载的逻辑
        super().uninstall()


def main():
    return Comfyui()
