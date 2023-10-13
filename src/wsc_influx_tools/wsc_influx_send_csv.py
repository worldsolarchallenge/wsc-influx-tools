"""wsc-influx-send-csv

This CLI tool sends data to an influx database.

"""
from __future__ import print_function

import argparse
import logging
import os
import pprint
import sys

logger = logging.getLogger(__name__)


def main():
    """Main function."""

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config",
        type=argparse.FileType("r", encoding="utf-8"),
        default=None,
        help="YAML file to override config options",
    )

    parser.add_argument("-o", "--output", default=sys.stdout, type=argparse.FileType("w", encoding="utf-8"))
    parser.add_argument("--url", default=os.environ.get("INFLUX_URL", "us-east-1-1.aws.cloud2.influxdata.com"))
    parser.add_argument("--bucket", default=os.environ.get("INFLUX_BUCKET", "test"))
    parser.add_argument("--token", default=os.environ.get("INFLUX_TOKEN", None))

    parser.add_argument("--debug", default=False, action="store_true")
    parser.add_argument("--quiet", default=False, action="store_true")

    args = parser.parse_args()

    if args.debug:
        # Set the level of the root logger
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.quiet:
        # Set the level of the root logger
        logging.getLogger().setLevel(logging.ERROR)

    config_defaults = {
        "influx": {
            "bucket": args.bucket,
            "org": args.org,
            "url": args.url,
        }
    }
    config = mergedeep.merge(config_defaults, yaml.safe_load(args.config))

    logger.info("Getting data from %s", pprint.pformat(config["influx"]))


if __name__ == "__main__":
    main()
