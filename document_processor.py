#!/usr/bin/env python3
"""
Document Processor - AI-Powered Document Rewriting & Summarization
Powered by Claude Sonnet 4.5 (claude-sonnet-4-5-20250929) for intelligent text processing

Features:
- Document summarization (various lengths and styles)
- Text rewriting (tone, style, clarity improvements)
- Format conversion (markdown, plain text, structured)
- Multi-document analysis and synthesis
- Academic and business document processing
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax

# Import our Claude client
try:
    from src.pc_agent.claude_client import ClaudeClient
except ImportError:
    print("❌ Could not import ClaudeClient. Make sure the project is set up correctly.")
    sys.exit(1)

console = Console()

class DocumentType(Enum):
    """Supported document types"""
    TEXT = "text"
    MARKDOWN = "markdown" 
    PDF = "pdf"
    WORD = "word"
    HTML = "html"
    EMAIL = "email"
    ACADEMIC = "academic"
    BUSINESS = "business"
    TECHNICAL = "technical"

class SummaryStyle(Enum):
    """Summary style options"""
    BRIEF = "brief"           # 1-2 sentences
    EXECUTIVE = "executive"   # Executive summary format
    BULLET = "bullet"         # Bullet point format  
    DETAILED = "detailed"     # Comprehensive summary
    ACADEMIC = "academic"     # Academic abstract style
    NARRATIVE = "narrative"   # Story-like summary

class RewriteStyle(Enum):
    """Rewrite style options"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    ACADEMIC = "academic"
    TECHNICAL = "technical"
    CREATIVE = "creative"
    PERSUASIVE = "persuasive"
    CONCISE = "concise"
    DETAILED = "detailed"

