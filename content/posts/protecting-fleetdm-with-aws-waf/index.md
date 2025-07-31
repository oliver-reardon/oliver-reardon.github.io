---
title: Protecting FleetDM with AWS WAF
date: 2024-08-25T13:16:10-04:00
author: Oliver Reardon
tags: 
  - fleetdm
  - aws-waf
  - security
  - terraform
  - cloud
keywords: 
  - fleetdm
  - aws waf
  - web security
  - ip restriction
  - terraform
  - cloud
  - osquery
description: How to secure the FleetDM web console using AWS WAF, IP restrictions, and Terraform automation.
showFullContent: false
readingTime: true
hideComments: false
---

# Protecting FleetDM with AWS WAF

The [FleetDM](https://fleetdm.com/docs/get-started/why-fleet?gad_source=1) web console presents a valuable interface for managing endpoints — and like any administrative UI, it benefits from being accessible only to trusted networks. This configuration uses AWS WAF to restrict direct access based on source IP address, ensuring that only traffic from defined locations is allowed to reach the console.

The setup blocks all traffic by default and permits access only from trusted IP ranges, such as internal corporate networks and secure gateways used by managed browsers. While broader access policies are handled through a separate zero trust architecture, the WAF provides a clear network-layer boundary that limits exposure at the edge.

This post outlines the design, configuration, and purpose of this WAF setup.

For a complete example and Terraform code, see my repository: [fleet-aws-waf on GitHub](https://github.com/oliver-reardon/fleet-aws-waf)

## Why Use AWS WAF?

Even with authentication and device-based policies in place, it's often desirable to ensure that an application like FleetDM is not reachable at all from the open internet. AWS WAF serves this purpose by inspecting incoming requests at the edge and filtering based on predefined rules — before they reach the application load balancer.

In this implementation, WAF is used to:

1. Block all requests by default
   ```hcl
   ...
   default_action {
    block {}
   }
   ...
   ```
2. Allow traffic from trusted CIDRs or ranges
   ```hcl
   ...
   statement {
      // allow traffic from internal cidrs
      ip_set_reference_statement {
        arn = aws_wafv2_ip_set.main.arn
      }
    }
   ... 
   ```
3. Permit specific public API endpoints required for osquery agents
   ```hcl
   ...
   statement {
      // allow public traffic to only these endpoints
      // https://fleetdm.com/guides/what-api-endpoints-to-expose-to-the-public-internet
      or_statement {
        statement {
          byte_match_statement {
            positional_constraint = "CONTAINS"
            search_string         = "/api/v1/osquery"
            field_to_match {
              uri_path {}
            }
   ...
   ```
4. Log all request activity to CloudWatch for visibility
   ```hcl
   resource "aws_wafv2_web_acl_logging_configuration" "example" {
      log_destination_configs = [aws_cloudwatch_log_group.example.arn]
      resource_arn            = aws_wafv2_web_acl.main.arn
   }
   ```

## What the WAF Configuration Does

The [Terraform configuration](https://github.com/oliver-reardon/fleet-aws-waf) handles several key components:

1. **WAF Web ACL**
   - The core policy that defines which requests are allowed or blocked.
   - Default behavior is to block all requests unless explicitly allowed.

2. **Trusted IP Ranges**
   - Defined via an `aws_wafv2_ip_set`, which includes internal IP blocks and secure gateway egress addresses.
   - Used in a rule that allows access to the console from these sources.

3. **API Endpoint Exceptions**
   - Osquery agents require certain endpoints to be accessible from the public internet.
   - These include paths like `/api/osquery` and `/api/fleet/orbit`, which are explicitly permitted.

4. **CloudWatch Logging**
   - Logs are sent to a designated CloudWatch Log Group for auditing and monitoring.
   - An IAM resource policy grants the WAF service permission to write logs.

5. **Integration with ALB**
   - The Web ACL is attached to the Application Load Balancer that fronts FleetDM.
   - This ensures that all traffic passes through WAF filtering before reaching the app.

## Observability and Logging

Logs are written to CloudWatch for both allowed and blocked requests. This enables insight into:

- Unexpected sources attempting to access the console
- Frequency and volume of agent check-ins
- Behavior of internal users routing through trusted gateways

Each WAF rule has metrics enabled, making it possible to create dashboards or trigger alarms based on activity volume or anomalies.

```hcl
...
visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.waf_config.name}-allow-api-endpoints-metrics"
      sampled_requests_enabled   = true
    }
...
```

## Why Allow API Endpoints?

While the console should remain restricted, the backend must remain reachable by osquery agents that live on the public internet. To support this, a small number of API paths are allowed using byte match statements in WAF. These endpoints are:

- `/api/osquery`
- `/api/v1/osquery`
- `/api/fleet/orbit`
- `/api/fleet/device/ping`

These are safe to expose and are required for devices to check in and send results as defined [here](https://fleetdm.com/guides/what-api-endpoints-to-expose-to-the-public-internet#:~:text=and%20scripts%20functionality%2C-,/api/fleet/orbit/*,-and/api/fleet). There are additional endpoints that can be exposed depending on if MDM is being used or the `fleetctl` CLI needs access from outside the network.

## Terraform-Driven Setup

All resources — WAF rules, IP sets, log configuration, and associations — are managed via Terraform. This allows for reproducibility across environments, auditability through version control, and easier updates as network requirements evolve.

## Summary

This WAF configuration acts as a perimeter guard, limiting access to the FleetDM web console to trusted networks while ensuring essential functionality for osquery agents is preserved. It complements more advanced access control systems by reducing the attack surface and eliminating unnecessary exposure — all while being fully managed through code.