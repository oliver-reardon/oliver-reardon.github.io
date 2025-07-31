from openai import OpenAI
import frontmatter
import sys
import os
import yaml
import argparse

def generate_and_apply_suggestions(file_path, force=False):
    """
    Generate AI suggestions and apply them directly to the file's YAML front matter
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
    tags: [3-5 technical tags, lowercase, single words, use hyphens for compound terms]
    keywords: [4-6 relevant keywords, lowercase, maximum 2 words each]
    
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
        
        # Build YAML front matter manually to preserve order
        yaml_lines = ['---']
        
        # Add fields in specified order
        for field in field_order:
            if field in post.metadata:
                value = post.metadata[field]
                if isinstance(value, list):
                    # Format arrays properly
                    yaml_lines.append(f'{field}:')
                    for item in value:
                        yaml_lines.append(f'  - {item}')
                elif isinstance(value, bool):
                    yaml_lines.append(f'{field}: {str(value).lower()}')
                elif isinstance(value, str) and value == '':
                    yaml_lines.append(f'{field}: ""')
                else:
                    yaml_lines.append(f'{field}: {value}')
        
        # Add any remaining fields not in the order list
        for field, value in post.metadata.items():
            if field not in field_order:
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
        
        yaml_lines.append('---')
        yaml_lines.append('')  # Empty line after front matter
        
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
    Process all changed files and apply AI-generated front matter.
    """
    parser = argparse.ArgumentParser(description='Generate AI suggestions for Hugo front matter')
    parser.add_argument('files', nargs='+', help='Markdown files to process')
    parser.add_argument('--force', '-f', action='store_true', 
                       help='Override existing tags and keywords')
    
    args = parser.parse_args()
    
    results = []
    
    for file_path in args.files:
        if file_path.endswith('.md') and 'content/posts' in file_path:
            result = generate_and_apply_suggestions(file_path, force=args.force)
            results.append(result)
            print(result)
    
    # Write summary for GitHub comment
    summary = "## AI Front Matter Applied\n\n" + "\n".join([f"- {r}" for r in results])
    with open('ai-summary.md', 'w') as f:
        f.write(summary)

if __name__ == "__main__":
    main()