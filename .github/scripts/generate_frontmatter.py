from openai import OpenAI
import frontmatter
import sys
import os
import yaml
import argparse

def generate_and_apply_suggestions(file_path, force=False):
    """
    Generate AI suggestions and apply them directly to the file's YAML front matter.
    """
    # Load the markdown file with YAML front matter
    with open(file_path, 'r') as f:
        post = frontmatter.load(f)
    
    # Skip if tags and keywords already exist and are not empty (unless force is True)
    existing_tags = post.metadata.get('tags', [])
    existing_keywords = post.metadata.get('keywords', [])
    
    # Check if tags/keywords exist and are not empty
    if not force and (existing_tags and existing_keywords and 
        len(existing_tags) > 0 and len(existing_keywords) > 0):
        print(f"Skipping {file_path} - already has populated tags and keywords (use --force to override)")
        return f"Skipped {file_path} - already has tags and keywords"
    
    print(f"Processing {file_path}...")
    print(f"Current tags: {existing_tags}")
    print(f"Current keywords: {existing_keywords}")
    
    # Extract content and title
    content = post.content[:2000]  
    title = post.metadata.get('title', 'Untitled')
    
    # Construct the AI prompt
    prompt = f"""
    Analyze this Hugo blog post and suggest relevant tags and keywords.
    
    Title: {title}
    Content: {content}
    
    Return ONLY a valid YAML structure with:
    tags: [8 technical tags, lowercase, single words, use hyphens for compound terms]
    keywords: [6 relevant keywords, lowercase, maximum 2 words each]
    
    Example format:
    tags: ["aws", "terraform", "automation", "cloud-storage"]
    keywords: ["proxy server", "browser configuration", "cloud hosting"]
    """
    
    try:
        # Generate AI suggestions
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        # Parse the AI response as YAML
        ai_response = response.choices[0].message.content.strip()
        print(f"AI Response: {ai_response}")
        
        suggestions = yaml.safe_load(ai_response)
        print(f"Parsed suggestions: {suggestions}")
        
        # Apply suggestions to front matter
        if 'tags' in suggestions:
            post.metadata['tags'] = suggestions['tags']
        if 'keywords' in suggestions:
            post.metadata['keywords'] = suggestions['keywords']
        
        # Always add author if not already present
        if not post.metadata.get('author'):
            post.metadata['author'] = 'Oliver Reardon'
        
        # Manually write YAML with proper field order
        field_order = [
            'title', 'date', 'author', 
            'tags', 'keywords', 'description', 'showFullContent', 
            'readingTime', 'hideComments', 'draft'
        ]
        
        # Build YAML front matter manually to preserve field order
        # We can't use yaml.dump() because it doesn't preserve our custom field ordering
        yaml_lines = ['---']
        
        # STEP 1: Add fields in our preferred order (title, date, author, tags, etc.)
        # This ensures consistent front matter structure across all posts
        for field in field_order:
            if field in post.metadata:  # Only add fields that actually exist
                value = post.metadata[field]
                
                # Handle different data types with proper YAML formatting
                if isinstance(value, list):
                    # Arrays: tags: \n  - item1 \n  - item2
                    yaml_lines.append(f'{field}:')
                    for item in value:
                        yaml_lines.append(f'  - {item}')
                elif isinstance(value, bool):
                    # Booleans: showFullContent: true (lowercase for YAML)
                    yaml_lines.append(f'{field}: {str(value).lower()}')
                elif isinstance(value, str) and value == '':
                    # Empty strings: description: ""
                    yaml_lines.append(f'{field}: ""')
                else:
                    # Everything else (strings, numbers, dates): field: value
                    yaml_lines.append(f'{field}: {value}')
        
        # STEP 2: Add any remaining fields that weren't in our ordered list
        # This catches custom fields or fields we forgot to include in field_order
        for field, value in post.metadata.items():
            if field not in field_order:  # Skip fields we already processed above
                # Use the same formatting logic as above
                if isinstance(value, list):
                    yaml_lines.append(f'{field}:')
                    for item in value:
                        yaml_lines.append(f'  - {item}')
                elif isinstance(value, bool):
                    yaml_lines.append(f'{field}: {str(value).lower()}')
                elif isinstance(value, str) and value == '':
                    yaml_lines.append(f'{field}: ""')
                else:
                    yaml_lines.append(f'{field}: {value}')
        
        # Close the YAML front matter block
        yaml_lines.append('---')
        yaml_lines.append('')  # Empty line between front matter and content
        
        # Write the file manually
        with open(file_path, 'w') as f:
            f.write('\n'.join(yaml_lines))
            f.write(post.content)
        
        force_msg = " (forced)" if force else ""
        return f"Applied AI suggestions to {file_path}{force_msg}"
        
    except Exception as e:
        return f"Error processing {file_path}: {str(e)}"

def main():
    """
    Main entry point - processes command line arguments and applies AI-generated front matter to markdown files.
    
    This function handles both single file processing (local testing) and multiple file processing 
    (GitHub Actions workflow). It generates a summary file for GitHub PR comments.
    """
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Generate AI suggestions for Hugo front matter')
    parser.add_argument('files', nargs='+', help='Markdown files to process (supports glob patterns)')
    parser.add_argument('--force', '-f', action='store_true', 
                       help='Override existing tags and keywords even if they already exist')
    
    # Parse the provided command line arguments
    args = parser.parse_args()
    
    # Track results for summary generation
    results = []
    
    # Process each file provided via command line arguments
    for file_path in args.files:
        # Only process markdown files in the posts directory
        # This prevents accidentally processing other markdown files (README, etc.)
        if file_path.endswith('.md') and 'content/posts' in file_path:
            # Apply AI suggestions to this specific file
            result = generate_and_apply_suggestions(file_path, force=args.force)
            results.append(result)
            print(result)  # Real-time feedback during processing
    
    # Generate summary file for GitHub Actions workflow
    # This file gets read by the GitHub Action to post a PR comment
    summary = "## AI Front Matter Applied\n\n" + "\n".join([f"- {r}" for r in results])
    with open('ai-summary.md', 'w') as f:
        f.write(summary)

# Standard Python idiom - only run main() when script is executed directly
# (not when imported as a module)
if __name__ == "__main__":
    main()