class DocumentProcessor:
    """Main document processing class powered by Claude Sonnet 4.5"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize with Claude Sonnet 4.5 client"""
        self.config = config or {}
        self.claude = None
        self.results_dir = Path("document_results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Initialize Claude client with Sonnet 4.5
        try:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment")
            
            self.claude = ClaudeClient(api_key=api_key, config={
                'claude_model': 'claude-sonnet-4-5-20250929',  # Claude Sonnet 4.5
                'max_tokens': 8192,
                'temperature': 0.3
            })
            
            console.print("✅ Claude Sonnet 4.5 initialized for document processing")
            
        except Exception as e:
            console.print(f"❌ Failed to initialize Claude: {e}")
            raise
    
    def browse_and_select_document(self, start_path: str = ".") -> Optional[Path]:
        """Interactive file browser for document selection"""
        current_path = Path(start_path).resolve()
        
        while True:
            console.clear()
            console.print(Panel.fit(
                f"📁 Document Browser - Claude Sonnet 4.5 Document Processor\n"
                f"Current Directory: {current_path}",
                style="bold blue"
            ))
            
            # Get files and directories
            try:
                items = []
                
                # Add parent directory option (unless at root)
                if current_path.parent != current_path:
                    items.append(("📁 ..", "directory", current_path.parent))
                
                # Get directories and files
                for item in sorted(current_path.iterdir()):
                    if item.is_dir():
                        items.append((f"📁 {item.name}/", "directory", item))
                    elif item.suffix.lower() in ['.txt', '.md', '.pdf', '.docx', '.doc']:
                        size = item.stat().st_size
                        size_str = f"{size:,} bytes" if size < 1024 else f"{size//1024:,} KB"
                        items.append((f"📄 {item.name} ({size_str})", "file", item))
                
                # Display items in a table
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("#", style="dim", width=4)
                table.add_column("Name", style="green")
                table.add_column("Type", style="blue")
                
                for i, (display_name, item_type, path) in enumerate(items, 1):
                    table.add_row(str(i), display_name, item_type.title())
                
                if not items:
                    console.print("[yellow]No accessible files or directories found in this location.[/yellow]")
                else:
                    console.print(table)
                
                console.print("\n[bold]Options:[/bold]")
                console.print("• Enter number to select item")
                console.print("• 'q' or 'quit' to exit")
                console.print("• 'r' or 'refresh' to refresh current directory")
                if current_path != Path.cwd():
                    console.print("• 'h' or 'home' to go to working directory")
                
                choice = Prompt.ask("\nSelect an option", default="q").strip().lower()
                
                if choice in ['q', 'quit']:
                    return None
                elif choice in ['r', 'refresh']:
                    continue
                elif choice in ['h', 'home']:
                    current_path = Path.cwd()
                    continue
                
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(items):
                        _, item_type, selected_path = items[choice_num - 1]
                        
                        if item_type == "directory":
                            current_path = selected_path
                        elif item_type == "file":
                            # Confirm selection
                            if Confirm.ask(f"\nSelect document: {selected_path.name}?"):
                                console.print(f"✅ Selected: {selected_path}")
                                return selected_path
                    else:
                        console.print(f"[red]Invalid choice: {choice_num}. Please select 1-{len(items)}[/red]")
                        time.sleep(1)
                except ValueError:
                    console.print(f"[red]Invalid input: '{choice}'. Please enter a number, 'q', 'r', or 'h'[/red]")
                    time.sleep(1)
                    
            except PermissionError:
                console.print(f"[red]Permission denied accessing: {current_path}[/red]")
                current_path = current_path.parent
                time.sleep(1)
            except Exception as e:
                console.print(f"[red]Error browsing directory: {e}[/red]")
                time.sleep(1)
    
    def load_document(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Load document from file with content detection"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")
        
        console.print(f"📄 Loading document: {file_path.name}")
        
        # Detect file type and load content
        suffix = file_path.suffix.lower()
        
        if suffix in ['.txt', '.md', '.py', '.js', '.html', '.css']:
            # Text-based files
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            doc_type = DocumentType.MARKDOWN if suffix == '.md' else DocumentType.TEXT
            
        elif suffix == '.pdf':
            # PDF processing (requires PyPDF2 or similar)
            try:
                import PyPDF2
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    content = ""
                    for page in pdf_reader.pages:
                        content += page.extract_text() + "\n"
                doc_type = DocumentType.PDF
            except ImportError:
                console.print("⚠️ PDF processing requires PyPDF2. Install with: pip install PyPDF2")
                raise
                
        elif suffix in ['.doc', '.docx']:
            # Word document processing (requires python-docx)
            try:
                from docx import Document
                doc = Document(file_path)
                content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                doc_type = DocumentType.WORD
            except ImportError:
                console.print("⚠️ Word processing requires python-docx. Install with: pip install python-docx")
                raise
        else:
            # Fallback to text
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            doc_type = DocumentType.TEXT
        
        # Analyze document structure
        word_count = len(content.split())
        char_count = len(content)
        
        document_info = {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'content': content,
            'type': doc_type,
            'word_count': word_count,
            'char_count': char_count,
            'loaded_at': datetime.now().isoformat()
        }
        
        console.print(f"✅ Document loaded: {word_count} words, {char_count} characters")
        return document_info
    
    def summarize_document(self, 
                          document: Dict[str, Any], 
                          style: SummaryStyle = SummaryStyle.EXECUTIVE,
                          target_length: str = "medium") -> Dict[str, Any]:
        """Summarize document using Claude Sonnet 4.5"""
        
        console.print(Panel.fit(
            f"📝 Document Summarization with Claude Sonnet 4.5\n"
            f"Style: {style.value.title()} | Length: {target_length}",
            style="bold cyan"
        ))
        
        content = document['content']
        
        # Build prompt based on style
        style_prompts = {
            SummaryStyle.BRIEF: "Provide a brief 1-2 sentence summary of the key point.",
            SummaryStyle.EXECUTIVE: "Create an executive summary highlighting main findings, conclusions, and actionable insights.",
            SummaryStyle.BULLET: "Summarize using clear bullet points for each major topic or section.",
            SummaryStyle.DETAILED: "Provide a comprehensive summary covering all important aspects and details.",
            SummaryStyle.ACADEMIC: "Write an academic abstract summarizing methodology, findings, and significance.",
            SummaryStyle.NARRATIVE: "Create a narrative summary that tells the story and flow of the content."
        }
        
        length_guidance = {
            "short": "Keep the summary concise (100-200 words).",
            "medium": "Provide a moderate-length summary (200-400 words).",
            "long": "Create a detailed summary (400-600 words).",
            "comprehensive": "Provide an extensive summary covering all aspects."
        }
        
        prompt = f"""
        Please create a {style.value} summary of the following document. {length_guidance.get(target_length, length_guidance['medium'])}

        {style_prompts[style]}

        Document content:
        {content}

        Provide only the summary text without any additional formatting or instructions.
        """
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating summary with Claude Sonnet 4.5...", total=None)
            
            try:
                response = self.claude.generate_response(prompt, max_tokens=1500)
                summary = response.strip()
                progress.remove_task(task)
                
            except Exception as e:
                progress.remove_task(task)
                console.print(f"❌ Summarization failed: {e}")
                raise
        
        # Prepare result
        result = {
            'original_document': document,
            'summary': summary,
            'style': style.value,
            'target_length': target_length,
            'generated_at': datetime.now().isoformat(),
            'word_count_original': document['word_count'],
            'word_count_summary': len(summary.split()),
            'compression_ratio': len(summary.split()) / document['word_count']
        }
        
        console.print(f"✅ Summary generated: {len(summary.split())} words "
                     f"({result['compression_ratio']:.1%} of original)")
        
        return result
    
    def rewrite_document(self, 
                        document: Dict[str, Any],
                        style: RewriteStyle = RewriteStyle.PROFESSIONAL,
                        instructions: str = "") -> Dict[str, Any]:
        """Rewrite document using Claude Sonnet 4.5"""
        
        console.print(Panel.fit(
            f"✍️ Document Rewriting with Claude Sonnet 4.5\n"
            f"Style: {style.value.title()}" + (f"\nInstructions: {instructions}" if instructions else ""),
            style="bold green"
        ))
        
        content = document['content']
        
        # Style-specific instructions
        style_instructions = {
            RewriteStyle.PROFESSIONAL: "Rewrite in a professional, business-appropriate tone with clear, formal language.",
            RewriteStyle.CASUAL: "Rewrite in a conversational, friendly tone that's easy to read and relatable.",
            RewriteStyle.ACADEMIC: "Rewrite in academic style with scholarly language, proper citations format, and analytical tone.",
            RewriteStyle.TECHNICAL: "Rewrite with precise technical language, clear explanations, and structured presentation.",
            RewriteStyle.CREATIVE: "Rewrite with engaging, creative language that captures attention and maintains interest.",
            RewriteStyle.PERSUASIVE: "Rewrite to be more compelling and persuasive, with stronger arguments and calls to action.",
            RewriteStyle.CONCISE: "Rewrite to be more concise while maintaining all key information and clarity.",
            RewriteStyle.DETAILED: "Expand and elaborate on the content with more examples, explanations, and detail."
        }
        
        prompt = f"""
        Please rewrite the following document using Claude Sonnet 4.5's advanced language processing capabilities:

        ORIGINAL DOCUMENT:
        {content}

        REWRITING INSTRUCTIONS:
        - Style: {style_instructions[style]}
        - Maintain all key information and main points
        - Improve clarity, flow, and readability
        - Preserve the document's structure and organization
        - Enhance language quality and engagement
        {f"- Additional instructions: {instructions}" if instructions else ""}

        Please provide a complete rewrite that improves upon the original while maintaining its core message and intent.
        """
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Rewriting document with Claude Sonnet 4.5...", total=None)
            
            try:
                response = self.claude.generate_response(prompt, max_tokens=2000)
                rewritten = response.strip()
                progress.remove_task(task)
                
            except Exception as e:
                progress.remove_task(task)
                console.print(f"❌ Rewriting failed: {e}")
                raise
        
        # Prepare result
        result = {
            'original_document': document,
            'rewritten_content': rewritten,
            'style': style.value,
            'instructions': instructions,
            'generated_at': datetime.now().isoformat(),
            'word_count_original': document['word_count'],
            'word_count_rewritten': len(rewritten.split()),
            'length_change': len(rewritten.split()) - document['word_count']
        }
        
        console.print(f"✅ Document rewritten: {len(rewritten.split())} words "
                     f"({result['length_change']:+d} word change)")
        
        return result
    
    def analyze_multiple_documents(self, documents: List[Dict[str, Any]], 
                                  analysis_type: str = "comparison") -> Dict[str, Any]:
        """Analyze multiple documents together using Claude Sonnet 4.5"""
        
        console.print(Panel.fit(
            f"🔍 Multi-Document Analysis with Claude Sonnet 4.5\n"
            f"Documents: {len(documents)} | Type: {analysis_type}",
            style="bold magenta"
        ))
        
        # Combine documents for analysis
        combined_content = ""
        for i, doc in enumerate(documents, 1):
            combined_content += f"\n\nDOCUMENT {i}: {doc['file_name']}\n"
            combined_content += "=" * 50 + "\n"
            combined_content += doc['content']
        
        analysis_prompts = {
            "comparison": "Compare and contrast these documents, highlighting similarities, differences, and unique aspects of each.",
            "synthesis": "Synthesize the information from all documents into a coherent unified analysis.",
            "themes": "Identify common themes, patterns, and key insights across all documents.",
            "summary": "Provide a comprehensive summary that incorporates information from all documents."
        }
        
        prompt = f"""
        Please analyze the following multiple documents using Claude Sonnet 4.5's advanced analytical capabilities:

        {combined_content}

        ANALYSIS INSTRUCTIONS:
        - Type: {analysis_prompts.get(analysis_type, analysis_prompts['comparison'])}
        - Identify relationships and connections between documents
        - Highlight key insights that emerge from the collective analysis
        - Provide structured, clear analysis with specific examples
        - Note any contradictions or conflicting information

        Please provide a thorough multi-document analysis.
        """
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Analyzing documents with Claude Sonnet 4.5...", total=None)
            
            try:
                response = self.claude.generate_response(prompt, max_tokens=3000)
                analysis = response.strip()
                progress.remove_task(task)
                
            except Exception as e:
                progress.remove_task(task)
                console.print(f"❌ Analysis failed: {e}")
                raise
        
        result = {
            'documents': documents,
            'analysis': analysis,
            'analysis_type': analysis_type,
            'generated_at': datetime.now().isoformat(),
            'document_count': len(documents),
            'total_words': sum(doc['word_count'] for doc in documents)
        }
        
        console.print(f"✅ Multi-document analysis complete: {len(documents)} documents analyzed")
        return result
    
    def save_result(self, result: Dict[str, Any], output_name: str = None) -> str:
        """Save processing result to file"""
        if not output_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"document_result_{timestamp}"
        
        output_path = self.results_dir / f"{output_name}.json"
        
        # Convert enum values to strings for JSON serialization
        def convert_enums(obj):
            if hasattr(obj, 'value'):  # Enum
                return obj.value
            elif isinstance(obj, dict):
                return {k: convert_enums(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_enums(item) for item in obj]
            else:
                return obj
        
        json_safe_result = convert_enums(result)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_safe_result, f, indent=2, ensure_ascii=False)
        
        # Also save human-readable version
        readable_path = self.results_dir / f"{output_name}.md"
        with open(readable_path, 'w', encoding='utf-8') as f:
            f.write(f"# Document Processing Result\n\n")
            f.write(f"**Generated:** {result.get('generated_at', 'Unknown')}\n\n")
            
            if 'summary' in result:
                f.write(f"## Summary\n\n{result['summary']}\n\n")
            
            if 'rewritten_content' in result:
                f.write(f"## Rewritten Content\n\n{result['rewritten_content']}\n\n")
            
            if 'analysis' in result:
                f.write(f"## Analysis\n\n{result['analysis']}\n\n")
        
        console.print(f"💾 Results saved: {output_path}")
        console.print(f"📄 Readable version: {readable_path}")
        
        return str(output_path)

def interactive_document_processor():
    """Interactive CLI for document processing"""
    console.print(Panel.fit(
        "📚 Document Processor - Claude Sonnet 4.5 Powered\n"
        "AI Document Rewriting & Summarization System",
        style="bold blue"
    ))
    
    try:
        processor = DocumentProcessor()
    except Exception as e:
        console.print(f"❌ Failed to initialize processor: {e}")
        return
    
    while True:
        console.print("\n" + "="*60)
        console.print("🔹 Document Processing Options:")
        console.print("1. 📄 Summarize Document")
        console.print("2. ✍️  Rewrite Document") 
        console.print("3. 🔍 Analyze Multiple Documents")
        console.print("4. 📁 View Results")
        console.print("5. ❌ Exit")
        
        choice = Prompt.ask("\n➤ Choose option", choices=["1", "2", "3", "4", "5"])
        
        if choice == "1":
            # Document summarization
            console.print("\n🔹 Select document to summarize:")
            console.print("1. 📝 Enter file path manually")
            console.print("2. 📁 Browse for file")
            
            path_choice = Prompt.ask("Choose method", choices=["1", "2"], default="2")
            
            if path_choice == "1":
                file_path = Prompt.ask("📂 Enter document path")
            else:
                selected_path = processor.browse_and_select_document()
                if not selected_path:
                    console.print("❌ No file selected")
                    continue
                file_path = str(selected_path)
            
            try:
                document = processor.load_document(file_path)
                
                # Get summary style
                styles = [s.value for s in SummaryStyle]
                style_choice = Prompt.ask("📝 Summary style", choices=styles, default="executive")
                style = SummaryStyle(style_choice)
                
                length = Prompt.ask("📏 Target length", choices=["short", "medium", "long"], default="medium")
                
                result = processor.summarize_document(document, style, length)
                
                # Display result
                console.print(Panel(result['summary'], title="📝 Summary", style="green"))
                
                if Confirm.ask("💾 Save result?"):
                    processor.save_result(result, f"summary_{document['file_name']}")
                    
            except Exception as e:
                console.print(f"❌ Error: {e}")
        
        elif choice == "2":
            # Document rewriting
            console.print("\n🔹 Select document to rewrite:")
            console.print("1. 📝 Enter file path manually")
            console.print("2. 📁 Browse for file")
            
            path_choice = Prompt.ask("Choose method", choices=["1", "2"], default="2")
            
            if path_choice == "1":
                file_path = Prompt.ask("📂 Enter document path")
            else:
                selected_path = processor.browse_and_select_document()
                if not selected_path:
                    console.print("❌ No file selected")
                    continue
                file_path = str(selected_path)
            
            try:
                document = processor.load_document(file_path)
                
                # Get rewrite style
                styles = [s.value for s in RewriteStyle]
                style_choice = Prompt.ask("✍️  Rewrite style", choices=styles, default="professional")
                style = RewriteStyle(style_choice)
                
                instructions = Prompt.ask("📋 Additional instructions (optional)", default="")
                
                result = processor.rewrite_document(document, style, instructions)
                
                # Display result (truncated)
                preview = result['rewritten_content'][:500] + "..." if len(result['rewritten_content']) > 500 else result['rewritten_content']
                console.print(Panel(preview, title="✍️ Rewritten Content (Preview)", style="cyan"))
                
                if Confirm.ask("💾 Save result?"):
                    processor.save_result(result, f"rewrite_{document['file_name']}")
                    
            except Exception as e:
                console.print(f"❌ Error: {e}")
        
        elif choice == "3":
            # Multiple document analysis
            console.print("\n� Select documents for analysis:")
            console.print("You can add multiple documents using browse or manual entry")
            
            documents = []
            while True:
                if documents:
                    console.print(f"\n📚 Currently selected: {len(documents)} documents")
                    for i, doc in enumerate(documents, 1):
                        console.print(f"  {i}. {doc['file_name']}")
                
                console.print("\n🔹 Add document:")
                console.print("1. 📝 Enter file path manually")
                console.print("2. 📁 Browse for file")
                console.print("3. ✅ Finish and analyze")
                if documents:
                    console.print("4. 🗑️  Remove last document")
                
                add_choice = Prompt.ask("Choose option", 
                                      choices=["1", "2", "3", "4"] if documents else ["1", "2", "3"], 
                                      default="2")
                
                if add_choice == "1":
                    path = Prompt.ask("📂 Enter document path")
                    if path:
                        try:
                            doc = processor.load_document(path)
                            documents.append(doc)
                        except Exception as e:
                            console.print(f"❌ Error loading {path}: {e}")
                
                elif add_choice == "2":
                    selected_path = processor.browse_and_select_document()
                    if selected_path:
                        try:
                            doc = processor.load_document(str(selected_path))
                            documents.append(doc)
                        except Exception as e:
                            console.print(f"❌ Error loading {selected_path}: {e}")
                
                elif add_choice == "3":
                    if not documents:
                        console.print("❌ Please add at least one document")
                        continue
                    break
                
                elif add_choice == "4" and documents:
                    removed = documents.pop()
                    console.print(f"🗑️ Removed: {removed['file_name']}")
            
            if documents:
                analysis_type = Prompt.ask(
                    "🔍 Analysis type", 
                    choices=["comparison", "synthesis", "themes", "summary"], 
                    default="comparison"
                )
                
                try:
                    result = processor.analyze_multiple_documents(documents, analysis_type)
                    
                    # Display result (truncated)
                    preview = result['analysis'][:500] + "..." if len(result['analysis']) > 500 else result['analysis']
                    console.print(Panel(preview, title="🔍 Analysis (Preview)", style="magenta"))
                    
                    if Confirm.ask("💾 Save result?"):
                        processor.save_result(result, f"analysis_{analysis_type}")
                        
                except Exception as e:
                    console.print(f"❌ Error: {e}")
            else:
                console.print("❌ Need at least 2 documents for analysis")
        
        elif choice == "4":
            # View results
            results_files = list(processor.results_dir.glob("*.md"))
            if results_files:
                console.print(f"📁 Found {len(results_files)} result files:")
                for file in results_files[-5:]:  # Show last 5
                    console.print(f"   📄 {file.name}")
            else:
                console.print("📭 No results found")
        
        elif choice == "5":
            console.print("👋 Goodbye!")
            break

if __name__ == "__main__":
    interactive_document_processor()