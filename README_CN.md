# SleeperX

面向黑苹果用户的原生 macOS 菜单栏电源/睡眠管理工具。

* 低电量时自动睡眠。
* 接通电源时自动禁止睡眠。
* 随时禁用闲置睡眠或合盖睡眠（支持定时自动取消）。
* 合盖时锁屏。

事件驱动（IOKit / NSWorkspace 通知），PyObjC 原生实现，不再轮询。

> 需要 **macOS 10.12 (Sierra) 或更高版本**。

* 多语言支持：
  * 英文
  * 简体中文
  * 繁体中文
  * 日文
  * 韩文

## 特权助手

禁用合盖睡眠与修改睡眠（休眠）模式需要 root 权限，因为 `pmset -a disablesleep` /
`hibernatemode` 没有公开的 IOKit 等价接口。首次使用这些功能时，SleeperX 会安装一个经典
LaunchDaemon 助手。你只需**一次**输入管理员密码授权（不会存储任何密码）。助手仅执行固定、
白名单内的 `pmset` 命令，并通过 socket 权限与连入方 uid 校验加以限制。其余操作（整机睡眠、
息屏、禁用空闲睡眠）都无需 root。

## 下载

请查看 [Releases 页面](../../releases)。

## 首次打开（未签名应用）

SleeperX 以未签名方式分发。首次启动时 Gatekeeper 会拒绝打开。可以**右键点击应用 → 打开**，
或清除隔离属性：

```bash
xattr -dr com.apple.quarantine /Applications/SleeperX.app
```

## 如何构建

需要 Python 3.12 与 [uv](https://docs.astral.sh/uv/)。

```bash
uv sync --extra build
uv run python build.py                   # 产出 dist/SleeperX.app 与 dist/SleeperX-<version>.zip
```

## 提交 Bug

导出日志（偏好设置 → 高级选项），并附到 GitHub issue。导出的日志会屏蔽隐私数据。
