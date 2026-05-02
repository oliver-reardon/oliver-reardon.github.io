---
title: "Talent Profile"
description: "Builds scalable, secure infrastructure and endpoint platforms with a focus on macOS and cross-platform device management."
date: 2025-03-19T00:00:00Z
lastmod: 2026-03-31T00:00:00Z
type: "home"
layout: "single"
summary: "Builds scalable, secure infrastructure and endpoint platforms with a focus on macOS and cross-platform device management. Uses event-driven automation and infrastructure as code to enforce security controls, improve reliability, and reduce operational toil. Designs and delivers resilient, end-to-end solutions across infrastructure, identity, and device fleets. Experienced in observability, incident response, and automated remediation. Provides strong technical leadership, mentors engineers, and drives high standards while remaining hands-on."
draft: false
categories: ["Portfolio", "Resume", "Skills"]
showToc: true
showComments: false
--- 

Builds scalable, secure infrastructure and endpoint platforms with a focus on macOS and cross-platform device management. Uses event-driven automation and infrastructure as code to enforce security controls, improve reliability, and reduce operational toil. Designs and delivers resilient, end-to-end solutions across infrastructure, identity, and device fleets. Experienced in observability, incident response, and automated remediation. Provides strong technical leadership, mentors engineers, and drives high standards while remaining hands-on.

