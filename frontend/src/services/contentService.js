import apiClient from './apiClient';

class ContentService {
  /**
   * Generate content using AI
   */
  async generateContent(data) {
    try {
      const response = await apiClient.post('/content/generate', {
        title: data.title,
        content: data.content,
        tone: data.tone,
        format_type: data.format,
        include_hashtags: data.includeHashtags,
        include_seo: data.includeSEO,
      });
      
      return response.data;
    } catch (error) {
      console.error('Content generation error:', error);
      throw error;
    }
  }

  /**
   * Generate SEO metadata for content
   */
  async generateSEOMetadata(content, title) {
    try {
      const response = await apiClient.post('/content/seo-metadata', {
        content,
        title,
      });
      
      return response.data;
    } catch (error) {
      console.error('SEO metadata generation error:', error);
      throw error;
    }
  }

  /**
   * Get content improvement suggestions
   */
  async getContentSuggestions(content) {
    try {
      const response = await apiClient.post('/content/suggestions', {
        content,
      });
      
      return response.data;
    } catch (error) {
      console.error('Content suggestions error:', error);
      throw error;
    }
  }

  /**
   * Get available content templates
   */
  async getTemplates() {
    try {
      const response = await apiClient.get('/content/templates');
      return response.data;
    } catch (error) {
      console.error('Templates fetch error:', error);
      throw error;
    }
  }

  /**
   * Generate demo content
   */
  async generateDemoContent() {
    try {
      const response = await apiClient.post('/content/demo');
      return response.data;
    } catch (error) {
      console.error('Demo content generation error:', error);
      // Return fallback content if API fails
      return {
        success: true,
        demo_content: `🚀 AI Blog Assistant: Automating the Future of Technical Content

Following up on my goal to build a modular AI-powered innovation lab, I'm excited to introduce the AI Blog Assistant—a tool I built to automate the creation of research summaries, technical blogs, and SEO-ready content.

🧠 Why I Built It
As developers, we spend countless hours digesting technical papers, experimenting, and writing documentation. But sharing our insights publicly often takes a back seat. The AI Blog Assistant solves this by turning structured notes, papers, or ideas into coherent, high-quality blog posts—automatically.

🛠 What It Does
✅ Takes input (bullet points, markdown notes, or PDFs)
✅ Uses GPT to generate summaries, tutorials, or commentary in a chosen tone (explanatory, concise, humorous, etc.)
✅ Automatically embeds key terms, links, and SEO meta-structure
✅ Supports one-click publishing (Notion/Markdown export ready)

📈 Impact on Workflow
✅ Reduced blog creation time by 70%
✅ Enabled daily posting with consistent quality
✅ Increased knowledge retention by forcing structured summarization
✅ Opened the door to multi-language publishing & cross-platform sharing

🌐 Tech Stack
React · GPT API · SEO Schema · Markdown Renderer · Flask Backend (soon to be FastAPI)

Coming soon: integration with arXiv, S2ORC, and image captioning via BLIP

🧩 Part of a Bigger System
This assistant is one module of my broader effort to build plug-and-play tools, including:
📊 AI Stock Sentiment Tracker
🧪 AI-Accelerated DOE for Engineering
🖼 3D MCP Model Generator
🎛 UI Mockup Generator

💬 Let's Share Knowledge Better
I believe tech is best advanced not only by building, but by communicating ideas well. This tool is my attempt to bridge that gap—and I'm happy to open-source it or co-develop it further with researchers, bloggers, and dev teams.

🔗 You can see the project (and others) here: 👉 https://lnkd.in/g2EHhQtd

If this resonates with your work or vision, let's connect.

#AI #BlogAutomation #KnowledgeSharing #MachineLearning #FullStackDevelopment #LLM #SEO #DeveloperTools #OpenSource #InnovationLab #GPT4`,
        metadata: {
          word_count: 250,
          character_count: 1500,
          format: 'linkedin',
          tone: 'professional'
        }
      };
    }
  }

  /**
   * Export content to different formats
   */
  async exportContent(content, format) {
    const exports = {
      markdown: this._exportToMarkdown(content),
      html: this._exportToHTML(content),
      notion: this._exportToNotion(content),
      json: this._exportToJSON(content),
    };

    return exports[format] || content;
  }

