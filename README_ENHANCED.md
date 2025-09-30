# 🚀 Enhanced SEO Content Optimization System

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue"/>
  <img src="https://img.shields.io/badge/License-MIT-blue"/>
  <img src="https://img.shields.io/badge/Enhanced-SEO%20System-green"/>
</p>

---

## 📖 Overview

This advanced SEO Content Optimization System uses LangGraph to perform comprehensive webpage content audits and competitive analysis. The system has been significantly enhanced with **13 specialized AI agents** that work together to provide deep insights into search intent, competitive landscape, keyword opportunities, and content optimization strategies.

**🎯 Key Features:**
- ✅ **Advanced Web Scraping** with Bright Data Web Unlocker
- ✅ **SEMrush Integration** for keyword data and competitive analysis
- ✅ **Intent Classification** and user behavior analysis
- ✅ **Competitive Content Scraping** and analysis
- ✅ **Content Topic Extraction** and gap analysis
- ✅ **Client Content Auditing** with scoring
- ✅ **Automated Content Generation** with specific additions
- ✅ **Comprehensive SEO Reports** with actionable insights

---

## 🤖 System Architecture

The enhanced system consists of **13 specialized AI agents** organized in 3 phases:

### **Phase 1: Data Collection (5 agents)**
1. **Title Scraper** - Extracts page content using Bright Data Web Unlocker
2. **Query Researcher** - Researches search landscape and related queries
3. **Query Extractor** - Identifies main search queries and focus keywords
4. **Competitive Scraper** - Scrapes top competitor pages
5. **SEMrush Keyword** - Fetches keyword metrics (volume, difficulty, CPC)

### **Phase 2: Analysis (5 agents)**
6. **Intent Categorization** - Classifies user search intent
7. **Competitive Summary** - Analyzes competitor content strategies
8. **Content Topics Extractor** - Identifies key topics and themes
9. **Client Content Analyzer** - Audits current content with scoring
10. **AI Overview Retriever** - Fetches Google AI Overviews

### **Phase 3: Optimization (3 agents)**
11. **Summarizer** - Synthesizes all analysis data
12. **Content Additions** - Generates specific content improvements
13. **Briefing Generator** - Creates comprehensive optimization reports

---

## 🛠️ Installation

