import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

def init_session_state():
    if "files_processed" not in st.session_state:
        st.session_state.files_processed = False
    if "file_contents" not in st.session_state:
        st.session_state.file_contents = {}
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "readme_generated" not in st.session_state:
        st.session_state.readme_generated = ""
    if "raw_prompt" not in st.session_state:
        st.session_state.raw_prompt = ""
    if "reset_counter" not in st.session_state:
        st.session_state.reset_counter = 0

def configure_gemini():
    """Configure Gemini API"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        return True
    else:
        st.error("🚨 Google API Key not found. Please set the GOOGLE_API_KEY environment variable.")
        return False

def get_system_prompt():
    return """You are an advanced README generator AI. You must output ONLY clean, properly formatted Markdown content without any code block markers or additional formatting.

When composing the README, follow these guidelines:

1. **Project Title and Badge Section**  
   - Extract or infer a concise project title.  
   - Optionally include status/version/build badges if present in the files or mentioned in the prompt.

2. **Project Description**  
   - Summarize the project's purpose, features, and high-level architecture.  
   - Explain what problem it solves and who the intended users are.

3. **Table of Contents**  
   - Automatically generate links to the main sections of the README.

4. **Installation**  
   - Detail any prerequisites (languages, frameworks, tools).  
   - Provide step-by-step setup or installation commands derived from environment/config files.

5. **Usage**  
   - Show common usage patterns or code snippets.  
   - Explain command-line flags, configuration options, or API endpoints based on the project files.

6. **Configuration**  
   - Describe configuration files (e.g., `.env`, `config.yaml`) and their options/values.

7. **Features / Functionality**  
   - List and briefly explain the main features or modules, pulling from code comments or directory structure.

8. **Examples**  
   - Provide sample input/output or screenshots if available.

9. **API Reference** (for libraries or services)  
   - Document exposed functions, classes, or endpoints with parameters and return values.

10. **Contributing**  
    - Offer guidelines for how developers can contribute, referencing any `CONTRIBUTING.md` or coding standards.

11. **Testing**  
    - Explain how to run tests, including commands and testing frameworks picked up from the files.

12. **License**  
    - Detect and state the project's license based on LICENSE file or user prompt.

13. **Acknowledgements / Credits**  
    - Mention authors, third-party libraries, or inspirations.

14. **Contact / Support**  
    - Describe how to reach maintainers or link to issue tracker/discussion forums.

