from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from pathlib import Path
import markdown
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.toc import TocExtension
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, PythonLexer
import re

router = APIRouter(prefix="/docs", tags=["documentation"])

DOCS_DIR = Path(__file__).parent.parent.parent / "docs"

def process_mermaid_blocks(content):
    """Pre-process Mermaid blocks in markdown before conversion"""
    def replace_mermaid(match):
        code = match.group(1).strip()
        # Create a pre-rendered SVG container
        return f'''<div class="mermaid-diagram">
            <pre style="display: none">{code}</pre>
            <div class="mermaid-svg"></div>
        </div>'''
    
    # Handle ```mermaid blocks
    content = re.sub(
        r'```mermaid\s*(.*?)```',
        replace_mermaid,
        content,
        flags=re.DOTALL
    )
    
    # Handle ```sequence blocks
    content = re.sub(
        r'```sequence\s*(.*?)```',
        lambda m: replace_mermaid(type('Match', (), {'group': lambda x: 'sequenceDiagram\n' + m.group(1) if x == 1 else None})),
        content,
        flags=re.DOTALL
    )
    
    return content

def process_code_blocks(html_content):
    """Process code blocks with proper syntax highlighting"""
    def replace_code_block(match):
        code = match.group(2)
        lang = match.group(1) if match.group(1) else 'python'
        
        # Skip Mermaid blocks
        if lang.lower() in ['mermaid', 'sequence']:
            return match.group(0)
            
        try:
            lexer = get_lexer_by_name(lang)
        except:
            lexer = PythonLexer()
            
        formatter = HtmlFormatter(
            style='monokai',
            cssclass='highlight',
            linenos=True
        )
        
        highlighted = highlight(code, lexer, formatter)
        return highlighted
    
    # Handle code blocks with language specification
    pattern = r'<pre><code class="language-([^"]+)">(.*?)</code></pre>'
    html_content = re.sub(pattern, replace_code_block, html_content, flags=re.DOTALL)
    
    # Handle code blocks without language specification
    pattern = r'<pre><code>(.*?)</code></pre>'
    html_content = re.sub(pattern, lambda m: replace_code_block(type('Match', (), {'group': lambda x: ('python' if x == 1 else m.group(1))})), html_content, flags=re.DOTALL)
    
    return html_content

@router.get("/", response_class=HTMLResponse)
async def list_docs(request: Request):
    """List all available documentation files"""
    try:
        base_url = str(request.base_url).rstrip('/')
        docs = sorted([f.stem for f in DOCS_DIR.glob("*.md")])
        
        # Create HTML list with links
        html_content = f"""
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; color: #333; }}
            h1 {{ color: #2c3e50; margin-bottom: 30px; }}
            ul {{ list-style: none; padding: 0; }}
            li {{ margin: 10px 0; padding: 15px; border: 1px solid #e1e4e8; border-radius: 6px; transition: all 0.2s; }}
            li:hover {{ border-color: #0366d6; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            a {{ color: #0366d6; text-decoration: none; font-weight: 500; }}
            a:hover {{ text-decoration: underline; }}
        </style>
        <h1>Documentation</h1>
        <ul>
        """
        
        for doc in docs:
            html_content += f'<li><a href="{base_url}/docs/{doc}">{doc}</a></li>'
            
        html_content += """
        </ul>
        """
        return html_content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{doc_name}", response_class=HTMLResponse)
