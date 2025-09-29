# 📝 Content Brief System - Simplified

A clean, simplified content brief generator that uses **prompts as TXT files**, **flexible inputs**, and produces **Dutch content briefs** in the exact format you need.

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run the system:**
   ```bash
   cd content_brief_system
   python main.py
   ```

## 📁 Project Structure

```
content_brief_system/
├── prompts/                    # 📝 TXT prompt templates
│   ├── serp_analyzer.txt      # Analyzes SERP competitors  
│   ├── page_analyzer.txt      # Audits target page
│   └── brief_generator.txt    # Creates final brief
├── brand_guidelines/           # 🎨 Brand voice guidelines
│   └── ing_tone_of_voice.txt  # ING-specific tone
├── utils/                      # 🛠️ Utilities
│   └── prompt_loader.py       # Loads & formats prompts
├── output/                     # 📄 Generated briefs
├── config.py                   # ⚙️ Configuration
├── main.py                     # 🚀 Main application
├── requirements.txt            # 📦 Dependencies
└── .env.example               # 🔐 Environment template
```

## 🎯 How It Works

### **Simple 3-Agent Flow:**

```
1. 📊 SERP Analyzer     → Analyzes top 3 competitors
2. 🔍 Page Analyzer     → Audits your target page  
3. 📝 Brief Generator   → Creates structured brief
```

### **Input (Flexible):**
- ✅ **URL** (required)
- ✅ **Focus keyword** (required) 
- ✅ **Secondary keywords** (optional)

### **Output (Structured):**
Dutch content brief with these sections:
- **URL & SERP links**
- **Opmerkelijk** (Key insights)
- **Type pagina** (Page type)
- **Funnelfase** (Funnel stage)
- **Body copy** (Content recommendations)
- **Focus keyword**
- **Secundaire keywords**
- **Page title suggestie** (max 60 chars)
- **Meta description suggestie** (max 155 chars)
- **H1/H2/H3 suggesties**
- **Aanvulling CJE** (Strategic additions)
- **Inspiratie** (SERP insights)

## ⚙️ Configuration

### **API Keys (.env file):**
```bash
# Choose your LLM provider:
OPENAI_API_KEY="sk-..."           # For GPT models
# OR
GEMINI_API_KEY="AI..."            # For Gemini models
MODEL="gemini/gemini-2.5-flash"   # Specify model

# For SERP data (when implemented):
SERP_API_KEY="your-serp-key"
```

### **Supported Models:**
- ✅ **OpenAI:** `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`
- ✅ **Gemini:** `gemini/gemini-2.5-flash`, `gemini/gemini-pro`

## 📝 Customizing Prompts

Edit any `.txt` file in `prompts/` directory:

**Example - Add new variable to `serp_analyzer.txt`:**
```
TASK: Analyze for keyword "{focus_keyword}" in {industry} industry.

NEW VARIABLE: {industry}
```

**Then update main.py:**
```python
serp_prompt = loader.load(
    "serp_analyzer.txt",
    focus_keyword=focus_keyword,
    industry="Banking",  # New variable
    **serp_data
)
```

## 🎨 Brand Guidelines

Edit `brand_guidelines/ing_tone_of_voice.txt` to customize:
- Tone of voice rules
- Language preferences  
- Writing guidelines
- Examples of good/bad copy

## 📋 Example Usage

```bash
$ python main.py

============================================================
📝 CONTENT BRIEF GENERATOR  
============================================================

🔗 Target URL (required): https://www.ing.nl/betaalrekening
🎯 Focus keyword (required): gratis betaalrekening
📋 Secondary keywords (optional): online bankieren, betaalpas

============================================================
📊 INPUT SUMMARY:
   URL: https://www.ing.nl/betaalrekening
   Focus Keyword: gratis betaalrekening
   Secondary Keywords: ['online bankieren', 'betaalpas']
============================================================

Continue? (y/n): y

🌐 Fetching data...
   Fetching: https://www.ing.nl/betaalrekening
   Fetching SERP for: gratis betaalrekening
✅ Data fetched

🔍 Running SERP Analyzer...
✅ SERP analysis complete

📄 Running Page Analyzer...  
✅ Page analysis complete

📝 Generating content brief...
✅ Brief generated

============================================================
✅ SUCCESS! Brief saved to: output/brief_gratis_betaalrekening.md
============================================================
```

## 🔧 Adding SERP API Integration

**Currently using dummy data. To add real SERP data:**

1. **Choose a SERP API provider:**
   - SerpAPI
   - Bright Data
   - DataForSEO
   - ScaleSerp

2. **Update `get_serp_results()` in main.py:**
   ```python
   def get_serp_results(keyword, num_results=3):
       # Replace with actual API call
       api_key = Config.SERP_API_KEY
       # Your SERP API implementation here
       return results
   ```

## 🎯 What's Different from the Complex Version

| **Before (Complex)** | **After (Simple)** | **Why** |
|---------------------|-------------------|---------|
| Hardcoded prompts in code | TXT files with variables | Easy editing |
| Hardcoded inputs | User inputs at runtime | Flexibility |
| Generic output | Brief-structured output | Matches your template |
| LangGraph + 6 agents | Simple 3-function flow | Keep it simple |
| Keyword discovery complexity | Optional secondary keywords | Focus on core value |

## 🔮 Future Enhancements (Optional)

- ✅ **SERP API integration** (replace dummy data)
- ✅ **Web scraping improvements** (handle more page types)
- ✅ **Multiple brand guidelines** (beyond just ING)
- ✅ **Batch processing** (multiple URLs at once)
- ✅ **Output formats** (JSON, Excel, etc.)
- ✅ **Keyword research** (add back if needed)

## 🐛 Troubleshooting

**Import errors?**
```bash
pip install -r requirements.txt
```

**No API response?**
- Check your `.env` file
- Verify API keys are valid
- Check internet connection

**Empty briefs?**
- Check that prompts have all required variables
- Verify page content was fetched successfully
- Check LLM model availability

---

✨ **Keep it simple, keep it working!** This system focuses on the core value: **analyzing data and generating great briefs**. 🎯