🔗 [LinkedIn](https://linkedin.com/in/oliver-reardon) | [GitHub](https://github.com/oliver-reardon)  

---

## 🔧 Skills & Technologies  

Docker · AWS · Ansible · macOS/Linux/Unix/Chrome @ scale · Azure · Terraform · Windows Server · CI/CD · Python ·
Git · API integrations · Jira · DevOps · Grafana · Splunk · Puppet · Scalr · MDM · PowerShell  
Infrastructure as Code (IaC) · AI · OSQuery · Serverless Framework · Bash/Zsh · AI · MCP

---

## 🏆 Certifications & Achievements  

- **[HashiCorp Certified: Terraform Associate](https://www.credly.com/badges/94f63417-b2fd-4da7-bd01-135fdb28b65b/public_url)**
- **Jamf 200/300**
- **Cisco Certified Network Associate (CCNA)**  
- **R/GA Cube Award Winner**  
- **Certified Kubernetes Administrator (CKA)** (In Progress)
- **Microsoft Certified: Azure Fundamentals**  
- **CompTIA Network+**  
- **Made 2,861 GitHub contributions** over the last year across various projects.
---

## 💼 Professional Experience  

### **Peloton Interactive, New York City, NY**  
- **Manager, Client Platform Engineering** *(June 2024 - Present)*  
- **Senior Client Platform Engineer (Team Lead)** *(Dec 2023 - June 2024)*  
- **Client Platform Engineer** *(Sept 2023 - Dec 2023)*  

Client Platform Engineering Manager operating as a hands-on senior individual contributor with deep expertise in diagnostic analysis and root cause investigation. Designs and delivers scalable, event-driven automation systems that improve reliability, performance, and operational efficiency, with a focus on reducing toil and creating reusable platform capabilities. Experienced in observability, incident management, and infrastructure as code, working end-to-end across systems to solve complex problems. Provides technical leadership, mentors engineers, and drives high standards while contributing directly to design and implementation.

#### **Key Responsibilities:**  
- Manage large-scale endpoint and fleet operations via MDM and configuration management.
- Build aggregated event pipelines and shared metrics for SIEM and security observability.
- Design and implement scalable automation to drive reliability, efficiency, and operational resilience.
- Lead production incident response and participate in on-call rotations.
- Integrate AI-driven automation and analytics to enhance operations, security, and decision-making.
- Lead Jira sprint planning, execution tracking, and delivery for operational engineering initiatives.
- Oversee Terraform + Scalr pipelines for infrastructure provisioning, cost visibility, and governance.
- Partner with SOC to validate findings and execute security remediation.
- Designed and enforced macOS endpoint security controls (disk encryption, OS hardening, device compliance policies), integrating signals into identity providers to support device trust and conditional access.
- Built automated security workflows using Terraform and CI/CD pipelines to provision, audit, and remediate endpoint configurations across the fleet, ensuring consistent compliance and reducing manual intervention.

---

### **R/GA (Interpublic Group of Companies), New York City, NY**  
- **Systems Administrator** *(January 2018 - August 2023)*  

Lead global IT team managing corporate endpoints across 19 sites.  
Engineered integrations with SaaS products while ensuring security and compliance.  

#### **Key Responsibilities:**  
- Engineered production-grade automation using Bash, PowerShell, and Python.
- Operated and scaled Linux microservices and node fleets using Puppet.
- Drove infrastructure reliability to consistently meet and exceed SLOs.
- Led cloud and on-prem infrastructure automation, scaling, and large-scale migrations.
- Implemented enterprise security controls aligned with CIS benchmarks and SOX requirements.
- Directed endpoint security strategy and enforcement via MDM.
- Authored and maintained high-value technical documentation and internal knowledge systems.
- Owned virtualized infrastructure availability and led incident response.
- Architected and maintained enterprise identity and trust systems (PKI, Kerberos, SSO, LDAP, 802.1X).

---

## 🎓 Education  

**Bachelor's Degree** – *Visual Communications, Time-Based Media*  
**University of Central England (UCE), Birmingham, England, UK** *(Sept 2002 - June 2005)*  

Focused on web-based tool design and online motion graphics.  

---

## 🔬 Recent Select Projects

> Certain repositories are limited to internal project work and can only be accessed within the current organization.

- **Designed and built a production-grade deployment of [FleetDM](https://fleetdm.com/)** on AWS using Terraform, enabling real-time endpoint visibility across 4000+ devices and reducing setup/operational overhead by 20% through reusable, automated infrastructure.
- [**Engineered offline-capable NDJSON log transport pipeline**](/posts/ndjson-event-buffered-transport-daemon/) for SAP Privileges (macOS) using Fluent Bit, `newsyslog`, and JWT-authenticated API forwarding.
- **Developed a device lifecycle automation framework** using Python and GitHub Actions to synchronize management tasks across Jamf Pro, Microsoft Intune, and Google Admin. The system automates critical API-driven operations, including remote device locking with PIN generation, deprovisioning, and record deletion. Real-time Slack and CMDB integrations ensure a centralized audit trail for all automated security actions.
- [**Log forwarding of osquery results**](https://oliver-reardon.github.io/posts/osquery-results-to-loki-with-kinesis-data-stream/) to Grafana Loki via AWS Kinesis Data Stream.
- [**Automated secure browser proxy configuration at scale using AWS S3 and CloudFront**](https://oliver-reardon.github.io/posts/distributing-a-proxy-auto-configuration-using-aws/)
- [**Restrict web app access using AWS WAF**](https://oliver-reardon.github.io/posts/protecting-fleetdm-with-aws-waf/) with CIDR ACL while keeping required API endpoints public.
- **Engineered an AWS Managed Grafana instance** using Terraform, integrated with Okta for federated authentication.
- [**Presented series data with Grafana & MySQL**](https://oliver-reardon.github.io/posts/application-usage-reports-using-grafana-and-mysql/) reducing software licensing costs and improving compliance.
- [**Developed Python CLI**](https://oliver-reardon.github.io/posts/set-computer-management-status-jamf-pro/) to automate inventory data manipulation after a vendor change.  
- **Built real-time security dashboards** with Splunk, integrating Jamf, Azure, Okta & OSQuery.  
- [**Containerized MDM**](https://oliver-reardon.github.io/posts/jamf-pro-docker-container/) server development environments using Docker.  
- **Implemented secure storage replication** for drive encryption keys with GnuPG & GitHub Actions.  
- **Integrated software repo into a CI/CD pipeline** with GitHub pull request approvals.  
- [**Created AWS Lambda function**](https://github.com/oliver-reardon/ms-graph-api-ea) to query Azure AD group membership efficiently.
- [**My Talent Profile**](https://github.com/oliver-reardon/oliver-reardon.github.io) produced using [hugo](https://gohugo.io/) and deployed using [GitHub Actions](https://github.com/oliver-reardon/oliver-reardon.github.io/blob/main/.github/workflows/deploy.yml) with cache validation.

---

