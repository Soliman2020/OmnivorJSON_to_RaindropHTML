import streamlit as st
import json
from datetime import datetime
import html
import io
import base64
from pathlib import Path
import os

def convert_omnivore_folder_to_pocket_html(folder_path):
    """
    Convert all Omnivore JSON files in a folder to Pocket-compatible HTML
    
    Args:
    folder_path: String path to folder containing JSON files
    
    Returns:
    tuple: (html_content, stats_dict)
    """
    # Start HTML file
    html_content = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Omnivore Bookmarks to Pocket</title>
</head>
<body>
<h1>Bookmarks</h1>
<dl>"""
    
    # Track statistics
    stats = {
        'total_files': 0,
        'total_articles': 0,
        'processed_files': [],
        'failed_files': []
    }
    
    # Get all JSON files in the folder
    json_files = list(Path(folder_path).glob('*.json'))
    
    # Process each JSON file
    for json_file in json_files:
        try:
            # Read JSON content
            with open(json_file, 'r', encoding='utf-8') as f:
                omnivore_data = json.load(f)
            
            # Skip if not a list
            if not isinstance(omnivore_data, list):
                stats['failed_files'].append(f"{json_file.name} (Invalid format)")
                continue
            
            file_article_count = 0
            
            # Convert each article in the file
            for article in omnivore_data:
                # Skip if no URL
                if 'url' not in article:
                    continue
                
                # Escape HTML special characters
                title = html.escape(article.get('title', article['url']))
                url = html.escape(article['url'])
                
                # Process tags/labels
                tags = ''
                if 'labels' in article and article['labels']:
                    tags = html.escape(','.join(article['labels']))
                
                # Convert timestamps if available
                try:
                    if 'savedAt' in article:
                        timestamp = datetime.fromisoformat(article['savedAt'].replace('Z', '+00:00'))
                        time_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                except:
                    time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Add bookmark entry with tags
                html_content += f"""
    <dt><a href="{url}" time_added="{time_str}" tags="{tags}">{title}</a></dt>
    <dd>{article.get('description', '')}</dd>"""
                
                file_article_count += 1
            
            stats['total_articles'] += file_article_count
            stats['processed_files'].append(f"{json_file.name} ({file_article_count} articles)")
            stats['total_files'] += 1
            
        except json.JSONDecodeError:
            stats['failed_files'].append(f"{json_file.name} (Invalid JSON)")
        except Exception as e:
            stats['failed_files'].append(f"{json_file.name} ({str(e)})")
    
    # Close HTML file
    html_content += """
</dl>
</body>
</html>"""
    
    return html_content, stats

def get_download_link(html_content, filename="pocket_import.html"):
    """Generate a download link for the HTML file"""
    b64 = base64.b64encode(html_content.encode()).decode()
    return f'<a href="data:text/html;base64,{b64}" download="{filename}">Download HTML File</a>'

# Streamlit UI
def main():
    st.set_page_config(page_title="From Omnivore to Raindrop Helper", page_icon="📚")
    
    # st.title("Omnivore JSON to Raindrop HTML")
    st.markdown("### ~~Omnivore~~ **JSON** to **<u>Raindrop HTML</u>** 🚀", unsafe_allow_html=True)
    
    st.markdown("""
    This tool converts Omnivore JSON exported files to Raindrop-compatible HTML format.
    ### ✨Instructions:
    1. On Omnivore: "Settings" -> Export all of your data as JSON files. 
        - This can be done once per day and will be delivered to your registered email address. 
        - Once your export has started you should receive an email with a link to your data within an hour. 
        - The download link will be available for 24 hours.
    2. Downlaod the ZIP file, Unzip it.
    3. Enter the folder path containing your Omnivore JSON files then press Enter.
    4. Click 'Convert to Raindrop format' to process the files.
    5. Download the generated HTML file.
    6. Import the HTML file into Raindrop.
    > Now all of your articles are on Raindrop with its corresponding tags. 🎉
    """)
    
    # Folder selection
    folder_path = st.text_input(
        "🎯 Enter the folder path containing your Omnivore JSON files below: ",
        placeholder=r"e.g., D:\omni_backup"
    )
    
    if folder_path:
        folder_path = os.path.expanduser(folder_path)  # Expand ~ to full home directory path
        if os.path.isdir(folder_path):
            json_files = list(Path(folder_path).glob('*.json'))
            if json_files:
                st.write(f"📁 Found {len(json_files)} JSON files in the folder")
                
                if st.button("Convert to Raindrop Format"):
                    with st.spinner("Converting files..."):
                        # Process files
                        html_content, stats = convert_omnivore_folder_to_pocket_html(folder_path)
                        
                        # Show statistics
                        st.subheader("Conversion Summary")
                        st.write(f"Total files processed: {stats['total_files']}")
                        st.write(f"Total articles converted: {stats['total_articles']}")
                        
                        if stats['processed_files']:
                            st.subheader("Successfully Processed Files")
                            for file in stats['processed_files']:
                                st.write(f"✅ {file}")
                        
                        if stats['failed_files']:
                            st.subheader("Failed Files")
                            for file in stats['failed_files']:
                                st.write(f"❌ {file}")
                        
                        # Generate download link
                        if stats['total_articles'] > 0:
                            st.subheader("Download")
                            st.markdown(get_download_link(html_content), unsafe_allow_html=True)
                            st.info("👆 Click the link above to download your Pocket import file")
            else:
                st.warning("No JSON files found in the selected folder")
        else:
            st.error("Invalid folder path. Please enter a valid folder path.")
    else:
        st.info("Please enter the folder path containing your JSON files to begin")

if __name__ == "__main__":
    main()
