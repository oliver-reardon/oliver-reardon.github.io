---
title: Mass Modify Computer Management Status In Jamf Pro
date: 2023-10-01T12:56:06-04:00
author: Oliver Reardon
tags: 
  - jamf-pro
  - management-status
  - automation
  - cli
  - python
keywords: 
  - jamf pro
  - management status
  - mass action
  - automation
  - sms-cli
  - python
description: "Python CLI tool for mass modifying computer management status in Jamf Pro after the removal of mass action functionality in version 10.49. Using Advanced Computer Search integration and the Universal API for bulk operations."
showFullContent: false
readingTime: true
hideComments: false
---

> Jamf removed the ability to mass action modify the management status for computers in 10.49.

Modifying the management status of computers in Jamf Pro can still be useful for various asset management reasons. Expanding on the sentiment of [Der Flounder](https://derflounder.wordpress.com/2023/08/15/updating-management-status-in-jamf-pro-computer-inventory-records-on-jamf-pro-10-49-0-and-later/), I created a simple Python tool to set the management status of Jamf Pro computer object(s) via the universal api. Rather than using a pre-defined static list - the tool uses an Advanced Computer Search to iterate over.

Here's an example of `sms-cli` modifying the management status of 3 computers.

```text
$ python ./sms-cli.py --url=https://company.jamfcloud.com --username=user --managed --id=156 --password='pass'
Are you sure you want to change the management status for the device(s)? [y/N]: y
[SMS-CLI] Using search ID: Computers - Test Group
[SMS-CLI] Setting management status for host:host1 jssid:2988...
[SMS-CLI]...New management status = True
[SMS-CLI] Setting management status for host:host2 jssid:4277...
[SMS-CLI]...New management status = True
[SMS-CLI] Setting management status for host:host3 jssid:4117...
[SMS-CLI]...New management status = True
```

Source and setup KB can be found here - https://github.com/1sth1sth1ng0n/smscli#set-management-status-cli-sms-cli