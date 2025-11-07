# OCR Text Extractor with Analytics

A comprehensive GUI application for extracting text from images using OCR (Optical Character Recognition) technology, with advanced text analytics features.

## 🌟 Features

- **📁 Image Loading**: Support for multiple image formats (PNG, JPG, JPEG, GIF, BMP, TIFF)
- **🔍 OCR Text Extraction**: Extract text from images using Tesseract OCR
- **📊 Word Count**: Real-time word counting of extracted text
- **📈 Frequency Analysis**: Top 10 most frequently used words with counts
- **🎯 Unique Word Detection**: Finds the most unique word (appears only once) with dictionary meaning
- **📚 Dictionary Integration**: Automatic word meaning lookup using online dictionary API
- **🖥️ User-friendly GUI**: Clean, tabbed interface with image preview

## 📋 Prerequisites

### Required Python Packages
```bash
pip install pillow pytesseract requests
```

| Package | Purpose | Installation |
|---------|---------|--------------|
| `tkinter` | GUI Framework | Usually included with Python |
| `Pillow` | Image processing | `pip install pillow` |
| `pytesseract` | OCR wrapper | `pip install pytesseract` |
| `requests` | API calls | `pip install requests` |

### Tesseract OCR Engine Installation

#### 🪟 Windows
1. Download from: [Tesseract Windows Installer](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install the executable
3. Add to system PATH or use default location

#### 🐧 Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install tesseract-ocr
```

#### 🍎 macOS
```bash
brew install tesseract
```

#### Manual Path Configuration
If Tesseract is installed in a custom location:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Your\Tesseract\Path\tesseract.exe'
```

## 🚀 Quick Start

1. **Clone or Download** the project files
2. **Install Dependencies**:
   ```bash
   cd c:\Py_project
   pip install -r requirements.txt
   ```
3. **Run the Application**:
   ```bash
   python Main.py
   ```

## 📖 How to Use

### Step 1: Load an Image
- Click **"Load Image"** button
- Select an image file containing text
- Preview appears in the left panel

### Step 2: Extract Text
- Click **"Extract Text"** button
- Wait for OCR processing (progress shown in status bar)
- Results appear in tabbed interface

### Step 3: Analyze Results
Navigate through the tabs to view:
- **📝 Extracted Text**: Raw OCR output
- **📊 Analytics**: Detailed text statistics and insights

## 📁 Project Structure

```
c:\Py_project\
├── Main.py                 # 🎯 Main application entry point
├── README.md              # 📚 Documentation (this file)
├── requirements.txt       # 📦 Python dependencies
└── sample_images/         # 🖼️ Test images (optional)
```

## 🔧 Technical Implementation

### Core Technologies
- **GUI**: `tkinter` with `ttk` themed widgets
- **OCR Engine**: Google's Tesseract OCR
- **Image Processing**: Pillow (PIL)
- **Text Analysis**: Regular expressions and Collections.Counter
- **API Integration**: RESTful dictionary API
- **Concurrency**: Threading for non-blocking operations

### Analytics Features

| Feature | Description | Algorithm |
|---------|-------------|-----------|
| **Word Count** | Total alphabetic words | Regex pattern matching |
| **Frequency Analysis** | Top 10 common words | Counter with most_common() |
| **Unique Detection** | Single-occurrence words | Counter filtering |
| **Dictionary Lookup** | Word definitions | REST API integration |

## 🛠️ Troubleshooting

### Common Issues

#### ❌ "Tesseract not found" Error
**Solutions:**
- ✅ Verify Tesseract installation: `tesseract --version`
- ✅ Check PATH environment variable
- ✅ Use absolute path in code if needed

#### ❌ No Text Extracted
**Solutions:**
- ✅ Use high-contrast, clear images
- ✅ Ensure text is horizontal and readable
- ✅ Try different image formats or preprocessing

#### ❌ Dictionary API Failures
**Solutions:**
- ✅ Check internet connectivity
- ✅ Verify API availability at [dictionaryapi.dev](https://dictionaryapi.dev)
- ✅ Check firewall/proxy settings

#### ❌ GUI Performance Issues
**Solutions:**
- ✅ Process smaller images
- ✅ Close other applications
- ✅ Ensure sufficient system memory

## 🔮 Future Roadmap

### Planned Features
- [ ] **Multi-language OCR** support (Spanish, French, etc.)
- [ ] **Batch processing** for multiple images
- [ ] **Export options** (PDF, Word, CSV)
- [ ] **OCR confidence** scoring
- [ ] **Text preprocessing** filters
- [ ] **Custom dictionaries** integration
- [ ] **Cloud OCR** service integration
- [ ] **Mobile app** version

### Performance Improvements
- [ ] **Caching** for processed images
- [ ] **Parallel processing** for batch operations
- [ ] **Memory optimization** for large images
- [ ] **Background processing** queue

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the **MIT License** - see the LICENSE file for details.

## 📞 Support

- **Issues**: Create an issue on the project repository
- **Documentation**: Refer to this README
- **Community**: Join discussions in project forums

---

**Made with ❤️ using Python and Tesseract OCR**