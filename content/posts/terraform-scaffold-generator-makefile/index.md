+++
title = "Terraform Scaffold Generator"
date = "2024-11-27T19:33:15-04:00"
#dateFormat = "2006-01-02" # This value can be configured for per-post date formatting
author = "Oliver Reardon"
authorTwitter = "" #do not include @
cover = ""
tags = ["terraform", "makefile", "automation", "infrastructure"]
keywords = ["terraform", "makefile", "project generator", "infrastructure as code", "automation", "scaffolding"]
description = "A lightweight Makefile-based tool for generating consistent Terraform project structures with organizational standards and best practices."
showFullContent = false
readingTime = true
hideComments = false
+++

I was looking for a repeatable, consistent way to generate Terraform project structures that aligned with internal organizational standards. The idea was to make it easy to spin up new infrastructure projects without reinventing the wheel each time.

The goal of this tool was to create a lightweight, opinionated generator that scaffolds new Terraform projects in seconds. It offers a uniform starting point with sensible defaults, a clean structure, and space for project-specific customization. By defining a clear and consistent baseline, the generator reduces onboarding time, prevents common mistakes, and makes it easier to maintain a high standard across infrastructure codebases. It’s a simple way to bring structure and consistency to Terraform work without getting in the way.

**Project repository:** [github.com/oliver-reardon/terraform-scaffold-generator](https://github.com/oliver-reardon/terraform-scaffold-generator)

Using a Makefile made it easy to create consistent, repeatable Terraform project scaffolds. The `new` target handles validation, copies the template, and replaces placeholders automatically. The `help` target displays a user-friendly list of available Makefile commands along with brief descriptions. It parses comments marked with `##` in the Makefile and formats them into a clear summary.

```makefile
.PHONY: help new

NAME ?= my-project
n ?= $(NAME)
OUTPUT ?= .
o ?= $(OUTPUT)

help: ## Show this help
	@echo "Terraform Scaffold Generator"
	@echo ""
	@echo "Usage: make new n=project-name [o=output-dir]"
	@echo "Defaults: n=my-project, o=current-directory"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "}; /^[a-zA-Z0-9_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

new: ## Create new project from template
	@if [ -z "$(n)" ]; then echo "Please specify NAME=name or n=name"; exit 1; fi
	@if [ ! -d "template" ]; then echo "Missing template/ directory"; exit 1; fi
	@mkdir -p "$(o)"
	@if [ -d "$(o)/$(n)" ]; then echo "Directory $(o)/$(n) already exists"; exit 1; fi
	@echo "Creating terraform project: $(n) in $(o)"
	@cp -r template "$(o)/$(n)"
	@find "$(o)/$(n)" -type f \( -name '*.tfvars' -o -name '.header.md' \) -exec sed -i.bak 's/my-project/$(n)/g' {} +
	@find "$(o)/$(n)" -name '*.bak' -delete
	@echo "Done! Run: cd $(o)/$(n)"
```

## Creating a New Project

To create a new Terraform project from the template, run:

```bash
make new n=my-project-name
```

You can also specify a custom output directory:

```bash
make new n=my-project-name o=./projects
```

This creates the boilerplate scaffold structure:

```bash
my-project-name/
├── terraform/
│   ├── locals.tf       # Local values and naming conventions
│   ├── main.tf         # Main Terraform resources
│   ├── outputs.tf      # Output definitions
│   ├── providers.tf    # Provider configurations
│   ├── variables.tf    # Variable definitions
│   └── versions.tf     # Version constraints
├── environments/
│   ├── dev.tfvars      # Development environment variables
│   ├── staging.tfvars  # Staging environment variables
│   └── prod.tfvars     # Production environment variables
├── .gitignore          # Git ignore patterns
├── .header.md          # Custom header for documentation
├── .terraform-docs.yml # Terraform-docs configuration
└── Makefile            # Project automation (fmt, docs)
```

An additional [`Makefile`](https://github.com/oliver-reardon/terraform-scaffold-generator/blob/main/template/Makefile) is created in the new project root which can be used to format the Terraform HCL and also create project documentation using [`terraform-docs`](https://github.com/terraform-docs/terraform-docs).

```bash
.PHONY: help docs fmt

TFPATH ?= terraform
p ?= $(TFPATH)

help: ## Show this help
	@echo "Terraform Documentation Generator"
	@echo ""
	@echo "Usage: make docs [p=path] or make fmt [p=path]"
	@echo "Default path: terraform/"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "}; /^[a-zA-Z0-9_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

docs: ## Generate terraform-docs
	@if ! command -v terraform-docs >/dev/null 2>&1; then echo "terraform-docs not installed. Run: brew install terraform-docs"; exit 1; fi
	@echo "Generating documentation for $(p)..."
	@terraform-docs markdown $(p) > README.md
	@echo "Documentation updated in README.md"

fmt: ## Format Terraform files
	@echo "Formatting Terraform files in $(p)..."
	@terraform fmt -recursive $(p)/
	@echo "Terraform files formatted"
```

## Updating Terraform Module Documentation

1. Edit `.header.md` with your project description and usage instructions
2. Add comments to your Terraform variables and outputs
3. Use the project Makefile to format and generate docs

### Update the docs:
```bash
cd my-project-name

# Format your Terraform files (default: terraform/ folder)
make fmt

# Format files in a specific path
make fmt p=modules/networking

# Generate documentation (default: terraform/ folder)
make docs

# Generate docs for a specific path
make docs p=modules/networking
```

The generated `README.md` will contain:
- Your custom header from `.header.md`
- Auto-generated tables of inputs (variables)
- Auto-generated tables of outputs
- Provider requirements
- Resource documentation

### Conclusion

This Terraform scaffold generator solves the common problem of inconsistent project structures across teams. By standardizing the initial setup, you reduce cognitive load, improve code quality, and make it easier for team members to work across different infrastructure projects. The Makefile approach keeps things simple while providing powerful automation for both project generation and ongoing maintenance.



