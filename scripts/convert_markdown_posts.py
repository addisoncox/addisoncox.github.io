import datetime
import os
import re
import markdown
from bs4 import BeautifulSoup
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

pre_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="./../styles.css"/>
    <title>Addison Cox</title>
</head>
<body>
    <header>
        <nav>
            <ul>
                <li><a href="/">Home</a></li>
                <li><a href="./posts">Posts</a></li>
                <li><a href="./contact">Contact</a></li>
            </ul>
        </nav>
    </header>
    
    <section class="content">
<div class="container">
'''

post_html = '''
</div>
    </section>
    
</body>
'''

def extract_date_from_markdown(markdown_file):
    with open(markdown_file, 'r', encoding='utf-8') as file:
        first_line = file.readline().strip()

    match = re.match(r'(\d{2}/\d{2}/\d{4})', first_line)
    if match:
        return match.group(1)
    else:
        return None

def sort_posts_by_date(post_list, dates):
    # Combine post_list and dates into tuples
    combined_data = list(zip(post_list, dates))

    # Sort the combined data by date
    sorted_data = sorted(combined_data, key=lambda x: datetime.datetime.strptime(x[1], "%m/%d/%Y"), reverse=True)

    # Extract the sorted posts from the sorted data
    sorted_posts = [post for post, _ in sorted_data]

    return sorted_posts

def convert_markdown_to_html(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as md_file:
        # Skip the first line containing the date
        md_file.readline()
        markdown_content = md_file.read()

    html_content = markdown.markdown(markdown_content)

    with open(output_file, 'w', encoding='utf-8') as html_file:
        html_file.write( pre_html + html_content + post_html)

def generate_post_list_html(post_list):
    post_list_html = '<ul class="post-list">\n'
    for post_title, post_url in post_list:
        post_list_html += f'    <li><a href="{post_url}">{post_title}</a></li>\n'
    post_list_html += '</ul>\n'
    return post_list_html

def update_posts_html(existing_html_file, post_list):
    with open(existing_html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    existing_post_list = soup.find('ul', class_='post-list')

    if existing_post_list:

        existing_post_list.clear()

        for post_title, post_url in post_list:
            li_tag = soup.new_tag('li')
            a_tag = soup.new_tag('a', href=post_url)
            a_tag.string = post_title
            li_tag.append(a_tag)
            existing_post_list.append(li_tag)

        with open(existing_html_file, 'w', encoding='utf-8') as file:
            file.write(str(soup))
    else:
        print("Error: Could not find the existing post list in the HTML file.")

def add_syntax_highlighting(html_file):
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    pre_elements = soup.find_all('pre')

    for pre in pre_elements:
        code = pre.find('code')
        if code:

            code_content = code.get_text()
            language = pre.get('class')[0]

            lexer = get_lexer_by_name(language, stripall=True)
            formatter = HtmlFormatter()
            highlighted_code = highlight(code_content, lexer, formatter)

            code.replace_with(BeautifulSoup(highlighted_code, 'html.parser'))

    # Write the updated HTML content to the same file
    with open(html_file, 'w', encoding='utf-8') as file:
        file.write(str(soup))

def convert_markdown_files_in_directory(directory):
    # Check if the directory exists
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        return

    post_list = []
    dates = []

    for filename in os.listdir(directory):
        if filename.endswith(".md"):
            md_file_path = os.path.join(directory, filename)
            html_file_path = os.path.join('../posts', f"{os.path.splitext(filename)[0]}.html")

            dates.append(extract_date_from_markdown(md_file_path))
            post_title = os.path.splitext(filename)[0]
            post_url = f"/posts/{post_title.lower()}"
            post_list.append((post_title, post_url))

            convert_markdown_to_html(md_file_path, html_file_path)
            add_syntax_highlighting(html_file_path)


    update_posts_html('../posts.html', sort_posts_by_date(post_list, dates))

if __name__ == "__main__":
    directory_path = '../md/posts'
    convert_markdown_files_in_directory(directory_path)
    print(f"Conversion and syntax highlighting complete for files in '{directory_path}' directory.")
