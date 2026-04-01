# 🎨 The Pitch Visualizer

**AI-Powered Storyboard Generator for Sales Pitch Decks**

Transform customer success stories into compelling visual storyboards with AI. This tool automatically segments narratives, engineers visual prompts, and generates professional storyboards in seconds.

---

## 🌟 Features

### Core Features
- **Dynamic Scene Segmentation**: Automatically detects story complexity and generates 3-6 scenes
- **LLM-Powered Prompt Engineering**: Uses Groq Llama 3.3 70B to create detailed visual prompts
- **4-Tier Image Generation**: Cascading fallback system for 95%+ reliability
- **Modern Dark UI**: Professional interface with real-time progress tracking
- **Visual Consistency**: Maintains character and style consistency across all panels
- **Multiple Visual Styles**: 6 professional style options to choose from

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- NVIDIA GPU (recommended) or CPU
- 7GB free disk space (for local model)
- Internet connection (for first-time model download)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd "The Pitch Visualizer"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys**
   
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_key_here
   HUGGINGFACE_API_KEY=your_hf_key_here
   STABILITY_API_KEY=your_stability_key_here  # Optional
   IMAGE_METHOD=auto  # Options: local, huggingface, pollinate, auto
   ```
   
   Get your API keys:
   - Groq: https://console.groq.com/keys
   - Hugging Face: https://huggingface.co/settings/tokens
   - Stability AI: https://platform.stability.ai/ (optional)

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Open in browser**
   ```
   http://127.0.0.1:8000
   ```

---

## 📖 Usage

1. **Enter your narrative**: Paste a customer success story (3-5 sentences minimum)
2. **Select visual style**: Choose from 6 professional styles
3. **Generate storyboard**: Click the button and wait 30-90 seconds
4. **Review results**: View your storyboard with images, captions, and AI prompts

### Example Narrative
```
The marketing team at TechCorp was drowning in manual reports, spending 20 hours 
weekly on data entry. Errors were rampant and morale was at an all-time low. 
Then they discovered our AI automation platform. Within weeks, the team transformed 
their workflow. Now they spend just 2 hours weekly on reports, error rates dropped 
95%, and the team focuses on strategic creative work instead.
```

---

## 🎯 Image Generation Methods

The system uses a 4-tier cascading fallback for maximum reliability:

| Method | Speed | Cost | Best For |
|--------|-------|------|----------|
| **Local Stable Diffusion** | 10-20s | FREE | Daily use (PRIMARY) |
| **Stability AI API** | 5-10s | Paid | High quality fallback |
| **Hugging Face API** | 20-30s | Free tier | **Best for context-aware images** ⭐ |
| **Pollinations.ai** | 15-30s | FREE | Last resort |

> **💡 Recommendation:** For best results with context-aware images that match your narrative, use `IMAGE_METHOD=huggingface`. The Hugging Face Inference API generates more semantically accurate images compared to local diffusers, which may lack performance on consumer GPUs.

Configure in `.env`:
```env
IMAGE_METHOD=auto  # Tries all methods automatically (RECOMMENDED)
IMAGE_METHOD=local  # Force local GPU only
IMAGE_METHOD=huggingface  # Force Hugging Face API only
IMAGE_METHOD=pollinate  # Force Pollinations only
```

---

## 🛠️ Technical Stack

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI + Uvicorn |
| **Frontend** | HTML/CSS/JavaScript |
| **LLM** | Groq Llama 3.3 70B |
| **Image Generation** | Hugging Face Diffusers (Local) |
| **Fallback APIs** | Stability AI, Hugging Face Inference, Pollinations |
| **Templating** | Jinja2 |
| **Styling** | Custom CSS (Dark theme) |

---

## 📁 Project Structure

```
The Pitch Visualizer/
├── main.py                      # FastAPI application
├── requirements.txt             # Python dependencies
├── .env                        # API keys (create this)
├── .gitignore                  # Git ignore rules
├── services/
│   ├── text_engine.py          # LLM narrative processing
│   ├── image_engine.py         # Image generation entry point
│   └── image_engine_diffusers.py  # Local SD + fallbacks
├── static/
│   ├── css/
│   │   └── styles.css          # Custom styles
│   ├── js/
│   │   └── app.js              # Frontend logic
│   └── images/                 # Generated images
└── templates/
    └── index.html              # Main UI template
```

---

## 🔧 Configuration

### Environment Variables (.env)

```env
# Required: LLM API Key
GROQ_API_KEY=gsk_...

# Required: Image Generation (at least one)
HUGGINGFACE_API_KEY=hf_...     # For HF Inference API fallback
STABILITY_API_KEY=sk-...       # Optional: Premium fallback

# Image Generation Method
IMAGE_METHOD=auto  # Options: local, huggingface, pollinate, auto
```

### Image Method Options

- **`auto`**: Cascading fallback (Local → Stability → HF API → Pollinations)
- **`local`**: Local Stable Diffusion GPU only (fastest, FREE)
- **`huggingface`**: Hugging Face Inference API only
- **`pollinate`**: Pollinations.ai only (simplest)

---

## 🐛 Troubleshooting

### "CUDA out of memory"
- Close other GPU applications
- Reduce resolution in `image_engine_diffusers.py`
- Use `IMAGE_METHOD=huggingface` as fallback

### "Model download failed"
- Check internet connection
- Retry (download will resume)
- Clear cache: `C:\Users\<user>\.cache\huggingface\hub\`

### "Rate limited" (Pollinations)
- Wait 2-3 minutes between generations
- Switch to `IMAGE_METHOD=local` or `huggingface`

### "No images generated"
- Check console logs for specific errors
- Verify API keys in `.env` are valid
- Try `IMAGE_METHOD=auto` for automatic fallback

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| **First Run** | 5-10 min (model download) |
| **Subsequent Runs** | 30-90 seconds (3-6 images) |
| **GPU Generation** | 10-20s per image |
| **API Generation** | 20-30s per image |
| **Success Rate** | 95%+ (with auto fallback) |

---

## 🎯 Design Decisions

See [`DESIGN_DECISIONS.md`](./DESIGN_DECISIONS.md) for detailed documentation on:
- Why dynamic scene count (3-6)
- Two-pass LLM processing rationale
- Cascading fallback architecture
- Prompt engineering methodology
- GPU optimization choices

---

## 📝 License

This project is open-source and available for educational and commercial use.

---

## 👨‍💻 Author

Created with ❤️ for the AI community

---

## 📞 Support

For issues or questions:
1. Check console logs for error messages
2. Verify API keys in `.env` are valid
3. Review `DESIGN_DECISIONS.md` for architecture details
4. Check `GAP_ANALYSIS.md` for troubleshooting

---

**Status:** ✅ Production Ready  
**Last Updated:** March 2025  
**Version:** 2.0 - Complete Implementation