**Critical Formatting Rules:**  
- Output ONLY the markdown content, do not wrap it in code blocks (```markdown or ```)
- Start directly with the project title using # heading
- Use proper Markdown syntax: headings (#, ##, ###), bullet lists (-), numbered lists (1.)
- Include fenced code blocks with language specification for code examples
- Use **bold** and *italic* text appropriately
- Create proper links and references
- Ensure all sections flow naturally without extra formatting markers

Always tailor the README to the specific project context. Generate clean, ready-to-use Markdown content."""

def create_copy_button(text_to_copy, button_text="📋 Copy to Clipboard"):
    """Create a copy button component with dark theme compatible styling"""
    unique_id = str(uuid.uuid4()).replace('-', '')
    
    # Escape the text for JavaScript
    escaped_text = text_to_copy.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
    
    copy_component = f"""
    <div id="copy-container-{unique_id}" style="margin: 10px 0;">
        <button id="copy-btn-{unique_id}" 
                onclick="copyToClipboard{unique_id}()" 
                style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 12px;
                    cursor: pointer;
                    font-weight: 600;
                    font-size: 14px;
                    width: 100%;
                    box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
                    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 8px;
                    min-height: 48px;
                "
                onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 12px 24px rgba(102, 126, 234, 0.4)'"
                onmouseout="this.style.transform='translateY(0px)'; this.style.boxShadow='0 8px 16px rgba(102, 126, 234, 0.3)'"
                >
            <span style="font-size: 16px;">📋</span>
            <span>Copy to Clipboard</span>
        </button>
        
        <textarea id="copy-text-{unique_id}" 
                  style="position: absolute; left: -9999px; opacity: 0;"
                  readonly>{escaped_text}</textarea>
    </div>

    <script>
        function copyToClipboard{unique_id}() {{
            const button = document.getElementById('copy-btn-{unique_id}');
            const textArea = document.getElementById('copy-text-{unique_id}');
            
            try {{
                // Method 1: Modern clipboard API
                if (navigator.clipboard && window.isSecureContext) {{
                    navigator.clipboard.writeText(textArea.value).then(() => {{
                        button.innerHTML = '<span style="font-size: 16px;">✅</span><span>Copied!</span>';
                        button.style.background = 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)';
                        button.style.transform = 'scale(0.95)';
                        setTimeout(() => {{
                            button.innerHTML = '<span style="font-size: 16px;">📋</span><span>Copy to Clipboard</span>';
                            button.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                            button.style.transform = 'scale(1)';
                        }}, 2000);
                    }}).catch(() => {{
                        fallbackCopy{unique_id}();
                    }});
                }} else {{
                    fallbackCopy{unique_id}();
                }}
            }} catch (err) {{
                fallbackCopy{unique_id}();
            }}
        }}
        
        function fallbackCopy{unique_id}() {{
            const button = document.getElementById('copy-btn-{unique_id}');
            const textArea = document.getElementById('copy-text-{unique_id}');
            
            try {{
                textArea.style.position = 'static';
                textArea.style.opacity = '1';
                textArea.select();
                textArea.setSelectionRange(0, 99999);
                
                const successful = document.execCommand('copy');
                
                textArea.style.position = 'absolute';
                textArea.style.opacity = '0';
                
                if (successful) {{
                    button.innerHTML = '<span style="font-size: 16px;">✅</span><span>Copied!</span>';
                    button.style.background = 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)';
                    setTimeout(() => {{
                        button.innerHTML = '<span style="font-size: 16px;">📋</span><span>Copy to Clipboard</span>';
                        button.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                    }}, 2000);
                }} else {{
                    throw new Error('Copy command failed');
                }}
            }} catch (err) {{
                button.innerHTML = '<span style="font-size: 16px;">⚠️</span><span>Manual Copy Needed</span>';
                button.style.background = 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)';
                setTimeout(() => {{
                    button.innerHTML = '<span style="font-size: 16px;">📋</span><span>Copy to Clipboard</span>';
                    button.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                }}, 3000);
            }}
        }}
    </script>
    """
    return copy_component

def read_file_content(uploaded_file):
    """Read content from uploaded file based on file type"""
    try:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        # Text-based files that can be read as UTF-8
        text_extensions = {
            'py', 'txt', 'md', 'json', 'yaml', 'yml', 'html', 'css', 'js', 
            'xml', 'csv', 'toml', 'ini', 'sh', 'bat', 'ps1', 'sql', 'log',
            'gitignore', 'dockerfile', 'makefile', 'rakefile', 'gemfile',
            'rc', 'htaccess', 'htpasswd', 'prettierrc', 'eslintrc', 'babelrc',
            'editorconfig', 'conf', 'cfg'
        }
        
        # Special handling for files without extensions but known names
        special_files = {
            'dockerfile', 'makefile', 'rakefile', 'gemfile', 'jenkinsfile'
        }
        
        filename_lower = uploaded_file.name.lower()
        
        if file_extension in text_extensions or filename_lower in special_files or 'config' in filename_lower:
            # Read as text
            content = uploaded_file.read().decode('utf-8')
            return content
        else:
            # For binary files, just return file info
            return f"[Binary file: {uploaded_file.name} - Size: {uploaded_file.size} bytes]"
            
    except UnicodeDecodeError:
        return f"[Binary file: {uploaded_file.name} - Could not read as text]"
    except Exception as e:
        return f"[Error reading file {uploaded_file.name}: {str(e)}]"

def generate_readme(raw_prompt, file_contents):
    """Generate README using Gemini"""
    try:
        # Create the model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Prepare file contents for the prompt
        files_section = ""
        if file_contents:
            files_section = "\n\n**Project Files:**\n"
            for filename, content in file_contents.items():
                files_section += f"\n--- {filename} ---\n{content}\n"
        
        # Combine system prompt with user's raw prompt and file contents
        full_prompt = f"{get_system_prompt()}\n\n**User Project Description:**\n{raw_prompt}{files_section}\n\nGenerate a comprehensive README.md based on the above information."
        
        # Generate response
        response = model.generate_content(full_prompt)
        
        return response.text
    except Exception as e:
        st.error(f"Error generating README: {str(e)}")
        return None

def add_custom_css():
    """Add custom CSS for dark theme compatibility"""
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Custom Typography */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Updated header styling to separate emoji from text */
    .main-header {
        font-weight: 700;
        font-size: 3rem;
        text-align: center;
        margin-bottom: 0.5rem;
        line-height: 1.2;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }

    .header-emoji {
        font-size: 3rem;
        /* Keep emoji natural - no background clip */
    }

    .header-text {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* Update the mobile responsiveness section */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem !important;
            flex-direction: column !important;
            gap: 0.25rem !important;
        }
        
        .header-emoji {
            font-size: 2rem !important;
        }
    }
    
    .main-subtitle {
        text-align: center;
        color: var(--text-color-secondary, #8b949e);
        font-size: 1.2rem;
        font-weight: 400;
        margin-bottom: 2rem;
        opacity: 0.8;
    }
    
    /* Dark theme compatible cards */
    .custom-card {
        background: var(--background-color, rgba(255, 255, 255, 0.05));
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        border: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
        margin-bottom: 2rem;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .custom-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.4);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    /* Section Headers - Dark theme compatible */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--text-color, #e6edf3);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .section-icon {
        font-size: 1.2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Input Styling - Dark theme compatible */
    .stTextArea textarea {
        border-radius: 12px !important;
        border: 2px solid var(--border-color, rgba(255, 255, 255, 0.2)) !important;
        background-color: var(--background-color, rgba(0, 0, 0, 0.2)) !important;
        color: var(--text-color, #e6edf3) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
        line-height: 1.6 !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
    }
    
    .stTextArea textarea::placeholder {
        color: var(--text-color-secondary, #8b949e) !important;
        opacity: 0.7 !important;
    }
    
    /* File Uploader Styling - Dark theme compatible */
    .stFileUploader {
        margin: 1rem 0;
    }
    
    .stFileUploader > div {
        border-radius: 12px !important;
        border: 2px dashed var(--border-color, rgba(255, 255, 255, 0.3)) !important;
        background: var(--background-color, rgba(0, 0, 0, 0.1)) !important;
        padding: 2rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stFileUploader > div:hover {
        border-color: #667eea !important;
        background: rgba(102, 126, 234, 0.1) !important;
    }
    
    .stFileUploader label {
        color: var(--text-color, #e6edf3) !important;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0px) !important;
    }
    
    /* Secondary Button - Dark theme compatible */
    .stButton > button[kind="secondary"] {
        background: var(--background-color, rgba(255, 255, 255, 0.1)) !important;
        color: var(--text-color, #e6edf3) !important;
        border: 1px solid var(--border-color, rgba(255, 255, 255, 0.2)) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.15) !important;
        border-color: rgba(102, 126, 234, 0.5) !important;
    }
    
    /* Download Button Special Styling */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
    }
    
    /* Success/Error Messages - Dark theme compatible */
    .stSuccess {
        background: rgba(16, 185, 129, 0.15) !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        color: #10b981 !important;
    }
    
    .stError {
        background: rgba(248, 113, 113, 0.15) !important;
        border: 1px solid rgba(248, 113, 113, 0.3) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        color: #f87171 !important;
    }
    
    .stWarning {
        background: rgba(251, 191, 36, 0.15) !important;
        border: 1px solid rgba(251, 191, 36, 0.3) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        color: #fbbf24 !important;
    }
    
    .stInfo {
        background: rgba(59, 130, 246, 0.15) !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        color: #3b82f6 !important;
    }
    
    /* Expander Styling - Dark theme compatible */
    .streamlit-expanderHeader {
        background: var(--background-color, rgba(255, 255, 255, 0.05)) !important;
        border-radius: 8px !important;
        border: 1px solid var(--border-color, rgba(255, 255, 255, 0.1)) !important;
        font-weight: 500 !important;
        color: var(--text-color, #e6edf3) !important;
    }
    
    .streamlit-expanderContent {
        background: var(--background-color, rgba(0, 0, 0, 0.1)) !important;
        border: 1px solid var(--border-color, rgba(255, 255, 255, 0.1)) !important;
        border-top: none !important;
    }
    
    /* Radio Button Styling - Dark theme compatible */
    .stRadio > div {
        flex-direction: row !important;
        gap: 1rem !important;
    }
    
    .stRadio label {
        background: var(--background-color, rgba(255, 255, 255, 0.05)) !important;
        padding: 0.5rem 1rem !important;
        border-radius: 8px !important;
        border: 1px solid var(--border-color, rgba(255, 255, 255, 0.1)) !important;
        transition: all 0.3s ease !important;
        color: var(--text-color, #e6edf3) !important;
    }
    
    .stRadio label:hover {
        background: rgba(102, 126, 234, 0.1) !important;
        border-color: rgba(102, 126, 234, 0.3) !important;
    }
    
    /* Divider Styling */
    .stDivider {
        margin: 2rem 0 !important;
    }
    
    /* Code Block Styling - Dark theme compatible */
    .stCode {
        border-radius: 12px !important;
        border: 1px solid var(--border-color, rgba(255, 255, 255, 0.1)) !important;
        background: var(--background-color, rgba(0, 0, 0, 0.3)) !important;
    }
    
    /* Markdown Content Styling - Dark theme compatible */
    .stMarkdown {
        line-height: 1.7 !important;
        color: var(--text-color, #e6edf3) !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: var(--text-color, #e6edf3) !important;
        font-weight: 600 !important;
    }
    
    /* Progress Bar */
    .stProgress {
        margin: 1rem 0 !important;
    }
    
    /* Columns Gap */
    .row-widget {
        gap: 2rem !important;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* File Preview Styling - Dark theme compatible */
    .file-preview {
        background: var(--background-color, rgba(0, 0, 0, 0.2));
        border: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        font-size: 12px;
        color: var(--text-color, #e6edf3);
        max-height: 200px;
        overflow-y: auto;
    }
    
    /* Metric styling - Dark theme compatible */
    .stMetric {
        background: var(--background-color, rgba(255, 255, 255, 0.05)) !important;
        padding: 1rem !important;
        border-radius: 8px !important;
        border: 1px solid var(--border-color, rgba(255, 255, 255, 0.1)) !important;
    }
    
    .stMetric label {
        color: var(--text-color-secondary, #8b949e) !important;
    }
    
    .stMetric [data-testid="metric-value"] {
        color: var(--text-color, #e6edf3) !important;
    }
    
    /* Tabs styling - Dark theme compatible */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--background-color, rgba(0, 0, 0, 0.1)) !important;
        border-radius: 8px !important;
        padding: 0.5rem !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--text-color-secondary, #8b949e) !important;
        border-radius: 6px !important;
        margin: 0 0.25rem !important;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: rgba(102, 126, 234, 0.2) !important;
        color: var(--text-color, #e6edf3) !important;
    }
    
    /* Caption styling - Dark theme compatible */
    .stCaption {
        color: var(--text-color-secondary, #8b949e) !important;
    }
    
    /* Spinner styling - Dark theme compatible */
    .stSpinner {
        color: #667eea !important;
    }
    
    /* Animation Classes */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease-out;
    }
    
    /* Mobile Responsiveness */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem !important;
        }
        
        .custom-card {
            padding: 1.5rem !important;
            margin-bottom: 1rem !important;
        }
        
        .row-widget {
            flex-direction: column !important;
        }
    }
    
    /* CSS Variables for theme compatibility */
    :root {
        --text-color: #e6edf3;
        --text-color-secondary: #8b949e;
        --background-color: rgba(255, 255, 255, 0.05);
        --border-color: rgba(255, 255, 255, 0.1);
    }
    
    /* Light theme overrides (when body has light theme class) */
    .stApp[data-theme="light"] {
        --text-color: #1f2937;
        --text-color-secondary: #6b7280;
        --background-color: rgba(255, 255, 255, 0.8);
        --border-color: rgba(229, 231, 235, 0.8);
    }
    </style>
    """, unsafe_allow_html=True)

