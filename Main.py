import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pytesseract
from PIL import Image, ImageTk
from PIL.ExifTags import TAGS
import re
from collections import Counter
import requests
import json
import threading
import os
from datetime import datetime
from tkinterdnd2 import DND_FILES, TkinterDnD


class OCRTextExtractor:
    """OCRify - Advanced OCR Text Extractor with Analytics and Metadata Viewer"""
    
    def __init__(self, root):
        """Initialize OCRify application"""
        self.root = root
        self.root.title("OCRify - Advanced OCR Text Extractor & Image Analyzer")
        self.root.geometry("1600x1000")
        self.root.minsize(1200, 700)
        
        # Configure modern styling
        self._configure_styles()
        
        # Application variables
        self.image_path = None
        self.extracted_text = ""
        self.image_metadata = {}
        self.original_image = None
        self.recent_files = []
        self.settings = {"auto_extract": False, "save_results": True}
        
        # Setup drag and drop
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_file_drop)
        
        # Setup GUI
        self.setup_gui()
        
        # Setup keyboard shortcuts
        self.setup_shortcuts()
        
        # Load recent files
        self.load_recent_files()
        
        # Set initial focus
        self.root.focus_set()
    
    def _configure_styles(self):
        """Configure modern TTK styles with OCRify branding"""
        style = ttk.Style()
        
        # Use a modern theme as base
        try:
            style.theme_use('vista')  # Windows modern theme
        except:
            style.theme_use('clam')
        
        # OCRify color scheme - modern blue gradient theme
        self.colors = {
            'primary': '#2563eb',      # Modern blue
            'primary_dark': '#1d4ed8', # Darker blue
            'secondary': '#f1f5f9',    # Light gray
            'accent': '#06b6d4',       # Cyan accent
            'success': '#10b981',      # Green
            'warning': '#f59e0b',      # Amber
            'danger': '#ef4444',       # Red
            'bg_main': '#ffffff',      # White background
            'bg_secondary': '#f8fafc', # Light background
            'text_primary': '#1e293b', # Dark text
            'text_secondary': '#64748b', # Gray text
            'border': '#e2e8f0',      # Light border
            'gradient_start': '#3b82f6',
            'gradient_end': '#1e40af'
        }
        
        # Configure modern styles
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 24, 'bold'), 
                       foreground=self.colors['primary'])
        
        style.configure('Subtitle.TLabel', 
                       font=('Segoe UI', 12), 
                       foreground=self.colors['text_secondary'])
        
        style.configure('Heading.TLabel', 
                       font=('Segoe UI', 11, 'bold'), 
                       foreground=self.colors['text_primary'])
        
        style.configure('Modern.TButton', 
                       font=('Segoe UI', 10, 'bold'),
                       padding=(15, 8))
        
        style.map('Modern.TButton',
                 background=[('active', self.colors['primary_dark']),
                           ('!active', self.colors['primary'])],
                 foreground=[('active', 'black'),
                           ('!active', 'black')])
        
        style.configure('Success.TButton',
                       font=('Segoe UI', 10, 'bold'),
                       padding=(15, 8))
        
        style.map('Success.TButton',
                 background=[('active', '#059669'),
                           ('!active', self.colors['success'])],
                 foreground=[('active', 'black'),
                           ('!active', 'black')])
        
        style.configure('Status.TLabel', 
                       font=('Segoe UI', 9), 
                       foreground=self.colors['text_secondary'])
        
        # Configure root background
        self.root.configure(bg=self.colors['bg_main'])
        
    def setup_gui(self):
        """Setup the modern GUI interface with OCRify branding"""
        # Create main frame with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Header section with OCRify branding
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        header_frame.columnconfigure(1, weight=1)
        
        # OCRify logo/title
        title_frame = ttk.Frame(header_frame)
        title_frame.grid(row=0, column=0, sticky=tk.W)
        
        title_label = ttk.Label(title_frame, text="OCRify", style='Title.TLabel')
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        subtitle_label = ttk.Label(title_frame, 
                                 text="Advanced OCR Text Extraction & Image Analysis", 
                                 style='Subtitle.TLabel')
        subtitle_label.grid(row=1, column=0, sticky=tk.W)
        
        # Quick actions toolbar
        toolbar_frame = ttk.Frame(header_frame)
        toolbar_frame.grid(row=0, column=1, sticky=tk.E, padx=(20, 0))
        
        # Recent files menu button
        self.recent_btn = ttk.Menubutton(toolbar_frame, text="📁 Recent", style='Modern.TButton')
        self.recent_btn.grid(row=0, column=0, padx=(0, 5))
        self.recent_menu = tk.Menu(self.recent_btn, tearoff=0)
        self.recent_btn.configure(menu=self.recent_menu)
        
        # Settings button
        settings_btn = ttk.Button(toolbar_frame, text="⚙️ Settings", 
                                command=self.show_settings, style='Modern.TButton')
        settings_btn.grid(row=0, column=1, padx=(0, 5))
        
        # Help button
        help_btn = ttk.Button(toolbar_frame, text="❓ Help", 
                            command=self.show_help, style='Modern.TButton')
        help_btn.grid(row=0, column=2)
        
        # Progress bar (initially hidden)
        self.progress_frame = ttk.Frame(main_frame)
        self.progress_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        self.progress_frame.columnconfigure(1, weight=1)
        
        self.progress_label = ttk.Label(self.progress_frame, text="Processing...", 
                                      style='Status.TLabel')
        self.progress_label.grid(row=0, column=0, padx=(0, 10))
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        self.progress_frame.grid_remove()  # Hide initially
        
        # Main content area
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Left panel - Image viewer with modern styling
        left_panel = ttk.LabelFrame(content_frame, text="🖼️ Image Workspace", padding="15")
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 15))
        left_panel.rowconfigure(1, weight=1)
        left_panel.columnconfigure(0, weight=1)
        
        # Enhanced control buttons with tooltips
        controls_frame = ttk.Frame(left_panel)
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.load_btn = ttk.Button(controls_frame, text="📁 Load Image", 
                                 command=self.load_image, style='Modern.TButton')
        self.load_btn.grid(row=0, column=0, padx=(0, 8))
        self.create_tooltip(self.load_btn, "Load an image file for OCR processing (Ctrl+O)")
        
        self.extract_btn = ttk.Button(controls_frame, text="🔍 Extract Text", 
                                    command=self.extract_text, state='disabled',
                                    style='Success.TButton')
        self.extract_btn.grid(row=0, column=1, padx=(0, 8))
        self.create_tooltip(self.extract_btn, "Extract text from the loaded image (Ctrl+E)")
        
        self.metadata_btn = ttk.Button(controls_frame, text="📊 Metadata", 
                                     command=self.extract_metadata, state='disabled',
                                     style='Modern.TButton')
        self.metadata_btn.grid(row=0, column=2, padx=(0, 8))
        self.create_tooltip(self.metadata_btn, "Extract image metadata and EXIF data (Ctrl+M)")
        
        self.save_btn = ttk.Button(controls_frame, text="💾 Save Results", 
                                 command=self.save_results, state='disabled',
                                 style='Modern.TButton')
        self.save_btn.grid(row=0, column=3)
        self.create_tooltip(self.save_btn, "Save extracted text and metadata (Ctrl+S)")
        
        # Modern image display area with drag-and-drop
        image_container = ttk.Frame(left_panel, relief='solid', borderwidth=1)
        image_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        image_container.rowconfigure(0, weight=1)
        image_container.columnconfigure(0, weight=1)
        
        self.image_label = tk.Label(image_container, 
                                  text="🖼️  OCRify Image Workspace\n\n"
                                       "📁 Click 'Load Image' or drag & drop an image file here\n\n"
                                       "Supported formats: PNG, JPG, JPEG, GIF, BMP, TIFF", 
                                  bg=self.colors['bg_secondary'],
                                  fg=self.colors['text_secondary'],
                                  font=('Segoe UI', 12),
                                  relief='flat',
                                  bd=0)
        self.image_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=20, pady=20)
        
        # Configure drag and drop for image area
        self.image_label.drop_target_register(DND_FILES)
        self.image_label.dnd_bind('<<Drop>>', self.on_file_drop)
        
        # Right panel - Results with modern tabbed interface
        right_panel = ttk.LabelFrame(content_frame, text="📊 Analysis Results", padding="15")
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)
        
        # Enhanced notebook with modern styling
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Text extraction tab
        self.setup_text_tab()
        
        # Analytics tab
        self.setup_analytics_tab()
        
        # Metadata tab
        self.setup_metadata_tab()
        
        # Modern status bar
        self.setup_status_bar(main_frame)
    
    def setup_text_tab(self):
        """Setup the text extraction results tab"""
        text_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(text_frame, text="📝 Extracted Text")
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(1, weight=1)
        
        # Text controls
        text_controls = ttk.Frame(text_frame)
        text_controls.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(text_controls, text="Extracted Text:", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W)
        
        # Text action buttons
        text_actions = ttk.Frame(text_controls)
        text_actions.grid(row=0, column=1, sticky=tk.E)
        
        copy_btn = ttk.Button(text_actions, text="📋 Copy", command=self.copy_text)
        copy_btn.grid(row=0, column=0, padx=(0, 5))
        
        clear_btn = ttk.Button(text_actions, text="🗑️ Clear", command=self.clear_text)
        clear_btn.grid(row=0, column=1)
        
        # Enhanced text display
        self.text_display = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, 
                                                     height=25, font=('Consolas', 11),
                                                     bg='white', fg=self.colors['text_primary'],
                                                     selectbackground=self.colors['primary'],
                                                     selectforeground='white')
        self.text_display.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_controls.columnconfigure(1, weight=1)
    
    def setup_analytics_tab(self):
        """Setup the text analytics tab"""
        analytics_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(analytics_frame, text="📊 Analytics")
        analytics_frame.columnconfigure(0, weight=1)
        analytics_frame.rowconfigure(3, weight=1)
        
        # Analytics header with stats
        stats_frame = ttk.LabelFrame(analytics_frame, text="📈 Text Statistics", padding="10")
        stats_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        stats_frame.columnconfigure(3, weight=1)
        
        self.word_count_label = ttk.Label(stats_frame, text="Words: 0", style='Heading.TLabel')
        self.word_count_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        self.char_count_label = ttk.Label(stats_frame, text="Characters: 0", style='Heading.TLabel')
        self.char_count_label.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        self.line_count_label = ttk.Label(stats_frame, text="Lines: 0", style='Heading.TLabel')
        self.line_count_label.grid(row=0, column=2, sticky=tk.W)
        
        # Word frequency analysis
        freq_frame = ttk.LabelFrame(analytics_frame, text="🏆 Word Frequency Analysis", padding="10")
        freq_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        freq_frame.columnconfigure(0, weight=1)
        
        self.freq_words_text = scrolledtext.ScrolledText(freq_frame, height=8, wrap=tk.WORD,
                                                        font=('Consolas', 10))
        self.freq_words_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Unique word analysis
        unique_frame = ttk.LabelFrame(analytics_frame, text="🎯 Unique Word Discovery", padding="10")
        unique_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        unique_frame.columnconfigure(0, weight=1)
        
        self.unique_word_text = scrolledtext.ScrolledText(unique_frame, height=10, wrap=tk.WORD,
                                                         font=('Consolas', 10))
        self.unique_word_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def setup_metadata_tab(self):
        """Setup the image metadata tab"""
        metadata_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(metadata_frame, text="📋 Metadata")
        metadata_frame.columnconfigure(0, weight=1)
        metadata_frame.rowconfigure(1, weight=1)
        
        # Metadata controls
        metadata_controls = ttk.Frame(metadata_frame)
        metadata_controls.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        metadata_controls.columnconfigure(1, weight=1)
        
        ttk.Label(metadata_controls, text="Image Metadata & EXIF Data:", 
                 style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W)
        
        # Metadata actions
        metadata_actions = ttk.Frame(metadata_controls)
        metadata_actions.grid(row=0, column=1, sticky=tk.E)
        
        export_btn = ttk.Button(metadata_actions, text="📤 Export", command=self.export_metadata)
        export_btn.grid(row=0, column=0)
        
        self.metadata_display = scrolledtext.ScrolledText(metadata_frame, wrap=tk.WORD,
                                                         height=25, font=('Consolas', 10))
        self.metadata_display.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def setup_status_bar(self, parent):
        """Setup modern status bar with additional information"""
        status_frame = ttk.Frame(parent, relief='sunken', borderwidth=1)
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(15, 0))
        status_frame.columnconfigure(1, weight=1)
        
        self.status_var = tk.StringVar()
        self.status_var.set("✨ Welcome to OCRify! Load an image to get started")
        
        status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                               style='Status.TLabel', anchor=tk.W)
        status_label.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        # Version info
        version_label = ttk.Label(status_frame, text="OCRify v2.0", 
                                style='Status.TLabel', anchor=tk.E)
        version_label.grid(row=0, column=1, sticky=tk.E, padx=10, pady=5)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts for better UX"""
        # Bind both lowercase and uppercase for cross-platform compatibility
        self.root.bind('<Control-o>', lambda e: self.load_image())
        self.root.bind('<Control-O>', lambda e: self.load_image())
        
        self.root.bind('<Control-e>', lambda e: self.extract_text() if self.extract_btn['state'] == 'normal' else None)
        self.root.bind('<Control-E>', lambda e: self.extract_text() if self.extract_btn['state'] == 'normal' else None)
        
        self.root.bind('<Control-m>', lambda e: self.extract_metadata() if self.metadata_btn['state'] == 'normal' else None)
        self.root.bind('<Control-M>', lambda e: self.extract_metadata() if self.metadata_btn['state'] == 'normal' else None)
        
        self.root.bind('<Control-s>', lambda e: self.save_results() if self.save_btn['state'] == 'normal' else None)
        self.root.bind('<Control-S>', lambda e: self.save_results() if self.save_btn['state'] == 'normal' else None)
        
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<Control-Q>', lambda e: self.root.quit())
        
        self.root.bind('<F1>', lambda e: self.show_help())
    
    def create_tooltip(self, widget, text):
        """Create tooltip for widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, background=self.colors['text_primary'], 
                           foreground='white', font=('Segoe UI', 9), padx=5, pady=2)
            label.pack()
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def on_file_drop(self, event):
        """Handle drag and drop file events"""
        files = event.data.split()
        if files:
            file_path = files[0].strip('{}')  # Remove braces if present
            if self.is_image_file(file_path):
                self.load_image_from_path(file_path)
            else:
                messagebox.showwarning("Invalid File", 
                                     "Please drop a valid image file.\n\n"
                                     "Supported formats: PNG, JPG, JPEG, GIF, BMP, TIFF")
                self.root.focus_force()
    
    def is_image_file(self, file_path):
        """Check if file is a supported image format"""
        valid_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif')
        return file_path.lower().endswith(valid_extensions)
    
    def load_image_from_path(self, file_path):
        """Load image from a specific file path"""
        try:
            self.image_path = file_path
            self.original_image = Image.open(file_path)
            
            # Display image
            self.display_image(self.original_image)
            
            # Enable buttons
            self.extract_btn.configure(state='normal')
            self.metadata_btn.configure(state='normal')
            
            # Update recent files
            self.add_to_recent_files(file_path)
            
            # Auto-extract if enabled
            if self.settings.get("auto_extract", False):
                self.root.after(100, self.extract_text)
            
            self.status_var.set(f"✅ Image loaded: {os.path.basename(file_path)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            self.root.focus_force()
            self.status_var.set("❌ Error loading image")
    
    def display_image(self, image):
        """Display image in the image label with proper scaling"""
        # Calculate display size maintaining aspect ratio
        display_width, display_height = 400, 300
        img_width, img_height = image.size
        
        # Calculate scaling factor
        scale_w = display_width / img_width
        scale_h = display_height / img_height
        scale = min(scale_w, scale_h, 1.0)  # Don't upscale
        
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(resized_image)
        
        self.image_label.configure(image=photo, text="", bg='white')
        self.image_label.image = photo  # Keep reference
    
    def show_progress(self, message):
        """Show progress indicator"""
        self.progress_label.configure(text=message)
        self.progress_frame.grid()
        self.progress_bar.start(10)
        self.root.update()
    
    def hide_progress(self):
        """Hide progress indicator"""
        self.progress_bar.stop()
        self.progress_frame.grid_remove()
        self.root.update()
    
    def load_image(self):
        """Enhanced image loading with progress indicator"""
        file_types = [
            ('All Image files', '*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.tif'),
            ('PNG files', '*.png'),
            ('JPEG files', '*.jpg *.jpeg'),
            ('GIF files', '*.gif'),
            ('BMP files', '*.bmp'),
            ('TIFF files', '*.tiff *.tif'),
            ('All files', '*.*')
        ]
        
        filename = filedialog.askopenfilename(
            title="Select an image file - OCRify",
            filetypes=file_types
        )
        
        # Return focus to main window
        self.root.focus_force()
        
        if filename:
            self.load_image_from_path(filename)
    
    def extract_text(self):
        """Enhanced text extraction with progress tracking"""
        if not self.image_path:
            messagebox.showwarning("Warning", "Please load an image first")
            self.root.focus_force()
            return
        
        self.show_progress("🔍 Extracting text from image...")
        self.extract_btn.configure(state='disabled')
        
        thread = threading.Thread(target=self._perform_ocr)
        thread.daemon = True
        thread.start()
    
    def _perform_ocr(self):
        """Enhanced OCR with better error handling"""
        try:
            # Extract text using Tesseract
            image = Image.open(self.image_path)
            self.extracted_text = pytesseract.image_to_string(image)
            
            # Update GUI in main thread
            self.root.after(0, self._update_results)
            
        except Exception as e:
            error_msg = f"OCR extraction failed: {str(e)}\n\nPlease ensure:\n1. Tesseract OCR is properly installed\n2. The image contains readable text\n3. The image quality is sufficient"
            self.root.after(0, lambda: self._show_error(error_msg))
    
    def _update_results(self):
        """Enhanced results update with detailed analytics"""
        try:
            # Display extracted text
            self.text_display.delete(1.0, tk.END)
            self.text_display.insert(1.0, self.extracted_text)
            
            # Enhanced text analysis
            self._analyze_text_enhanced()
            
            # Enable save button
            self.save_btn.configure(state='normal')
            
            self.status_var.set("✅ Text extraction completed successfully")
            
            # Switch to text tab
            self.notebook.select(0)
            
            # Return focus to main window
            self.root.focus_force()
            
        except Exception as e:
            self._show_error(f"Failed to update results: {str(e)}")
        finally:
            self.extract_btn.configure(state='normal')
            self.hide_progress()
    
    def _analyze_text_enhanced(self):
        """Enhanced text analysis with more detailed statistics"""
        if not self.extracted_text.strip():
            self.word_count_label.configure(text="Words: 0")
            self.char_count_label.configure(text="Characters: 0")
            self.line_count_label.configure(text="Lines: 0")
            
            self.freq_words_text.delete(1.0, tk.END)
            self.freq_words_text.insert(1.0, "📋 No text extracted from image\n\nPossible reasons:\n- Image contains no readable text\n- Text quality is too poor\n- Language not supported")
            self.unique_word_text.delete(1.0, tk.END)
            self.unique_word_text.insert(1.0, "📋 No text available for analysis")
            return
        
        # Enhanced statistics
        words = re.findall(r'\b[a-zA-Z]+\b', self.extracted_text.lower())
        characters = len(self.extracted_text)
        lines = len(self.extracted_text.split('\n'))
        
        # Update statistics labels
        self.word_count_label.configure(text=f"Words: {len(words):,}")
        self.char_count_label.configure(text=f"Characters: {characters:,}")
        self.line_count_label.configure(text=f"Lines: {lines:,}")
        
        if not words:
            self.freq_words_text.delete(1.0, tk.END)
            self.freq_words_text.insert(1.0, "🔍 No recognizable words found\n\nThe extracted text may contain:\n- Only numbers or symbols\n- Non-English characters\n- Fragmented text")
            self.unique_word_text.delete(1.0, tk.END)
            self.unique_word_text.insert(1.0, "🔍 No valid words for analysis")
            return
        
        # Enhanced frequency analysis
        word_freq = Counter(words)
        top_10 = word_freq.most_common(10)
        
        freq_text = "🏆 TOP 10 MOST FREQUENT WORDS\n"
        freq_text += "=" * 40 + "\n\n"
        freq_text += "Rank │ Word            │ Count │ %\n"
        freq_text += "─────┼─────────────────┼───────┼──────\n"
        
        total_words = len(words)
        for i, (word, count) in enumerate(top_10, 1):
            percentage = (count / total_words) * 100
            freq_text += f"{i:2}.   │ {word:<15} │ {count:>5} │ {percentage:4.1f}%\n"
        
        self.freq_words_text.delete(1.0, tk.END)
        self.freq_words_text.insert(1.0, freq_text)
        
        # Enhanced unique word analysis
        unique_words = [word for word, count in word_freq.items() 
                       if count == 1 and len(word) >= 4]
        
        if unique_words:
            most_unique = max(unique_words, key=len)
            thread = threading.Thread(target=self._get_word_meaning, args=(most_unique,))
            thread.daemon = True
            thread.start()
        else:
            self.unique_word_text.delete(1.0, tk.END)
            self.unique_word_text.insert(1.0, "🔍 No unique words found\n\nAll words appear multiple times or are shorter than 4 letters.\n\nTry with an image containing more diverse vocabulary.")
    
    def copy_text(self):
        """Copy extracted text to clipboard"""
        if self.extracted_text:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.extracted_text)
            self.status_var.set("📋 Text copied to clipboard")
        else:
            messagebox.showinfo("Info", "No text to copy")
            self.root.focus_force()
    
    def clear_text(self):
        """Clear the text display"""
        self.text_display.delete(1.0, tk.END)
        self.status_var.set("🗑️ Text display cleared")
    
    def save_results(self):
        """Save extracted text and metadata to file"""
        if not self.extracted_text and not self.image_metadata:
            messagebox.showinfo("Info", "No results to save")
            self.root.focus_force()
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save OCRify Results",
            defaultextension=".txt",
            filetypes=[
                ('Text files', '*.txt'),
                ('JSON files', '*.json'),
                ('All files', '*.*')
            ]
        )
        
        # Return focus to main window
        self.root.focus_force()
        
        if filename:
            try:
                if filename.lower().endswith('.json'):
                    # Save as JSON
                    data = {
                        'extracted_text': self.extracted_text,
                        'metadata': self.image_metadata,
                        'image_path': self.image_path,
                        'timestamp': datetime.now().isoformat()
                    }
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                else:
                    # Save as text
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write("OCRify - Text Extraction Results\n")
                        f.write("=" * 40 + "\n\n")
                        f.write(f"Image: {os.path.basename(self.image_path) if self.image_path else 'Unknown'}\n")
                        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                        f.write("EXTRACTED TEXT:\n")
                        f.write("-" * 20 + "\n")
                        f.write(self.extracted_text)
                        
                self.status_var.set(f"💾 Results saved to {os.path.basename(filename)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save results: {str(e)}")
                self.root.focus_force()
    
    def export_metadata(self):
        """Export metadata to JSON file"""
        if not self.image_metadata:
            messagebox.showinfo("Info", "No metadata to export")
            self.root.focus_force()
            return
        
        filename = filedialog.asksaveasfilename(
            title="Export Metadata - OCRify",
            defaultextension=".json",
            filetypes=[('JSON files', '*.json'), ('All files', '*.*')]
        )
        
        # Return focus to main window
        self.root.focus_force()
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.image_metadata, f, indent=2, ensure_ascii=False)
                self.status_var.set(f"📤 Metadata exported to {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export metadata: {str(e)}")
                self.root.focus_force()
    
    def add_to_recent_files(self, file_path):
        """Add file to recent files list"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:10]  # Keep only 10 recent files
        self.update_recent_menu()
    
    def update_recent_menu(self):
        """Update recent files menu"""
        self.recent_menu.delete(0, tk.END)
        
        if not self.recent_files:
            self.recent_menu.add_command(label="No recent files", state='disabled')
        else:
            for i, file_path in enumerate(self.recent_files):
                filename = os.path.basename(file_path)
                if len(filename) > 30:
                    filename = filename[:27] + "..."
                self.recent_menu.add_command(
                    label=f"{i+1}. {filename}",
                    command=lambda fp=file_path: self.load_image_from_path(fp)
                )
            
            self.recent_menu.add_separator()
            self.recent_menu.add_command(label="Clear Recent", command=self.clear_recent_files)
    
    def clear_recent_files(self):
        """Clear recent files list"""
        self.recent_files.clear()
        self.update_recent_menu()
        self.status_var.set("🗑️ Recent files cleared")
    
    def load_recent_files(self):
        """Load recent files from settings (placeholder)"""
        # This would load from a config file in a full implementation
        pass
    
    def show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("OCRify Settings")
        settings_window.geometry("400x300")
        settings_window.resizable(False, False)
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Center the window
        settings_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        main_frame = ttk.Frame(settings_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="OCRify Settings", font=('Segoe UI', 14, 'bold')).pack(pady=(0, 20))
        
        # Auto-extract setting
        auto_extract_var = tk.BooleanVar(value=self.settings.get("auto_extract", False))
        ttk.Checkbutton(main_frame, text="Auto-extract text when image is loaded",
                       variable=auto_extract_var).pack(anchor=tk.W, pady=5)
        
        # Auto-save setting
        auto_save_var = tk.BooleanVar(value=self.settings.get("save_results", True))
        ttk.Checkbutton(main_frame, text="Enable auto-save functionality",
                       variable=auto_save_var).pack(anchor=tk.W, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))
        
        def save_settings():
            self.settings["auto_extract"] = auto_extract_var.get()
            self.settings["save_results"] = auto_save_var.get()
            settings_window.destroy()
            self.status_var.set("⚙️ Settings saved")
        
        ttk.Button(button_frame, text="Save", command=save_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=settings_window.destroy).pack(side=tk.RIGHT)
    
    def show_help(self):
        """Show help dialog with keyboard shortcuts and usage information"""
        help_window = tk.Toplevel(self.root)
        help_window.title("OCRify Help")
        help_window.geometry("600x500")
        help_window.transient(self.root)
        help_window.grab_set()
        
        # Center the window
        help_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 100,
            self.root.winfo_rooty() + 100
        ))
        
        main_frame = ttk.Frame(help_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="OCRify Help & Shortcuts", 
                 font=('Segoe UI', 16, 'bold')).pack(pady=(0, 20))
        
        help_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=20, width=70)
        help_text.pack(fill=tk.BOTH, expand=True)
        
        help_content = """
