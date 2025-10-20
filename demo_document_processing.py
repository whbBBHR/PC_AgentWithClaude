#!/usr/bin/env python3
"""
Document Processing Demo - Claude Sonnet 4.5 Powered
Demonstrates all features of the AI document processing system
"""

from document_processor import DocumentProcessor, SummaryStyle, RewriteStyle
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
import time

console = Console()

def demo_document_processing():
    """Comprehensive demonstration of document processing features"""
    
    console.print(Panel.fit(
        "🚀 Document Processing System Demo\n"
        "Powered by Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)",
        style="bold green"
    ))
    
    # Initialize processor
    console.print("\n📚 Initializing Document Processor...")
    processor = DocumentProcessor()
    
    # Demo 1: Document Summarization
    console.print("\n" + "="*60)
    console.print("📄 DEMO 1: Document Summarization")
    console.print("="*60)
    
    # Load our test document
    document = processor.load_document('test_document.txt')
    console.print(f"📖 Loaded: {document['file_name']} ({document['word_count']} words)")
    
    # Test different summary styles
    styles_to_test = [
        (SummaryStyle.EXECUTIVE, "medium"),
        (SummaryStyle.BULLET, "short"),
        (SummaryStyle.ACADEMIC, "medium")
    ]
    
    for style, length in track(styles_to_test, description="Testing summary styles..."):
        console.print(f"\n🔍 Testing {style.value.title()} Summary ({length} length)")
        result = processor.summarize_document(document, style, length)
        
        # Show preview
        preview = result['summary'][:200] + "..." if len(result['summary']) > 200 else result['summary']
        console.print(Panel(preview, title=f"{style.value.title()} Summary Preview", style="cyan"))
        console.print(f"📊 Compression: {result['compression_ratio']:.1%} ({result['word_count_summary']} words)")
        time.sleep(1)
    
    # Demo 2: Document Rewriting
    console.print("\n" + "="*60)
    console.print("✍️ DEMO 2: Document Rewriting")
    console.print("="*60)
    
    # Create a smaller sample for rewriting
    sample_text = """
    Artificial Intelligence has become really important in our world today. 
    It's used in lots of different areas and is changing how we do things. 
    AI can help solve problems and make tasks easier for people.
    """
    
    sample_doc = {
        'file_path': 'sample.txt',
        'file_name': 'sample.txt',
        'content': sample_text.strip(),
        'type': document['type'],
        'word_count': len(sample_text.split()),
        'char_count': len(sample_text),
        'loaded_at': document['loaded_at']
    }
    
    # Test different rewriting styles
    rewrite_styles = [RewriteStyle.PROFESSIONAL, RewriteStyle.ACADEMIC, RewriteStyle.CASUAL]
    
    for style in track(rewrite_styles, description="Testing rewrite styles..."):
        console.print(f"\n✨ Testing {style.value.title()} Rewriting")
        result = processor.rewrite_document(sample_doc, style, f"Rewrite in {style.value} style")
        
        console.print(Panel(
            f"**Original ({sample_doc['word_count']} words):**\n{sample_doc['content']}\n\n"
            f"**{style.value.title()} Style ({len(result['rewritten_content'].split())} words):**\n{result['rewritten_content'][:300]}...",
            title=f"{style.value.title()} Rewrite Comparison",
            style="magenta"
        ))
        time.sleep(1)
    
    # Demo 3: Multi-Document Analysis
    console.print("\n" + "="*60)
    console.print("🔍 DEMO 3: Multi-Document Analysis")
    console.print("="*60)
    
    # Load both test documents
    doc1 = processor.load_document('test_document.txt')
    doc2 = processor.load_document('test_document2.txt')
    
    console.print(f"📚 Analyzing documents:")
    console.print(f"  • {doc1['file_name']} ({doc1['word_count']} words)")
    console.print(f"  • {doc2['file_name']} ({doc2['word_count']} words)")
    
    # Test different analysis types
    analysis_types = ['comparison', 'synthesis', 'themes']
    
    for analysis_type in track(analysis_types, description="Running multi-document analysis..."):
        console.print(f"\n🔬 {analysis_type.title()} Analysis")
        result = processor.analyze_multiple_documents([doc1, doc2], analysis_type)
        
        preview = result['analysis'][:300] + "..." if len(result['analysis']) > 300 else result['analysis']
        console.print(Panel(preview, title=f"{analysis_type.title()} Analysis Preview", style="yellow"))
        time.sleep(1)
    
    # Demo 4: File Browser Feature
    console.print("\n" + "="*60)
    console.print("📁 DEMO 4: File Browser Feature")
    console.print("="*60)
    
    console.print("📂 The document processor includes an interactive file browser!")
    console.print("   • Navigate directories with arrow keys or numbers")
    console.print("   • Preview file sizes and types")
    console.print("   • Support for .txt, .md, .pdf, .docx files")
    console.print("   • Easy selection with confirmation")
    
    console.print("\n🎯 To try the file browser, run:")
    console.print("   python document_processor.py")
    console.print("   Then select option 1 or 2 and choose 'Browse for file'")
    
    # Demo Summary
    console.print("\n" + "="*60)
    console.print("✅ DEMO COMPLETE - Feature Summary")
    console.print("="*60)
    
    features = [
        "📄 Document Summarization (6 styles: brief, executive, bullet, detailed, academic, narrative)",
        "✍️ Document Rewriting (5 styles: professional, academic, casual, technical, creative)",
        "🔍 Multi-Document Analysis (comparison, synthesis, themes, summary)",
        "📁 Interactive File Browser with directory navigation",
        "💾 Results saving in JSON and Markdown formats",
        "🎨 Rich console interface with progress indicators",
        "📊 Detailed statistics and compression ratios",
        "🔧 Support for multiple file formats (.txt, .md, .pdf, .docx)",
        "🤖 Powered by Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)",
        "⚡ Fast processing with intelligent caching"
    ]
    
    for feature in features:
        console.print(f"  ✅ {feature}")
    
    console.print(Panel.fit(
        "🎉 Document Processing System Ready!\n"
        "Use 'python document_processor.py' for interactive mode\n"
        "Or import DocumentProcessor class for programmatic use",
        style="bold blue"
    ))

if __name__ == "__main__":
    demo_document_processing()