def create_stat_card(icon, title, value, color="blue"):
    """Create a statistics card with dark theme compatibility"""
    colors = {
        "blue": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "green": "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)",
        "orange": "linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)",
        "purple": "linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)"
    }
    
    return f"""
    <div style="
        background: var(--background-color, rgba(255, 255, 255, 0.05));
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        border: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
        text-align: center;
        transition: all 0.3s ease;
        margin-bottom: 1rem;
        backdrop-filter: blur(10px);
    ">
        <div style="
            background: {colors.get(color, colors['blue'])};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2rem;
            margin-bottom: 0.5rem;
        ">{icon}</div>
        <div style="
            font-size: 0.875rem;
            color: var(--text-color-secondary, #8b949e);
            font-weight: 500;
            margin-bottom: 0.25rem;
        ">{title}</div>
        <div style="
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text-color, #e6edf3);
        ">{value}</div>
    </div>
    """

def main():
    st.set_page_config(
        page_title="✨ README Generator Pro",
        page_icon="📝",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Add custom CSS
    add_custom_css()
    


    # With this:
    st.markdown("""
    <div class="fade-in">
        <h1 class="main-header">
            <span class="header-emoji">✨</span>
            <span class="header-text">README Generator Pro</span>
        </h1>
        <p class="main-subtitle">Generate comprehensive, professional README files for your projects using AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    init_session_state()
    
    # Check if Gemini API is configured
    if not configure_gemini():
        st.stop()
    
    # Statistics Row
    if st.session_state.file_contents or st.session_state.readme_generated:
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        with col_stat1:
            st.markdown(create_stat_card("📁", "Files Uploaded", len(st.session_state.file_contents), "blue"), unsafe_allow_html=True)
        
        with col_stat2:
            total_chars = sum(len(content) for content in st.session_state.file_contents.values())
            st.markdown(create_stat_card("📊", "Total Characters", f"{total_chars:,}", "green"), unsafe_allow_html=True)
        
        with col_stat3:
            readme_length = len(st.session_state.readme_generated) if st.session_state.readme_generated else 0
            st.markdown(create_stat_card("📝", "README Length", f"{readme_length:,}", "orange"), unsafe_allow_html=True)
        
        with col_stat4:
            status = "Generated ✅" if st.session_state.readme_generated else "Pending ⏳"
            st.markdown(create_stat_card("🎯", "Status", status, "purple"), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Create two columns for better layout
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        # Input Section Card
        st.markdown("""
        <div class="custom-card fade-in">
            <div class="section-header">
                <span class="section-icon">🚀</span>
                Project Input
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Project description input
        st.markdown("### 📝 Project Description")
        raw_prompt = st.text_area(
            "Tell us about your project:",
            placeholder="🎯 Describe your project's purpose, key features, technologies used, and any specific requirements.\n\nExample:\n• What problem does it solve?\n• What technologies are you using?\n• What are the main features?\n• Who is the target audience?",
            height=200,
            key=f"raw_prompt_input_{st.session_state.reset_counter}",
            help="Provide as much detail as possible for a better README"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # File upload section
        st.markdown("### 📁 Upload Project Files")
        st.markdown("*Optional: Upload your project files to generate more accurate documentation*")
        
        uploaded_files = st.file_uploader(
            "Drag and drop your files here or click to browse",
            type=["py", "txt", "md", "json", "yaml", "yml", "html", "css", "js", 
                "xml", "csv", "toml", "ini", "sh", "bat", "ps1", "sql", "log",
                "gitignore", "dockerfile", "makefile", "requirements"],
            accept_multiple_files=True,
            key=f"file_uploader_{st.session_state.reset_counter}",
            help="Supported formats: Python, Config files, Documentation, Scripts, and more"
        )
        
        # Process uploaded files with enhanced UI
        if uploaded_files:
            st.session_state.file_contents = {}
            
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, uploaded_file in enumerate(uploaded_files):
                # Update progress
                progress = (i + 1) / len(uploaded_files)
                progress_bar.progress(progress)
                status_text.text(f"Processing {uploaded_file.name}... ({i+1}/{len(uploaded_files)})")
                
                content = read_file_content(uploaded_file)
                st.session_state.file_contents[uploaded_file.name] = content
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Enhanced file preview
            with st.expander(f"📂 File Preview ({len(uploaded_files)} files processed)", expanded=False):
                tabs = st.tabs([f"📄 {file.name}" for file in uploaded_files[:5]])  # Limit to 5 tabs
                
                for i, (tab, uploaded_file) in enumerate(zip(tabs, uploaded_files[:5])):
                    with tab:
                        content = st.session_state.file_contents[uploaded_file.name]
                        if content.startswith("[Binary file:") or content.startswith("[Error reading"):
                            st.info(content)
                        else:
                            # Determine file type for syntax highlighting
                            file_ext = uploaded_file.name.split('.')[-1].lower()
                            lang_map = {
                                'py': 'python', 'js': 'javascript', 'html': 'html',
                                'css': 'css', 'json': 'json', 'yaml': 'yaml',
                                'yml': 'yaml', 'sh': 'bash', 'sql': 'sql'
                            }
                            
                            preview = content[:1000] + "\n\n... (truncated)" if len(content) > 1000 else content
                            st.code(preview, language=lang_map.get(file_ext, 'text'))
                            
                            # File stats
                            st.caption(f"📊 {len(content)} characters • {len(content.splitlines())} lines")
            
            st.success(f"✅ Successfully processed {len(uploaded_files)} files!")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Generate README button with enhanced styling
        generate_col1, generate_col2 = st.columns([3, 1])
        
        with generate_col1:
            generate_clicked = st.button(
                "🚀 Generate Professional README",
                type="primary",
                disabled=not raw_prompt.strip(),
                use_container_width=True,
                help="Click to generate your README based on the project description and uploaded files"
            )
        
        with generate_col2:
            if st.button("🔄 Reset", type="secondary", use_container_width=True):
                # Increment reset counter to force widget reset
                st.session_state.reset_counter += 1
                
                # Clear specific session state values but keep reset_counter
                st.session_state.files_processed = False
                st.session_state.file_contents = {}
                st.session_state.chat_history = []
                st.session_state.readme_generated = ""
                st.session_state.raw_prompt = ""
                
                # Force a complete rerun
                st.rerun()
        
        # Generate README logic
        if generate_clicked:
            if raw_prompt.strip():
                with st.spinner("🤖 AI is crafting your professional README..."):
                    # Enhanced progress indication
                    progress_container = st.empty()
                    
                    with progress_container.container():
                        st.info("🔍 Analyzing your project...")
                        readme_content = generate_readme(raw_prompt, st.session_state.file_contents)
                    
                    progress_container.empty()
                    
                    if readme_content:
                        st.session_state.readme_generated = readme_content
                        st.success("🎉 README generated successfully!")
                        st.balloons()
                    else:
                        st.error("❌ Failed to generate README. Please try again.")
            else:
                st.warning("⚠️ Please enter a project description first")
    
    with col2:
        # Output Section Card
        st.markdown("""
        <div class="custom-card fade-in">
            <div class="section-header">
                <span class="section-icon">📄</span>
                Generated README
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.readme_generated:
            # Enhanced display mode selector
            st.markdown("### 👀 Preview Options")
            display_mode = st.radio(
                "Choose how to view your README:",
                ["🎨 Rendered Preview", "📝 Raw Markdown", "💻 Code View"],
                horizontal=True,
                help="Switch between different view modes for your generated README"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Enhanced action buttons row
            st.markdown("### 🛠️ Actions")
            col_copy, col_download, col_clear = st.columns(3)
            
            with col_copy:
                # Add the modern copy button
                copy_button_html = create_copy_button(st.session_state.readme_generated)
                st.components.v1.html(copy_button_html, height=80)
            
            with col_download:
                st.download_button(
                    label="📥 Download README.md",
                    data=st.session_state.readme_generated,
                    file_name="README.md",
                    mime="text/markdown",
                    use_container_width=True,
                    help="Download the generated README as a .md file"
                )
            
            with col_clear:
                if st.button("🗑️ Clear All", type="secondary", use_container_width=True):
                    st.session_state.readme_generated = ""
                    st.session_state.file_contents = {}
                    st.rerun()
            
            
            # Display the generated README based on selected mode
            if display_mode == "🎨 Rendered Preview":
                # Clean up the markdown content first
                cleaned_content = st.session_state.readme_generated.strip()
                
                # Fix common markdown rendering issues in Streamlit
                if cleaned_content.startswith("```markdown"):
                    cleaned_content = cleaned_content[11:]
                if cleaned_content.startswith("```"):
                    first_newline = cleaned_content.find('\n')
                    if first_newline != -1:
                        cleaned_content = cleaned_content[first_newline + 1:]
                if cleaned_content.endswith("```"):
                    cleaned_content = cleaned_content[:-3]
                
                # Enhanced container for rendered markdown

                
                # Display the cleaned markdown content
                st.markdown(cleaned_content, unsafe_allow_html=True)
                
            elif display_mode == "📝 Raw Markdown":
                st.markdown("#### Raw Markdown Content")
                st.text_area(
                    "Copy this content to your README.md file:",
                    value=st.session_state.readme_generated,
                    height=600,
                    key="raw_markdown_display",
                    help="This is the raw markdown that you can copy and paste"
                )
                
            else:  # Code View
                st.markdown("#### Code Block View")
                st.code(st.session_state.readme_generated, language="markdown")
            
            # Additional stats for generated README
            st.markdown("<br>", unsafe_allow_html=True)
            readme_stats_col1, readme_stats_col2, readme_stats_col3 = st.columns(3)
            
            with readme_stats_col1:
                lines = len(st.session_state.readme_generated.splitlines())
                st.metric("📏 Lines", lines, help="Total number of lines in README")
            
            with readme_stats_col2:
                words = len(st.session_state.readme_generated.split())
                st.metric("📝 Words", words, help="Total word count")
            
            with readme_stats_col3:
                chars = len(st.session_state.readme_generated)
                st.metric("🔤 Characters", chars, help="Total character count")
                
        else:
            # Enhanced empty state
            st.markdown("""
            <div style="
                text-align: center;
                padding: 4rem 2rem;
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                border-radius: 20px;
                border: 2px dashed #cbd5e0;
                margin: 2rem 0;
            ">
                <div style="font-size: 4rem; margin-bottom: 1rem;">📝</div>
                <h3 style="color: #4a5568; margin-bottom: 1rem;">Ready to Generate!</h3>
                <p style="color: #718096; font-size: 1.1rem; line-height: 1.6;">
                    👈 Enter your project description and optionally upload files,<br>
                    then click <strong>'Generate Professional README'</strong> to create<br>
                    a comprehensive documentation for your project.
                </p>
                <div style="margin-top: 2rem;">
                    <div style="
                        display: inline-flex;
                        align-items: center;
                        gap: 1rem;
                        background: white;
                        padding: 1rem 2rem;
                        border-radius: 12px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                        border: 1px solid #e2e8f0;
                    ">
                        <span style="font-size: 1.5rem;">🚀</span>
                        <span style="color: #4a5568; font-weight: 500;">AI-Powered • Professional • Comprehensive</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Enhanced Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 16px;
        margin-top: 3rem;
        border: 1px solid rgba(229, 231, 235, 0.8);
    ">
        <div style="
            font-size: 1.5rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 600;
            margin-bottom: 0.5rem;
        ">
            ✨ README Generator Pro
        </div>
        <p style="color: #6b7280; font-size: 0.9rem; margin: 0;">
            Powered by AI • Built with ❤️ • Create professional documentation in seconds
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()