OCRify - Advanced OCR Text Extractor & Image Analyzer

KEYBOARD SHORTCUTS:
• Ctrl+O: Load image
• Ctrl+E: Extract text
• Ctrl+M: Extract metadata
• Ctrl+S: Save results
• Ctrl+Q: Quit application
• F1: Show this help

HOW TO USE:
1. Load an image by clicking "Load Image" or drag & drop an image file
2. Click "Extract Text" to perform OCR on the loaded image
3. View results in the tabs: Text, Analytics, and Metadata
4. Use "Save Results" to export your findings

FEATURES:
• Text extraction from images using advanced OCR
• Comprehensive text analytics and word frequency analysis
• Complete image metadata and EXIF data extraction
• Drag and drop support for easy file loading
• Recent files menu for quick access
• Modern, responsive user interface

SUPPORTED IMAGE FORMATS:
• PNG, JPG, JPEG, GIF, BMP, TIFF, TIF

TIPS FOR BEST RESULTS:
• Use high-resolution, clear images
• Ensure good contrast between text and background
• Avoid heavily stylized or decorative fonts
• Make sure the text is horizontally aligned

For technical support or feature requests, please visit our GitHub repository.

OCRify v2.0 - Making text extraction simple and powerful!
        """
        
        help_text.insert(1.0, help_content)
        help_text.configure(state='disabled')
        
        ttk.Button(main_frame, text="Close", command=help_window.destroy).pack(pady=(10, 0))
    
    def extract_metadata(self):
        """Extract and display image metadata including EXIF data"""
        if not self.image_path or not self.original_image:
            messagebox.showwarning("Warning", "Please load an image first")
            self.root.focus_force()
            return
        
        self.show_progress("📋 Extracting image metadata...")
        self.metadata_btn.configure(state='disabled')
        
        thread = threading.Thread(target=self._perform_metadata_extraction)
        thread.daemon = True
        thread.start()
    
    def _perform_metadata_extraction(self):
        """Extract metadata in a separate thread"""
        try:
            metadata = self._get_image_metadata()
            self.image_metadata = metadata
            
            # Update GUI in main thread
            self.root.after(0, self._update_metadata_display)
            
        except Exception as e:
            error_msg = f"Metadata extraction failed: {str(e)}"
            self.root.after(0, lambda: self._show_metadata_error(error_msg))
    
    def _get_image_metadata(self):
        """Extract comprehensive metadata from the image"""
        metadata = {}
        
        try:
            # Basic file information
            file_stats = os.stat(self.image_path)
            metadata['file_info'] = {
                'filename': os.path.basename(self.image_path),
                'filepath': self.image_path,
                'file_size': file_stats.st_size,
                'file_size_mb': round(file_stats.st_size / (1024 * 1024), 2),
                'created': datetime.fromtimestamp(file_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                'modified': datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Image properties
            metadata['image_info'] = {
                'format': self.original_image.format,
                'mode': self.original_image.mode,
                'size': self.original_image.size,
                'width': self.original_image.width,
                'height': self.original_image.height,
                'aspect_ratio': round(self.original_image.width / self.original_image.height, 2),
                'megapixels': round((self.original_image.width * self.original_image.height) / 1000000, 2)
            }
            
            # Color information
            if hasattr(self.original_image, 'getcolors'):
                try:
                    colors = self.original_image.getcolors(maxcolors=256*256*256)
                    if colors:
                        metadata['color_info'] = {
                            'unique_colors': len(colors),
                            'dominant_color': colors[0][1] if colors else 'Unknown'
                        }
                except:
                    metadata['color_info'] = {'unique_colors': 'Unable to calculate'}
            
            # EXIF data
            exif_data = {}
            if hasattr(self.original_image, '_getexif') and self.original_image._getexif():
                exif = self.original_image._getexif()
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    # Convert bytes to string for display
                    if isinstance(value, bytes):
                        try:
                            value = value.decode('utf-8')
                        except:
                            value = str(value)
                    exif_data[tag] = value
            
            metadata['exif_data'] = exif_data
            
            return metadata
            
        except Exception as e:
            raise Exception(f"Error extracting metadata: {str(e)}")
    
    def _update_metadata_display(self):
        """Update the metadata display with extracted information"""
        try:
            metadata_text = self._format_metadata_text(self.image_metadata)
            
            self.metadata_display.delete(1.0, tk.END)
            self.metadata_display.insert(1.0, metadata_text)
            
            self.status_var.set("✅ Metadata extraction completed")
            
            # Switch to metadata tab
            self.notebook.select(2)  # Metadata tab is index 2
            
            # Return focus to main window
            self.root.focus_force()
            
        except Exception as e:
            self._show_metadata_error(f"Failed to display metadata: {str(e)}")
        finally:
            self.metadata_btn.configure(state='normal')
            self.hide_progress()
    
    def _format_metadata_text(self, metadata):
        """Format metadata into a readable text display"""
        text = "📋 OCRify METADATA REPORT\n"
        text += "=" * 50 + "\n\n"
        
        # File Information
        if 'file_info' in metadata:
            file_info = metadata['file_info']
            text += "📁 FILE INFORMATION\n"
            text += "-" * 20 + "\n"
            text += f"Filename: {file_info.get('filename', 'Unknown')}\n"
            text += f"File Path: {file_info.get('filepath', 'Unknown')}\n"
            text += f"File Size: {file_info.get('file_size', 0):,} bytes ({file_info.get('file_size_mb', 0)} MB)\n"
            text += f"Created: {file_info.get('created', 'Unknown')}\n"
            text += f"Modified: {file_info.get('modified', 'Unknown')}\n\n"
        
        # Image Properties
        if 'image_info' in metadata:
            img_info = metadata['image_info']
            text += "🖼️ IMAGE PROPERTIES\n"
            text += "-" * 20 + "\n"
            text += f"Format: {img_info.get('format', 'Unknown')}\n"
            text += f"Color Mode: {img_info.get('mode', 'Unknown')}\n"
            text += f"Dimensions: {img_info.get('width', 0)} x {img_info.get('height', 0)} pixels\n"
            text += f"Aspect Ratio: {img_info.get('aspect_ratio', 0)}:1\n"
            text += f"Megapixels: {img_info.get('megapixels', 0)} MP\n\n"
        
        # Color Information
        if 'color_info' in metadata:
            color_info = metadata['color_info']
            text += "🎨 COLOR INFORMATION\n"
            text += "-" * 20 + "\n"
            text += f"Unique Colors: {color_info.get('unique_colors', 'Unknown')}\n"
            if 'dominant_color' in color_info and color_info['dominant_color'] != 'Unknown':
                text += f"Dominant Color: {color_info['dominant_color']}\n"
            text += "\n"
        
        # EXIF Data
        if 'exif_data' in metadata and metadata['exif_data']:
            text += "📷 EXIF DATA\n"
            text += "-" * 20 + "\n"
            
            # Prioritize important EXIF tags
            priority_tags = ['Make', 'Model', 'DateTime', 'DateTimeOriginal', 'Software', 
                           'ImageWidth', 'ImageLength', 'Orientation', 'XResolution', 
                           'YResolution', 'ResolutionUnit', 'Flash', 'FocalLength', 
                           'ISOSpeedRatings', 'ExposureTime', 'FNumber', 'WhiteBalance']
            
            exif_data = metadata['exif_data']
            
            # Display priority tags first
            for tag in priority_tags:
                if tag in exif_data:
                    value = exif_data[tag]
                    text += f"{tag}: {value}\n"
            
            # Display other EXIF tags
            other_tags = [tag for tag in exif_data.keys() if tag not in priority_tags]
            if other_tags:
                text += "\nOther EXIF Data:\n"
                for tag in sorted(other_tags):
                    value = exif_data[tag]
                    # Limit very long values
                    if isinstance(value, str) and len(value) > 50:
                        value = value[:47] + "..."
                    text += f"{tag}: {value}\n"
        else:
            text += "📷 EXIF DATA\n"
            text += "-" * 20 + "\n"
            text += "No EXIF data found in this image.\n\n"
        
        return text
    
    def _show_metadata_error(self, error_msg):
        """Show metadata extraction error and update status"""
        messagebox.showerror("Metadata Error", error_msg)
        self.root.focus_force()
        self.status_var.set("❌ Error extracting metadata")
        self.metadata_btn.configure(state='normal')
        self.hide_progress()
    
    def _get_word_meaning(self, word):
        """Get the meaning of a word using a dictionary API"""
        try:
            # Using Free Dictionary API
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract meaning
                meaning_text = f"🎯 MOST UNIQUE WORD: {word.upper()}\n" + "=" * 30 + "\n\n"
                
                if data and len(data) > 0:
                    entry = data[0]
                    
                    # Add phonetic if available
                    if 'phonetic' in entry:
                        meaning_text += f"Pronunciation: {entry['phonetic']}\n\n"
                    
                    # Add meanings
                    if 'meanings' in entry:
                        for i, meaning in enumerate(entry['meanings'][:2]):  # Limit to 2 meanings
                            part_of_speech = meaning.get('partOfSpeech', 'Unknown')
                            meaning_text += f"{part_of_speech.upper()}:\n"
                            
                            definitions = meaning.get('definitions', [])
                            for j, definition in enumerate(definitions[:2]):  # Limit to 2 definitions
                                def_text = definition.get('definition', 'No definition available')
                                meaning_text += f"  {j+1}. {def_text}\n"
                                
                                # Add example if available
                                if 'example' in definition:
                                    meaning_text += f"     Example: {definition['example']}\n"
                            meaning_text += "\n"
                else:
                    meaning_text += "Definition not found in dictionary."
            else:
                meaning_text = f"🎯 MOST UNIQUE WORD: {word.upper()}\n" + "=" * 30 + "\n\nDefinition not available\n(Dictionary API returned an error)"
                
        except requests.RequestException:
            meaning_text = f"🎯 MOST UNIQUE WORD: {word.upper()}\n" + "=" * 30 + "\n\nDefinition not available\n(Network connection error)"
        except Exception as e:
            meaning_text = f"🎯 MOST UNIQUE WORD: {word.upper()}\n" + "=" * 30 + f"\n\nError getting definition:\n{str(e)}"
        
        # Update GUI in main thread
        self.root.after(0, lambda: self._update_unique_word(meaning_text))
    
    def _update_unique_word(self, meaning_text):
        """Update the unique word display with meaning"""
        self.unique_word_text.delete(1.0, tk.END)
        self.unique_word_text.insert(1.0, meaning_text)
    
    def _show_error(self, error_msg):
        """Show error message and update status"""
        messagebox.showerror("OCRify Error", error_msg)
        self.root.focus_force()
        self.status_var.set("❌ Error occurred")
        self.extract_btn.configure(state='normal')
        self.hide_progress()


def main():
    """
    Main function to initialize and run OCRify
    """
    # Check if Tesseract is available
    tesseract_available = True
    try:
        pytesseract.get_tesseract_version()
        print("✅ Tesseract OCR is available")
    except Exception as e:
        tesseract_available = False
        print("⚠️ Warning: Tesseract OCR not found.")
        print("\n📋 To enable text extraction, please install Tesseract OCR:")
        print("1. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("2. Install and add to PATH")
        print("3. Or set pytesseract.pytesseract.tesseract_cmd path manually")
        
        # Try to set common Windows installation paths
        common_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            r'C:\Users\{os.getenv("USERNAME")}\AppData\Local\Tesseract-OCR\tesseract.exe'
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                print(f"✅ Found Tesseract at: {path}")
                tesseract_available = True
                break
        
        if not tesseract_available:
            print("\n⚠️ Tesseract not found. Text extraction will be disabled.")
            print("📋 Image metadata extraction will still work.")
    
    try:
        # Check for tkinterdnd2 for drag and drop support
        try:
            root = TkinterDnD.Tk()
            print("✅ Drag and drop support enabled")
        except:
            print("⚠️ tkinterdnd2 not found, using standard Tkinter")
            print("📋 Install tkinterdnd2 for drag and drop support: pip install tkinterdnd2")
            root = tk.Tk()
        
        # Set application icon if available (optional)
        try:
            # This would set an icon if you have one
            # root.iconbitmap('icon.ico')
            pass
        except:
            pass
        
        # Create the main application
        app = OCRTextExtractor(root)
        
        # Disable text extraction if Tesseract is not available
        if not tesseract_available:
            app.extract_btn.configure(state='disabled')
            app.status_var.set("⚠️ Tesseract OCR not found - Text extraction disabled")
        
        # Center the window on screen
        root.eval('tk::PlaceWindow . center')
        
        # Start the application
        print("🚀 Starting OCRify - Advanced OCR Text Extractor & Image Analyzer...")
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error starting OCRify: {str(e)}")
        messagebox.showerror("OCRify Error", 
                           f"Failed to start OCRify:\n{str(e)}")
    
    print("\n👋 OCRify closed. Thank you for using OCRify!")


if __name__ == "__main__":
    """
    OCRify - Advanced OCR Text Extractor & Image Analyzer
    
    A modern, feature-rich application for extracting text from images using OCR,
    analyzing text content, and viewing detailed image metadata including EXIF data.
    
    Features:
    - 🔍 Advanced text extraction from images using Tesseract OCR
    - 📊 Comprehensive text analytics with detailed statistics
    - 📋 Complete image metadata and EXIF data extraction
    - 🖱️ Drag and drop support for easy file loading
    - ⌨️ Keyboard shortcuts for power users
    - 📁 Recent files menu with quick access
    - 💾 Multiple export formats (TXT, JSON)
    - ⚙️ Customizable settings and preferences
    - 🎯 Modern, responsive user interface with OCRify branding
    - 💡 Tooltips and helpful user guidance
    
    Author: Enhanced AI Assistant
    Version: 2.0 - OCRify Edition
    """
    main()