  /**
   * Private method to export to Markdown
   */
  _exportToMarkdown(content) {
    // Convert LinkedIn format to Markdown
    let markdown = content
      .replace(/🚀|💡|🔥|✨|🎯|🧠|🛠|📈|🌐|🧩|💬|🔗/g, '') // Remove emojis
      .replace(/^(.+)$/gm, '$1  ') // Add line breaks
      .replace(/✅/g, '- ') // Convert checkmarks to bullet points
      .replace(/#(\w+)/g, '`$1`'); // Convert hashtags to code

    return `# ${content.split('\n')[0].replace(/🚀\s*/, '')}\n\n${markdown}`;
  }

  /**
   * Private method to export to HTML
   */
  _exportToHTML(content) {
    let html = content
      .replace(/\n\n/g, '</p><p>')
      .replace(/\n/g, '<br>')
      .replace(/✅/g, '✓')
      .replace(/#(\w+)/g, '<span class="hashtag">#$1</span>');

    return `<div class="blog-content"><p>${html}</p></div>`;
  }

  /**
   * Private method to export to Notion format
   */
  _exportToNotion(content) {
    // Notion-friendly format
    return content
      .replace(/🚀|💡|🔥|✨|🎯|🧠|🛠|📈|🌐|🧩|💬|🔗/g, '')
      .replace(/✅/g, '☑️')
      .replace(/#(\w+)/g, '`$1`');
  }

  /**
   * Private method to export to JSON
   */
  _exportToJSON(content) {
    const lines = content.split('\n').filter(line => line.trim());
    const title = lines[0].replace(/🚀\s*/, '');
    const sections = [];
    let currentSection = null;

    lines.slice(1).forEach(line => {
      if (line.match(/^[🧠🛠📈🌐🧩💬]/)) {
        if (currentSection) sections.push(currentSection);
        currentSection = {
          title: line.replace(/^[🧠🛠📈🌐🧩💬]\s*/, ''),
          content: []
        };
      } else if (currentSection && line.trim()) {
        currentSection.content.push(line.replace(/✅\s*/, ''));
      }
    });

    if (currentSection) sections.push(currentSection);

    return JSON.stringify({
      title,
      sections,
      hashtags: content.match(/#\w+/g) || [],
      metadata: {
        generated_at: new Date().toISOString(),
        word_count: content.split(' ').length,
        character_count: content.length
      }
    }, null, 2);
  }

  /**
   * Analyze content metrics
   */
  analyzeContent(content) {
    const words = content.split(/\s+/).filter(word => word.length > 0);
    const sentences = content.split(/[.!?]+/).filter(s => s.trim().length > 0);
    const paragraphs = content.split(/\n\s*\n/).filter(p => p.trim().length > 0);
    
    const emojis = content.match(/[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]/gu) || [];
    const hashtags = content.match(/#\w+/g) || [];
    const mentions = content.match(/@\w+/g) || [];
    const links = content.match(/https?:\/\/[^\s]+/g) || [];

    return {
      word_count: words.length,
      character_count: content.length,
      character_count_no_spaces: content.replace(/\s/g, '').length,
      sentence_count: sentences.length,
      paragraph_count: paragraphs.length,
      avg_words_per_sentence: sentences.length > 0 ? Math.round(words.length / sentences.length) : 0,
      avg_sentences_per_paragraph: paragraphs.length > 0 ? Math.round(sentences.length / paragraphs.length) : 0,
      emoji_count: emojis.length,
      hashtag_count: hashtags.length,
      mention_count: mentions.length,
      link_count: links.length,
      readability_score: this._calculateReadabilityScore(words.length, sentences.length),
      engagement_elements: {
        emojis: emojis,
        hashtags: hashtags,
        mentions: mentions,
        links: links,
        questions: (content.match(/\?/g) || []).length,
        exclamations: (content.match(/!/g) || []).length
      }
    };
  }

  /**
   * Calculate simple readability score
   */
  _calculateReadabilityScore(wordCount, sentenceCount) {
    if (sentenceCount === 0) return 0;
    
    const avgWordsPerSentence = wordCount / sentenceCount;
    
    // Simple readability score (higher is better)
    // Based on average sentence length
    if (avgWordsPerSentence <= 15) return 90; // Very easy
    if (avgWordsPerSentence <= 20) return 80; // Easy
    if (avgWordsPerSentence <= 25) return 70; // Fairly easy
    if (avgWordsPerSentence <= 30) return 60; // Standard
    if (avgWordsPerSentence <= 35) return 50; // Fairly difficult
    return 40; // Difficult
  }
}

export default new ContentService();