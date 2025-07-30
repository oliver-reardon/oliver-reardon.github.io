+++
title = "Distributing a Proxy Auto-Configuration (PAC) file using AWS services"
date = "2025-07-20T18:57:54-04:00"
#dateFormat = "2006-01-02" # This value can be configured for per-post date formatting
author = "Oliver Reardon"
authorTwitter = "" #do not include @
cover = ""
tags = ["", ""]
keywords = ["", ""]
description = ""
showFullContent = false
readingTime = true
hideComments = false
+++

A Proxy Auto-Configuration (PAC) file is a JavaScript file that tells browsers which proxy server to use for different websites automatically, rather than manually configuring proxy settings.

In order to distribute a public PAC file we need to satisfy some requirements:

- Modern browsers require PAC files to be served over HTTPS for security
- High availability, PAC file must be accessible 24/7 since browsers fetch it regularly
- Low latency, fast response times to avoid browser timeouts
- Correct MIME type, server must return `application/x-javascript-config` or `application/javascript` content type

For this use case, we were utilizing [Google Chrome Enterprise Premium Secure Gateway](https://cloud.google.com/beyondcorp-enterprise/docs/security-gateway-saas-apps) which required an accessible PAC file hosted on any cloud storage platform. The PAC file needed to be publicly accessible via HTTPS to automatically configure proxy settings for managed Chrome browsers/profiles across our organization.

The anatomy of a PAC file includes a `FindProxyForURL(url, host)` function that browsers call to determine how to route each web request. For each defined site the function checks if the requested URL matches a domain or sub-domain from the sites list. The function then returns the instruction string `HTTPS ingress.cloudproxy.app:443` to route the request via the proxy or `DIRECT` which instructs the browser to route the request via the internet.

```javascript
function FindProxyForURL(url, host) {
 const PROXY = "HTTPS ingress.cloudproxy.app:443";
 const sites = [
    "my-app-service.com",
    "another-app.com",
    "third-app.example.com",
    "internal-tool.company.com"
  ];

 for (const site of sites) {
   if (shExpMatch(url, 'https://' + site + '/*') || shExpMatch(url, '*.' + site + '/*')) {
     return PROXY;
   }
 }
return 'DIRECT';
}
```

For hosting the PAC file in globally accessible cloud storage I selected AWS S3 with CloudFront. S3 was selected due to it's simplicity and reliability and CloudFront was an obvious choice as it compliments S3 by adding CDN functionality including security (SSL/TLS, geographic restrictions, etc), cache control and custom MIME type headers. And as always, these resources were defined by [Terraform](https://www.hashicorp.com/en/products/terraform) with a [Scalr](https://docs.scalr.io/docs/introduction) remote backend.

To keep things secure, we ensure only CloudFront can access the S3 bucket using a bucket policy:

```hcl
# Secure S3 Bucket Policy (Only Allow CloudFront to Access S3)
resource "aws_s3_bucket_policy" "oac_policy" {
  bucket = aws_s3_bucket.my_bucket.id # Apply policy to the created bucket

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid    = "AllowCloudFrontAccess",
        Effect = "Allow",
        Principal = {
          Service = "cloudfront.amazonaws.com" # Allow only CloudFront to access
        },
        Action   = "s3:GetObject",
        Resource = "arn:aws:s3:::${aws_s3_bucket.my_bucket.id}/*", # All objects in the bucket
        Condition = {
          StringEquals = {
            "AWS:SourceArn" = aws_cloudfront_distribution.cdn.arn # Restrict access to this CloudFront distribution only
          }
        }
      }
    ]
  })
}
```
Sets `default_root_object` to `pac_config.js` so users can hit the root (`/`) and still get the PAC file.

```hcl
resource "aws_cloudfront_distribution" "cdn" {
  ...
  origin {
    domain_name              = aws_s3_bucket.my_bucket.bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.oac.id
  }

  default_root_object = "pac_config.js"
  ...
}
```
Following a successful Terraform apply the CDN URL is output for use by the Google Chrome policy [`ProxyPacUrl`](https://chromeenterprise.google/policies/?policy=ProxyPacUrl). There is also a newer Chrome policy [`ProxySettings`](https://chromeenterprise.google/policies/#ProxySettings) where you can also define a proxy URL with additional options.

```hcl
# Output the cdn URL
output "cdn_url" {
  value = "https://${aws_cloudfront_distribution.cdn.domain_name}"
}
```

For a complete example and Terraform code, see my repository: [proxy-pac-bucket on GitHub](https://github.com/oliver-reardon/proxy-pac-bucket)
