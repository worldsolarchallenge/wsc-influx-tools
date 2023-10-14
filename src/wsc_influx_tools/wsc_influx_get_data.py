# pylint: disable=duplicate-code
"""wsc-influx-get-data

This CLI tool downloads data from an influx database.

"""

import argparse
import logging
import os
import pprint
import sys
import yaml

import mergedeep
import influxdb_client_3

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

    parser.add_argument("--url", default=os.environ.get("INFLUX_URL", "https://us-east-1-1.aws.cloud2.influxdata.com"))
    parser.add_argument("--bucket", default=os.environ.get("INFLUX_BUCKET", "bwsc2023"))
    parser.add_argument("--org", default=os.environ.get("INFLUX_ORG", "Bridgestone World Solar Challenge"))
    parser.add_argument("--token", default=os.environ.get("INFLUX_TOKEN", None))

    parser.add_argument("--debug", default=False, action="store_true")
    parser.add_argument("--quiet", default=False, action="store_true")
    parser.add_argument("--dryrun", default=False, action="store_true")

    parser.add_argument("-o", "--output", type=argparse.FileType("w", encoding="utf-8"), default=sys.stdout)
    parser.add_argument("-f", "--format", choices=["markdown", "json", "csv"], default="markdown")

    group = parser.add_argument_group("Query Parameters")
    # Change to a custom query.
    group.add_argument("--query", type=str, default=None, help="Change to a InfluxQL query")

    # Parameters when using the default query.
    group.add_argument(
        "--window", default=86400, help="Amount of history to grab, in seconds, when using the default query."
    )
    group.add_argument("--measurement", default="telemetry", help="Influx measurement to query")

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
        },
        "query": {
            "query": args.query,
            "window": args.window,
            "measurement": args.measurement,
        },
    }
    config = config_defaults
    if args.config:
        config = mergedeep.merge(config_defaults, yaml.safe_load(args.config))

    logger.debug("Reading data from %s", pprint.pformat(config["influx"]))

    ####################################
    # Set up the influxdb client object.
    ####################################
    influx = influxdb_client_3.InfluxDBClient3(
        token=args.token,
        host=config["influx"]["url"].lstrip("https://"),
        org=config["influx"]["org"],
        database=config["influx"]["bucket"],
    )

    ####################################
    # Query the influx DB
    ####################################
    if args.query:
        # If we're using a custom query, that's the query.
        logger.info("Querying using custom query")
        query = args.query
    else:
        logger.info("Querying using default query with params: %s", config["query"])
        query = f"""\
SELECT
*
FROM {config["query"]["measurement"]}
WHERE time >= now() - {config["query"]["window"]}s
"""

    logger.debug("Using query:\n%s", query)

    table = influx.query(query=query, language="influxql")
    data_frame = table.to_pandas()

    logger.info("Found %d entries", len(data_frame))

    # Write the output in different formats
    if args.format == "markdown":
        args.output.write(str(data_frame))
    elif args.format == "json":
        args.output.write(data_frame.to_json(orient="records"))
    elif args.format == "csv":
        args.output.write(data_frame.to_csv())


if __name__ == "__main__":
    main()