async def get_doc(doc_name: str):
    """Get documentation content"""
    try:
        file_path = DOCS_DIR / f"{doc_name}.md"
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Documentation not found")
            
        content = file_path.read_text()
        
        # Pre-process code blocks to preserve formatting
        def preprocess_code_blocks(content):
            def replace_block(match):
                code = match.group(2)
                lang = match.group(1) or ''
                # Replace problematic characters with placeholders
                code = code.replace('{', '___LCURL___')
                code = code.replace('}', '___RCURL___')
                code = code.replace('&quot;', '"')
                code = code.replace('&amp;', '&')
                code = code.replace('&lt;', '<')
                code = code.replace('&gt;', '>')
                return f'```{lang}\n{code}\n```'
            
            # Process fenced code blocks
            content = re.sub(r'```(\w*)\n(.*?)```', replace_block, content, flags=re.DOTALL)
            return content
            
        content = preprocess_code_blocks(content)
        
        # Pre-process Mermaid blocks
        content = process_mermaid_blocks(content)
        
        # Convert markdown to HTML
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.admonition',
            'markdown.extensions.sane_lists',
            'markdown.extensions.smarty',
            FencedCodeExtension(),
            TableExtension(),
            TocExtension(permalink=False)
        ])
        html_content = md.convert(content)
        
        # Post-process to restore placeholders
        html_content = html_content.replace('___LCURL___', '{')
        html_content = html_content.replace('___RCURL___', '}')
        
        # Process code blocks for syntax highlighting
        html_content = process_code_blocks(html_content)
        
        # Get Pygments CSS
        pygments_css = HtmlFormatter(style='monokai').get_style_defs('.highlight')
        
        # Add enhanced CSS for better readability
        styled_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{doc_name} - Documentation</title>
            <script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                    line-height: 1.6;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    color: #24292e;
                }}
                
                h1, h2, h3, h4, h5, h6 {{
                    color: #2c3e50;
                    margin-top: 24px;
                    margin-bottom: 16px;
                    font-weight: 600;
                    line-height: 1.25;
                }}
                
                h1 {{ font-size: 2em; padding-bottom: .3em; border-bottom: 1px solid #eaecef; }}
                h2 {{ font-size: 1.5em; padding-bottom: .3em; border-bottom: 1px solid #eaecef; }}
                
                p {{ margin-top: 0; margin-bottom: 16px; }}
                
                pre {{
                    margin: 0;
                    padding: 16px;
                    overflow: auto;
                    font-size: 14px;
                    line-height: 1.45;
                    background-color: #1e1e1e;
                    border-radius: 6px;
                }}
                
                code {{
                    font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
                    font-size: 85%;
                    background-color: rgba(110, 118, 129, 0.4);
                    border-radius: 3px;
                    padding: 0.2em 0.4em;
                    margin: 0;
                }}
                
                .highlight {{
                    margin: 1em 0;
                    padding: 0;
                    background: #1e1e1e;
                    color: #e6e6e6;
                    border-radius: 6px;
                }}
                
                .highlight pre {{
                    margin: 0;
                    padding: 16px;
                    overflow: auto;
                    font-size: 14px;
                    line-height: 1.45;
                }}
                
                .highlight .lineno {{
                    color: #6e7681;
                    padding-right: 16px;
                    margin-right: 16px;
                    border-right: 1px solid #6e7681;
                    -webkit-user-select: none;
                    -moz-user-select: none;
                    -ms-user-select: none;
                    user-select: none;
                }}
                
                .highlight .line {{
                    display: inline-block;
                    width: 100%;
                }}
                
                .highlight .line:hover {{
                    background: rgba(110, 118, 129, 0.1);
                }}
                
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 15px 0;
                    overflow: auto;
                }}
                
                th, td {{
                    border: 1px solid #dfe2e5;
                    padding: 6px 13px;
                }}
                
                th {{
                    background-color: #f6f8fa;
                    font-weight: 600;
                }}
                
                tr:nth-child(2n) {{
                    background-color: #f6f8fa;
                }}
                
                blockquote {{
                    margin: 0;
                    padding: 0 1em;
                    color: #6a737d;
                    border-left: 0.25em solid #dfe2e5;
                }}
                
                .nav {{
                    margin-bottom: 32px;
                    padding-bottom: 16px;
                    border-bottom: 1px solid #eaecef;
                }}
                
                .nav a {{
                    color: #0366d6;
                    text-decoration: none;
                    font-weight: 500;
                }}
                
                .nav a:hover {{
                    text-decoration: underline;
                }}
                
                ul {{ padding-left: 2em; }}
                ol {{ padding-left: 2em; }}
                li + li {{ margin-top: 0.25em; }}
                
                .mermaid-diagram {{ 
                    background: #0d1117;
                    padding: 16px;
                    border-radius: 6px;
                    margin: 16px 0;
                }}
                
                .mermaid-svg svg {{
                    max-width: 100%;
                    height: auto;
                }}

                {pygments_css}
            </style>
        </head>
        <body>
            <div class="nav">
                <a href="/docs">← Back to Documentation List</a>
            </div>
            {html_content}
            <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    mermaid.initialize({{ 
                        startOnLoad: false,
                        theme: 'dark'
                    }});
                    
                    document.querySelectorAll('.mermaid-diagram').forEach(function(container) {{
                        const code = container.querySelector('pre').textContent;
                        const svgContainer = container.querySelector('.mermaid-svg');
                        
                        try {{
                            mermaid.render('mermaid-' + Math.random().toString(36).substr(2, 9), code)
                                .then(function({{ svg }}) {{
                                    svgContainer.innerHTML = svg;
                                }});
                        }} catch (error) {{
                            console.error('Failed to render Mermaid diagram:', error);
                            svgContainer.innerHTML = '<pre style="color: red;">Failed to render diagram</pre>';
                        }}
                    }});
                }});
            </script>
        </body>
        </html>
        """
        return styled_content
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 