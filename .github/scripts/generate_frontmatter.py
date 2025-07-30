from openai import OpenAI
import frontmatter
import sys
import os
import yaml

def generate_and_apply_suggestions(file_path):
    """
    Generate AI suggestions and apply them directly to the file's front matter.
    """
    # Load the markdown file with TOML front matter parsing
    with open(file_path, 'r') as f:
        post = frontmatter.load(f, handler=frontmatter.TOMLHandler())  # Specify TOML handler
    
    # Skip if tags and keywords already exist and are not empty
    existing_tags = post.metadata.get('tags', [])
    existing_keywords = post.metadata.get('keywords', [])
    
    # Check if tags/keywords exist and are not just empty strings
    if (existing_tags and existing_tags != ["", ""] and 
        existing_keywords and existing_keywords != ["", ""]):
        print(f"Skipping {file_path} - already has populated tags and keywords")
        return f"Skipped {file_path} - already has tags and keywords"
    
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
        suggestions = yaml.safe_load(ai_response)
        
        # Apply suggestions to front matter
        if 'tags' in suggestions:
            post.metadata['tags'] = suggestions['tags']
        if 'keywords' in suggestions:
            post.metadata['keywords'] = suggestions['keywords']
        
        # Write back to file with TOML format
        with open(file_path, 'w') as f:
            f.write(frontmatter.dumps(post, handler=frontmatter.TOMLHandler()))  # Use TOML handler
        
        return f"Applied AI suggestions to {file_path}"
        
    except Exception as e:
        return f"Error processing {file_path}: {str(e)}"

def main():
    """
    Process all changed files and apply AI-generated front matter.
    """
    if len(sys.argv) < 2:
        return
        
    files = sys.argv[1].split()
    results = []
    
    for file_path in files:
        if file_path.endswith('.md') and 'content/posts' in file_path:
            result = generate_and_apply_suggestions(file_path)
            results.append(result)
            print(result)
    
    # Write summary for GitHub comment
    summary = "## AI Front Matter Applied\n\n" + "\n".join([f"- {r}" for r in results])
    with open('ai-summary.md', 'w') as f:
        f.write(summary)

if __name__ == "__main__":
    main()