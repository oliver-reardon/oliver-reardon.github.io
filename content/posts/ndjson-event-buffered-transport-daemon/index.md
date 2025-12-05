---
title: "NDJSON Event Buffered Transport Daemon"
date: "2025-12-05T11:41:27-05:00"
author: "Oliver Reardon"
tags: []
keywords: []
description: ""
showFullContent: false
readingTime: true
hideComments: true
---

An offline-capable macOS logging framework that records events locally as plain-text logs and reliably forwards them to any remote API or generic text-based log store when connectivity is available. Built for enterprise deployment with reliable delivery and minimal operational overhead.

## Background

[SAP Privileges](https://github.com/SAP/macOS-enterprise-privileges) offers a [`RemoteLogging`](https://github.com/SAP/macOS-enterprise-privileges/wiki/Managing-Privileges#RemoteLogging) feature in addition to event logging through the [Apple Unified Logging](https://developer.apple.com/documentation/os/viewing-log-messages) system. 

At the time of writing, syslog and webhook are the only supported RemoteLogging options, and neither supports JWT-based authentication or the injection of non-standard HTTP headers. SAP Privileges does, however, support offline-capable logging and buffering through the [`QueueUnsentEvents`](https://github.com/SAP/macOS-enterprise-privileges/wiki/Managing-Privileges#QueueUnsentEvents) feature.

Apple's Unified Logging system is designed for local diagnostics, not reliable external log forwarding. Although log stream can provide real-time output, logs are stored in a proprietary binary format, require elevated access, and cannot be safely tailed as durable flat files. Retention is managed dynamically by the OS and may be aggressively truncated under disk pressure, making it unsuitable as a consistent, long-term source for forwarding logs to SIEMs, data lakes, or other platforms.

## Requirements

- Stream [SAP Privileges](https://github.com/SAP/macOS-enterprise-privileges) events to remote API
- Support JWT-based authentication
- Offline-capable logging and buffering
- Custom `x-source-id` header
- Structured JSON format

## Solution Overview

Because RemoteLogging and Apple's Unified Logging did not satisfy our requirements, we elected to introduce the lightweight endpoint log processor and forwarder [Fluent Bit](https://fluentbit.io/) in conjunction with [`newsyslog`](https://man.freebsd.org/cgi/man.cgi?newsyslog) for rotation of source logs. When devices are offline, events are logged locally in NDJSON format and periodically rolled over using newsyslog to prevent uncontrolled disk growth. When connectivity is restored, Fluent Bit automatically ships these events to the configured API endpoint with the required authentication and HTTP headers.

### Data Flow

```
SAP Privileges Event → privileges_local_logger.sh → Local NDJSON Log → newsyslog rotation → Fluent Bit → API Endpoint
```

### Key Capabilities

- **Offline-capable**: Events logged locally even without network connectivity
- **Structured logging**: NDJSON format for easy parsing and analysis
- **Automatic log rotation**: Built-in rotation to prevent disk space issues
- **Real-time shipping**: Events sent to API as soon as connectivity allows
- **Resilient delivery**: Built-in buffering and retry mechanisms

## Implementation

### Event Capture

To create dedicated log events we leveraged the SAP Privileges key [PostChangeExecutablePath](https://github.com/SAP/macOS-enterprise-privileges/wiki/Managing-Privileges#PostChangeExecutablePath) which executes a simple [bash script]() that records structured log entries locally with context captured from the provided arguments.

> When set, the PrivilegesAgent executes the given application or script and provides the current user's user name ($1) and its privileges (admin or user, $2) as launch arguments. If the application or script does not exist or is not executable, the launch operation fails silently.

### Event Schema

Each event is logged as a single line of JSON to `/usr/local/var/log/privileges/events.ndjson`:

```json
{
  "event_type": "privileges_change",      // Always "privileges_change" for normal events
  "username": "john.doe",                 // User account receiving/losing admin privileges
  "state": "admin",                       // Resulting privilege state ("admin" or "user")
  "action": "grant",                      // Action performed ("grant" or "revoke")
  "timestamp": "2025-11-06T15:30:45.123Z", // ISO 8601 timestamp with millisecond precision
  "serial": "C02X8XXXA1B2",              // Device serial number for device identification
  "hostname": "MacBook-Pro",              // Computer name for human-readable identification
  "hardware_uuid": "12345678-1234-1234-1234-123456789012", // Stable hardware identifier
  "parent_process": "Privileges",         // Process that triggered the event (usually "Privileges")
  "parent_pid": 1234,                     // Process ID of parent process
  "script_pid": 5678,                     // Process ID of logger script
  "script_version": "1.0"                 // Version of the logging script
}
```

### Log Rotation

The `newsyslog` service runs periodically and, based on this configuration, will rotate the log when it reaches 50 KB in size, retain up to 10 compressed archive files, and automatically recreate the log file if it does not exist.

```ini
# /etc/newsyslog.d/newsyslog-privileges.conf
/usr/local/var/log/privileges/events.ndjson root:staff 664 10 50 * JC
```

After newsyslog rotates the file, Fluent Bit continues tailing the newly created active log file and resumes reading from the correct position using its state database. Because all events from the previous file were already ingested before rotation and the rotated files are compressed and no longer written to, Fluent Bit does not need to read the archived logs and no events are lost.

### Event Forwarding

Once events reach Fluent Bit, it immediately parses each NDJSON record and attempts to forward it to the API endpoint. If the network is unavailable or the API cannot be reached, Fluent Bit automatically buffers the events in memory and then spills them to disk using its filesystem-backed storage configuration. These queued events are persisted across restarts, retried continuously, and flushed in order as soon as connectivity is restored, ensuring reliable, lossless delivery to the API.

## Components

| Component | Purpose | Location |
|-----------|---------|----------|
| `privileges_local_logger.sh` | Captures events in NDJSON format | `/usr/local/bin/` |
| `fluent-bit.conf` | Configures log shipping to API | `/usr/local/etc/fluent-bit/` |
| `parsers.conf` | JSON parsing rules for Fluent Bit | `/usr/local/etc/fluent-bit/` |
| `newsyslog-privileges.conf` | Log rotation configuration | `/etc/newsyslog.d/` |
| `com.privileges.fluent-bit.plist` | LaunchDaemon for Fluent Bit service | `/Library/LaunchDaemons/` |














