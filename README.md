# WSC Influx Tools

This project is in aid of the [Bridgestone World Solar Challenge](https://www.worldsolarchallenge.org/).

This is a python module which provides several CLI tools for interacting with the event's influx database.

## Installing wsc-influx-tools

wsc-influx-tools is a python package. THis has been tested on Linux and Mac (using Python 3.11).
Let us know if there are any issues. It can be installed using `pip`.
```bash
pip install wsc-influx-tools
```

The commands have useful help
```
$ wsc-influx-send-data --help
usage: wsc-influx-send-data [-h] [--config CONFIG] [--url URL] [--bucket BUCKET] [--org ORG]
                            [--token TOKEN] [--debug] [--quiet] [--dryrun] [--input INPUT]
```

## Writing data to influx

wsc-influx-tools provides a tool to send line format to an Influx V2 database from the CLI,
given a URL and a token.

Note that many of hte fields included below are overwritten (e.g. car name, team number, etc.)

Note that the precision used for the timestamp at the end of the line is nanoseconds (i.e. seconds * 1000000000)

```bash
wsc-influx-send-data --url https://telemetry.worldsolarchallenge.org/test/ingest/michigan --token TOKEN_GOES_HERE << EOF
telemetry,event=BWSC2023,class=Cruiser,team=World\ Solar\ Challenge\ Faculty,car=Solar\ Wombat\ 3,shortname=WSC\ Faculty longitude=135.26007,latitude=-30.24246,altitude=187.3,distance=432162,solarEnergy=20914846,batteryEnergy=52278368 1697461695000000000
EOF
```

## Reading data from Influx

For testing purposes, teams are provided with access to the InfluxDB V3 bucket to which their
data is written. The line format, written above, can be downloaded as CSV using the below command:

By default the wsc-influx-get-data command will query the last day's data from the given
measurement in the given bucket.

```bash
wsc-influx-get-data \
        --bucket test-teamdata \
        --measurement teamdata \
        --format=csv \
        --token TOKEN_GOES_HERE
```

The above results in a CSV output on the command line:
```bash
,iox::measurement,time,altitude,batteryEnergy,car,class,distance,escapedname,event,host,latitude,longitude,shortname,solarEnergy,team,teamnum
0,teamdata,2023-10-16 13:08:15,187.3,52278368.0,Astrum,Challenger,432162.0,michigan,BWSC2023,telegraf-deployment-michigan-6c497bc786-f4xdg,-30.24246,135.26007,Michigan,20914846.0,University of Michigan Solar Car Team,2
```
