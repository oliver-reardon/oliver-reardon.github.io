from openai import OpenAI  # Changed from: import openai
import frontmatter
import sys
import os

def generate_suggestions(file_path):
    """
    Analyze a Hugo blog post and generate AI-powered front matter suggestions.
    
    Args:
        file_path (str): Path to the markdown file to analyze
        
    Returns:
        str: YAML-formatted suggestions for tags and keywords
    """
    # Load the markdown file with front matter parsing
    with open(file_path, 'r') as f:
        post = frontmatter.load(f)
    
    # Extract the first 2000 characters of content to stay within API limits
    content = post.content[:2000]  
    # Get the title from existing front matter, default to 'Untitled'
    title = post.metadata.get('title', 'Untitled')
    
    # Construct the AI prompt with specific instructions
    prompt = f"""
    Analyze this Hugo blog post and suggest relevant tags and keywords.
    
    Title: {title}
    Content: {content}
    
    Return YAML format with:
    - tags: 5-8 technical tags
    - keywords: 8-12 relevant keywords
    
    Focus on: technology, tools, programming languages, frameworks, concepts mentioned.
    """
    
    # NEW: Create client instance
    client = OpenAI()  # Uses OPENAI_API_KEY environment variable automatically
    
    # NEW: Updated API call syntax
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3  # Low temperature for more consistent/focused responses
    )
    
    # Return the AI-generated suggestions
    return response.choices[0].message.content

def main():
    """
    Main function that processes command line arguments and generates suggestions
    for all changed markdown files in the content/posts directory.
    """
    # Check if file paths were provided as command line arguments
    if len(sys.argv) < 2:
        return
        
    # Parse the space-separated file paths from command line argument
    files = sys.argv[1].split()
    # Initialize the markdown output with header
    suggestions_md = "## 🤖 AI Front Matter Suggestions\n\n"
    
    # Process each file that was changed in the PR
    for file_path in files:
        # Only process markdown files in the content/posts directory
        if file_path.endswith('.md') and 'content/posts' in file_path:
            try:
                # Generate AI suggestions for this specific file
                suggestion = generate_suggestions(file_path)
                # Add the suggestions to the markdown output with file header
                suggestions_md += f"### {file_path}\n\n```yaml\n{suggestion}\n```\n\n"
            except Exception as e:
                # Handle errors gracefully and include them in the output
                suggestions_md += f"### {file_path}\n\nError generating suggestions: {str(e)}\n\n"
    
    # Write the complete suggestions to a file that GitHub Actions can read
    with open('ai-suggestions.md', 'w') as f:
        f.write(suggestions_md)

# Entry point when script is run directly
if __name__ == "__main__":
    main()