### **Requirements**
- Python >=3.10 <3.14
- [uv](https://docs.astral.sh/uv/) for dependency management

### **Quick Setup**

```bash
# Install uv if not already installed
pip install uv

# Clone and setup project
cd geo-ai-agent-main
uv sync

# Copy environment template
cp .env.example .env
```

---

## 🔑 Environment Configuration

### **Required Variables**

```bash
# Core LLM Configuration
GEMINI_API_KEY=your_gemini_api_key_here
MODEL=gemini/gemini-2.0-flash-exp

# Bright Data Web Unlocker (Recommended for advanced scraping)
BRIGHT_DATA_API_KEY=your_bright_data_api_key_here
BRIGHT_DATA_ZONE=your_bright_data_zone_here
```

### **Optional Enhancements**

```bash
# SEMrush API (for keyword data and competitive analysis)
SEMRUSH_API_KEY=your_semrush_api_key_here

# Other configurations
LOG_LEVEL=INFO
OUTPUT_DIR=output
```

**📝 Note:** The system includes intelligent fallbacks:
- Without Bright Data: Uses basic web scraping
- Without SEMrush: Skips keyword metrics but continues analysis

---

## 🚀 Usage

### **Method 1: CrewAI Command**
```bash
crewai run
```

### **Method 2: Direct Python Execution**
```bash
python src/ai_content_optimization_agent/main.py "https://your-website.com/page"
```

### **Method 3: Test the Enhanced System**
```bash
python test_enhanced_system.py
```

---

## 📊 Output Files

The system generates comprehensive reports in the `output/` directory:

| File | Content |
|------|---------|
| `comprehensive_optimization_report.md` | Main SEO analysis and recommendations |
| `content_briefing.md` | Content strategy and additions |
| `ai_overview.md` | Google AI Overview analysis |
| `query_fanout.md` | Search query research |
| `briefing_data.json` | Raw analysis data |

---

## 🎯 System Capabilities

### **🔍 Advanced Web Scraping**
- **Bright Data Web Unlocker** for JavaScript-heavy sites
- Extracts full page content (not limited to 2000 characters)
- Handles dynamic content and anti-bot protection
- Fallback to basic scraping if Web Unlocker unavailable

### **📈 SEMrush Integration**
- Search volume and keyword difficulty data
- Cost-per-click (CPC) analysis
- Domain ranking insights
- Competitive keyword research

### **🎯 Intent Classification**
- Categorizes search intent (Informational, Navigational, Transactional, Commercial)
- Confidence scoring for intent predictions
- User behavior pattern analysis

### **🏆 Competitive Intelligence**
- Scrapes top 3 competitor pages
- Content structure analysis (H1, H2s, length)
- Identifies content gaps and opportunities
- Competitive advantage assessment

### **💡 Content Optimization**
- Specific content additions with actual text
- SEO-optimized heading suggestions
- FAQ generation based on user questions
- Call-to-action improvements
- Technical SEO recommendations

### **📊 Comprehensive Reporting**
- Executive summaries with key findings
- Current content audit and scoring
- Keyword and search intent analysis
- Competitive landscape insights
- Prioritized action plans with ROI projections

---

## 🧪 Testing & Validation

Run the comprehensive test suite:

```bash
python test_enhanced_system.py
```

**Test Coverage:**
- ✅ Environment variable validation
- ✅ All agent imports and dependencies
- ✅ Bright Data Web Unlocker connectivity
- ✅ SEMrush API configuration
- ✅ Workflow creation and node validation
- ✅ Sample execution setup

---

## 📋 Implementation Status

| Component | Status | Description |
|-----------|--------|-------------|
| ✅ Bright Data Integration | **Complete** | Advanced web scraping with fallback |
| ✅ SEMrush Integration | **Complete** | Optional keyword data integration |
| ✅ Intent Classification | **Complete** | AI-powered search intent analysis |
| ✅ Competitive Scraping | **Complete** | Top competitor content analysis |
| ✅ Content Topics Extraction | **Complete** | Theme and topic identification |
| ✅ Client Content Analysis | **Complete** | Current content audit and scoring |
| ✅ Content Additions | **Complete** | Specific content improvements |
| ✅ Enhanced Optimizer | **Complete** | Comprehensive optimization reports |
| ✅ Workflow Integration | **Complete** | 13-agent sequential pipeline |

---

## 🛠️ Troubleshooting

### **Common Issues**

**1. Import Errors**
```bash
# Ensure proper Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

**2. API Connectivity**
```bash
# Test individual components
python -c "from src.ai_content_optimization_agent.utils.web_unlocker import BrightDataWebUnlocker; print('Web Unlocker OK')"
```

**3. Missing Dependencies**
```bash
uv sync --all-extras
```

### **Performance Tips**

- **Web Unlocker**: Improves scraping success rate by 90%+
- **SEMrush Data**: Adds keyword volume and competition insights
- **Batch Processing**: Process multiple URLs by modifying the main script

---

## 🔮 Future Enhancements

**Planned Features:**
- 📊 Automated A/B testing recommendations
- 🎨 Visual content optimization suggestions
- 📱 Mobile-first optimization analysis
- 🔗 Advanced internal linking strategies
- 🎯 Personalization recommendations
- 📈 ROI tracking and measurement

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Bright Data** for advanced web scraping capabilities
- **Google Gemini** for AI-powered content analysis
- **SEMrush** for keyword and competitive data
- **LangGraph** for workflow orchestration

---

<p align="center">
  <strong>🚀 Ready to optimize your content? Start with:</strong><br>
  <code>crewai run</code>
</p>