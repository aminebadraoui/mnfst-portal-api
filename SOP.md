# Marketing Angle Finder: How It Works 🚀

Hey there! This document will explain how our Marketing Angle Finder works in simple terms. Think of it as a smart tool that helps you understand what people are talking about online and find interesting marketing ideas!

## What Does It Do? 🤔

The Marketing Angle Finder does three main things:
1. Takes URLs from websites (like Reddit posts) you want to analyze
2. Reads and understands the content from these websites
3. Gives you three types of useful information:
   - Top Keywords: Important words and phrases that keep coming up
   - Key Insights: Main ideas and takeaways from the content
   - Key Quotes: Real examples of what people are saying

## How Does It Work? 🛠️

### 1. Getting the Content (Web Scraping)
- When you give it a URL, it visits the website (like a person would)
- It grabs all the important text from the page
- It cleans up the text by removing unnecessary stuff (like ads or formatting)

### 2. Breaking Down the Content
- The content is usually too big to analyze all at once
- So we break it into smaller chunks (like breaking a book into chapters)
- Each chunk is just the right size for our AI to understand properly

### 3. Analyzing Each Chunk
For each piece of content, our AI looks for:
- Important keywords that people use often
- Main ideas or problems people are talking about
- Real quotes that show what people actually think or feel

### 4. Live Updates
- Instead of waiting until everything is done, you get updates as they happen
- Each time the AI finds something interesting, it shows up on your screen
- This is like getting text messages instead of waiting for a long email

## Special Features 🌟

### Smart Keyword Handling
- If the same keyword appears multiple times, we count it
- We clean up keywords to avoid duplicates (like "back pain" and "Back Pain" are the same)
- We show you where each keyword came from

### Real-time Processing
- You can add multiple URLs at once
- Each URL is processed independently
- You see results appearing as they're found

### Error Handling
- If a website can't be reached, you get a friendly error message
- If part of the analysis fails, the rest continues working
- You're always kept informed about what's happening

## How to Use It 📝

1. **Start**
   - Open the Marketing Angle Finder page
   - You'll see a box where you can enter URLs

2. **Add URLs**
   - Enter one or more URLs you want to analyze
   - Click "Add Another URL" if you want to analyze multiple pages
   - Click the trash icon to remove a URL if you made a mistake

3. **Analyze**
   - Click the "Analyze" button
   - Watch as results appear in real-time in three columns:
     * Left: Top Keywords
     * Middle: Key Insights
     * Right: Key Quotes

4. **Review Results**
   - Keywords show how many times they appear
   - Insights show the main ideas found
   - Quotes show real examples from the content

## Behind the Scenes 🎬

The system uses several cool technologies:
- FastAPI for handling web requests
- GPT-4 for understanding the content
- Server-Sent Events (SSE) for live updates
- Smart algorithms for finding and counting keywords

## Common Questions ❓

**Q: How long does it take to analyze a URL?**
A: It depends on how much content there is, but you start seeing results within seconds!

**Q: Can it analyze any website?**
A: It works best with text-heavy pages like Reddit posts, blog articles, or forum discussions.

**Q: What if a URL doesn't work?**
A: Don't worry! The system will tell you if there's a problem and continue with any other URLs you provided.

## Tips for Best Results 💡

1. Use URLs with good text content (avoid image-only pages)
2. Add multiple related URLs to get better insights
3. Look for patterns in the keywords and insights
4. Pay attention to the actual quotes - they're real customer voices!

Remember: The more URLs you analyze, the better picture you get of what people are saying about a topic! 