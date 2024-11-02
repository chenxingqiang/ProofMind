# src/data/download_data.py

from .data_downloader import DataDownloader
import argparse
import logging
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description='Download mathematics theorem datasets')
    parser.add_argument('--data-dir', type=str, default='data',
                        help='Directory to store the downloaded data')
    parser.add_argument('--verify', action='store_true',
                        help='Verify data integrity after download')
    args = parser.parse_args()

    # 初始化下载器
    downloader = DataDownloader(data_dir=args.data_dir)

    # 下载数据
    logger.info("Starting data download...")
    if downloader.download_all():
        logger.info("Data download completed successfully")

        # 验证数据
        if args.verify:
            logger.info("Verifying data integrity...")
            if downloader.verify_data_integrity():
                logger.info("Data integrity verified successfully")
            else:
                logger.error("Data integrity check failed")
                return False
        return True
    else:
        logger.error("Data download failed")
        return False


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    success = main()
    sys.exit(0 if success else 1)
