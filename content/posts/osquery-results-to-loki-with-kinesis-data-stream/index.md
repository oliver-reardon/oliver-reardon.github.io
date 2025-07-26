+++
title = "OSQuery Results to Loki with Kinesis Data Stream"
date = "2023-10-19T11:35:25-04:00"
#dateFormat = "2006-01-02" # This value can be configured for per-post date formatting
author = "Oliver Reardon"
authorTwitter = "" #do not include @
cover = ""
tags = ["osquery", "loki", "kinesis", "fleetdm", "lambda"]
keywords = ["osquery", "grafana", "loki", "kinesis data stream", "fleetdm", "lambda transformation", "log aggregation", "macOS telemetry"]
description = "A practical guide on forwarding macOS application usage data from osquery to Grafana Loki using AWS Kinesis and Lambda for enrichment."
showFullContent = false
readingTime = true
hideComments = false
+++

Forwarding [osquery](https://www.osquery.io/) results to a log aggregator or SIEM requires enriching the JSON data payload to match the destination’s expected structure. [AWS Kinesis Data Streams](https://aws.amazon.com/kinesis/data-streams/) ingests data in real time, applies transformations using Lambda, and then delivers the enriched JSON payload to the downstream destination — in this case, [Grafana Loki](https://grafana.com/oss/loki/).

The osquery manager ([FleetDM](https://fleetdm.com/docs/get-started/why-fleet?gad_source=1)) runs as a container in AWS with the results plugin enabled by setting the environment variable `FLEET_OSQUERY_RESULT_LOG_PLUGIN` to `kinesis`. Additionally, defining `FLEET_KINESIS_RESULT_STREAM` with the name of the Kinesis Data Stream, which, in the Terraform setup, is referenced as `aws_kinesis_stream.data_stream.name`.

This macOS specific query focuses on 3 applications and logs the respective applications characteristics as query results:

```mysql
SELECT 
  bundle_executable, 
  bundle_identifier, 
  bundle_name, 
  bundle_short_version, 
  bundle_version, 
  display_name, 
  name, 
  path, 
  strftime(
    '%Y-%m-%d %H:%M:%S', last_opened_time, 
    'unixepoch'
  ) as last_opened_time 
FROM 
  apps 
WHERE 
  last_opened_time != '-1.0' 
  and bundle_name IN ('Chrome', 'Slack', 'zoom.us');
```
Once the above query automation runs, the data is forwarded to the downstream log destination (AWS Kinesis Data Stream).

## Pre-enriched Data:

```json
{
  "snapshot": [
      {
          "bundle_executable": "Google Chrome",
          "bundle_identifier": "com.google.Chrome",
          "bundle_name": "Chrome",
          "bundle_short_version": "134.0.6998.89",
          "bundle_version": "6998.89",
          "display_name": "Google Chrome",
          "last_opened_time": "2024-07-08 14:27:41",
          "name": "Google Chrome.app",
          "path": "/Applications/Google Chrome.app"
      },
      {
          "bundle_executable": "Slack",
          "bundle_identifier": "com.tinyspeck.slackmacgap",
          "bundle_name": "Slack",
          "bundle_short_version": "4.40.128",
          "bundle_version": "440000128",
          "display_name": "Slack",
          "last_opened_time": "2025-03-12 16:12:21",
          "name": "Slack.app",
          "path": "/Applications/Slack.app"
      },
      {
          "bundle_executable": "zoom.us",
          "bundle_identifier": "us.zoom.xos",
          "bundle_name": "zoom.us",
          "bundle_short_version": "5.16.10 (25689)",
          "bundle_version": "5.16.10.25689",
          "display_name": "",
          "last_opened_time": "2024-02-07 17:30:20",
          "name": "zoom.us.app",
          "path": "/Applications/zoom.us.app"
      }
  ],
  "action": "snapshot",
  "name": "pack/Global/App Usage",
  "hostIdentifier": "E0804EAC-481F-5BF3-AA00-8AA4EDE72395",
  "calendarTime": "Mon Mar 17 13:39:51 2025 UTC",
  "unixTime": 1742218791,
  "epoch": 0,
  "counter": 0,
  "numerics": false,
  "decorations": {
      "host_uuid": "E0804EAC-481F-5BF3-AA00-8AA4EDE72395",
      "hostname": "macos-host"
  }
}
```

To enrich this JSON data structure so Loki can ingest it we need to use a Lambda transformation attached to the Kinesis Data Stream. When the Kinesis Data Stream receives incoming data it will buffer the events to the Lambda function which extracts the event records, decodes them from base64 and appends additional meta data that Loki can use.

## Post-enriched Data:

```json
{
  "streams": [
      {
          "stream": {
              "host": "macos-host",
              "host_uuid": "E0804EAC-481F-5BF3-AA00-8AA4EDE72395",
              "bundle_executable": "Google Chrome",
              "bundle_identifier": "com.google.Chrome",
              "bundle_name": "Chrome",
              "bundle_version": "6998.89",
              "path": "/Applications/Google Chrome.app",
              "service_name": "fleet-data-stream"
          },
          "values": [
              [
                  "1742218797748051968",
                  "{\"host\": \"macos-host\", \"host_uuid\": \"E0804EAC-481F-5BF3-AA00-8AA4EDE72395\", \"bundle_executable\": \"Google Chrome\", \"bundle_identifier\": \"com.google.Chrome\", \"bundle_name\": \"Chrome\", \"bundle_short_version\": \"134.0.6998.89\", \"bundle_version\": \"6998.89\", \"display_name\": \"Google Chrome\", \"name\": \"Google Chrome.app\", \"path\": \"/Applications/Google Chrome.app\", \"last_opened_time\": \"2024-07-08 14:27:41\"}"
              ]
          ]
      },
      {
          "stream": {
              "host": "macos-host",
              "host_uuid": "E0804EAC-481F-5BF3-AA00-8AA4EDE72395",
              "bundle_executable": "Slack",
              "bundle_identifier": "com.tinyspeck.slackmacgap",
              "bundle_name": "Slack",
              "bundle_version": "440000128",
              "path": "/Applications/Slack.app",
              "service_name": "fleet-data-stream"
          },
          "values": [
              [
                  "1742218797748051968",
                  "{\"host\": \"macos-host\", \"host_uuid\": \"E0804EAC-481F-5BF3-AA00-8AA4EDE72395\", \"bundle_executable\": \"Slack\", \"bundle_identifier\": \"com.tinyspeck.slackmacgap\", \"bundle_name\": \"Slack\", \"bundle_short_version\": \"4.40.128\", \"bundle_version\": \"440000128\", \"display_name\": \"Slack\", \"name\": \"Slack.app\", \"path\": \"/Applications/Slack.app\", \"last_opened_time\": \"2025-03-12 16:12:21\"}"
              ]
          ]
      },
      {
          "stream": {
              "host": "macos-host",
              "host_uuid": "E0804EAC-481F-5BF3-AA00-8AA4EDE72395",
              "bundle_executable": "zoom.us",
              "bundle_identifier": "us.zoom.xos",
              "bundle_name": "zoom.us",
              "bundle_version": "5.16.10.25689",
              "path": "/Applications/zoom.us.app",
              "service_name": "fleet-data-stream"
          },
          "values": [
              [
                  "1742218797748051968",
                  "{\"host\": \"macos-host\", \"host_uuid\": \"E0804EAC-481F-5BF3-AA00-8AA4EDE72395\", \"bundle_executable\": \"zoom.us\", \"bundle_identifier\": \"us.zoom.xos\", \"bundle_name\": \"zoom.us\", \"bundle_short_version\": \"5.16.10 (25689)\", \"bundle_version\": \"5.16.10.25689\", \"display_name\": \"\", \"name\": \"zoom.us.app\", \"path\": \"/Applications/zoom.us.app\", \"last_opened_time\": \"2024-02-07 17:30:20\"}"
              ]
          ]
      }
  ]
}
```

Loki requires data in this structured format because it follows the push-based JSON log entry model, where logs are grouped into streams identified by key-value pairs (labels) and contain timestamped values (log entries).

The `stream` object contains key-value pairs like `host`, `host_uuid`, and `bundle_identifier`, which act as labels in Loki. Labels allow efficient indexing and filtering when querying logs using Loki’s query language LogQL.

The `values` array holds log entries as a list of timestamp-value pairs. Each timestamp (`"1742218797748051968"`, which is in nanoseconds) ensures logs are stored in chronological order for accurate time-based queries.

This approach reduces storage overhead by indexing only labels, keeping log queries fast and efficient.

Using the Grafana Explore feature with this LogQL query we can extract specific application data:

```yaml
{bundle_identifier="us.zoom.xos",service_name="fleet-data-stream"}
```

{{< figure src="loki-explore.webp" alt="Grafana explore results" caption="Grafana explore results" >}}

The `Fields` meta data area describes the stream object labels we provided in the Lambda transformation and the timestamped data is a log event with nested values we could use to build time-based visualizations in LogQL.

```yaml
count(count_over_time({bundle_identifier="com.google.Chrome"}[1d])) by (bundle_version)
```
{{< figure src="bundle-version-over-time.webp" alt="Results Over Time" caption="Results Over Time" >}}