"""wsc-influx-send-csv

This CLI tool sends data to an influx database.

"""

import argparse
import logging
import os
import pathlib
import pprint
import yaml

import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import mergedeep

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

    #    parser.add_argument("-o", "--output", default=sys.stdout, type=argparse.FileType("w", encoding="utf-8"))

    parser.add_argument("--url", default=os.environ.get("INFLUX_URL", "https://us-east-1-1.aws.cloud2.influxdata.com"))
    parser.add_argument("--bucket", default=os.environ.get("INFLUX_BUCKET", "test"))
    parser.add_argument("--org", default=os.environ.get("INFLUX_ORG", "Bridgestone World Solar Challenge"))
    parser.add_argument("--token", default=os.environ.get("INFLUX_TOKEN", None))

    parser.add_argument("--debug", default=False, action="store_true")
    parser.add_argument("--quiet", default=False, action="store_true")
    parser.add_argument("--dryrun", default=False, action="store_true")

    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("/dev/stdin"))

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
    config = config_defaults
    if args.config:
        config = mergedeep.merge(config_defaults, yaml.safe_load(args.config))

    logger.info("Writing data to %s", pprint.pformat(config["influx"]))

    # ##################################
    # Set up the influxdb client object.
    # ##################################
    # influx = influxdb_client_3.InfluxDBClient3(
    #     token=args.token,
    #     host=config["influx"]["url"],
    #     org=config["influx"]["org"],
    #     database=config["influx"]["bucket"],
    # )

    client = influxdb_client.InfluxDBClient(url=config["influx"]["url"], org=config["influx"]["org"], token=args.token)

    write_api = client.write_api(write_options=SYNCHRONOUS)

    logger.debug("Created influx")
    if not args.dryrun:
        logger.debug("Got past dry run")
        with args.input.open("r", encoding="utf-8") as f:
            logger.debug("Writing points to influx")
            points = f.readlines()
            logger.debug("Writing %d points to influx", len(points))

            for point in points:
                logger.debug("Writing '%s'", point)
                write_api.write(bucket=config["influx"]["bucket"], record=point)


#            p = influxdb_client.Point("my_measurement").tag("location", "Prague").field("temperature", 25.3)
#            write_api.write(bucket=config["influx"]["bucket"],
#                            record=p)


if __name__ == "__main__":
    main()
