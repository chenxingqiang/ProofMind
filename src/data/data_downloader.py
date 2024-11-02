# src/data/data_downloader.py

import os
import requests
import json
import zipfile
import tarfile
import logging
from pathlib import Path
from tqdm import tqdm
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataDownloader:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 数据源配置
        self.data_config = {
            "algebra": {
                "url": "https://raw.githubusercontent.com/deepmind/mathematics_dataset/master/mathematics_dataset/modules/algebra.py",
                "filename": "algebra_theorems.json"
            },
            "topology": {
                "url": "https://raw.githubusercontent.com/deepmind/mathematics_dataset/master/mathematics_dataset/modules/topology.py",
                "filename": "topology_theorems.json"
            },
            "number_theory": {
                "url": "https://raw.githubusercontent.com/deepmind/mathematics_dataset/master/mathematics_dataset/modules/numbers.py",
                "filename": "number_theory_theorems.json"
            }
        }

    def download_file(self, url: str, filename: str) -> bool:
        """下载文件并显示进度条"""
        file_path = self.data_dir / filename

        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))

            with open(file_path, 'wb') as f, tqdm(
                total=total_size,
                unit='iB',
                unit_scale=True,
                desc=f"Downloading {filename}"
            ) as pbar:
                for data in response.iter_content(chunk_size=8192):
                    size = f.write(data)
                    pbar.update(size)

            return True

        except Exception as e:
            logger.error(f"Error downloading {url}: {str(e)}")
            return False

    def process_python_to_json(self, python_file: Path, json_file: Path):
        """将Python文件中的数据转换为JSON格式"""
        try:
            with open(python_file, 'r') as f:
                content = f.read()

            # 提取数据（这里需要根据实际Python文件的格式进行调整）
            # 这里只是一个示例
            data = {
                "theorems": [
                    {
                        "statement": "Example theorem",
                        "proof": "Example proof"
                    }
                ]
            }

            with open(json_file, 'w') as f:
                json.dump(data, f, indent=2)

            return True

        except Exception as e:
            logger.error(f"Error processing file {python_file}: {str(e)}")
            return False

    def download_all(self) -> bool:
        """下载所有数据集"""
        success = True
        for domain, config in self.data_config.items():
            logger.info(f"Processing {domain} theorems...")

            # 创建领域目录
            domain_dir = self.data_dir / domain
            domain_dir.mkdir(exist_ok=True)

            # 下载Python文件
            python_file = self.data_dir / f"{domain}_raw.py"
            if not self.download_file(config['url'], python_file.name):
                success = False
                continue

            # 转换为JSON
            json_file = domain_dir / config['filename']
            if not self.process_python_to_json(python_file, json_file):
                success = False
                continue

            # 删除原始Python文件
            python_file.unlink()

            logger.info(f"Successfully processed {domain} theorems")

        return success

    def verify_data_integrity(self) -> bool:
        """验证下载的数据完整性"""
        success = True
        for domain, config in self.data_config.items():
            json_file = self.data_dir / domain / config['filename']

            if not json_file.exists():
                logger.error(f"Missing file: {json_file}")
                success = False
                continue

            try:
                with open(json_file) as f:
                    data = json.load(f)
                    if not data.get('theorems'):
                        logger.error(f"No theorems found in {json_file}")
                        success = False
                        continue

                logger.info(f"Verified {json_file}")

            except Exception as e:
                logger.error(f"Error verifying {json_file}: {str(e)}")
                success = False

        return success
