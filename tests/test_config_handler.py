from pathlib import Path
import tempfile

from config_handler import ConfigHandler


def test_config_summary_lists_current_runtime_details():
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "config.json"
        handler = ConfigHandler(str(config_path))

        summary = handler.get_config_summary()

        assert [line.strip() for line in summary.splitlines() if line.strip()] == [
            "配置摘要:",
            f"- 数据根目录: {handler.get_root_directory()}",
            f"- 日志目录: {handler.get_logs_directory()}",
            f"- 图片扫描目录: {handler.get_scan_root()}",
            f"- 服务器地址: {handler.get_host()}:{handler.get_port()}",
            f"- 支持的图片格式: {', '.join(handler.get_image_extensions())}",
            "- 默认文件夹: OK=OK, NOK=NOK",
        ]
