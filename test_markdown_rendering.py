#!/usr/bin/env python3
"""
Test markdown rendering with AI responses
"""

# Sample markdown response that the AI might generate
sample_markdown_response = """
# Understanding Artificial Intelligence

Artificial Intelligence (AI) is revolutionizing how we work and live. Below is a comprehensive guide to understanding AI.

## What is AI?

**Artificial Intelligence** refers to machines that can perform tasks that typically require human intelligence. These include:

1. **Learning** - improving from experience
2. **Reasoning** - solving problems
3. **Perception** - understanding visual/audio information
4. **Language** - understanding and generating text

## Types of AI

### Narrow AI (Weak AI)
- Designed for specific tasks
- All current AI systems are narrow AI
- Examples: ChatGPT, image recognition, chess engines

### General AI (Strong AI)
- Hypothetical AI with human-level intelligence
- Can learn and apply knowledge across domains
- Does not exist yet

## How AI Works

The basic process involves three steps:

1. **Data Collection** - Gather large amounts of training data
2. **Model Training** - Use algorithms to find patterns
3. **Prediction/Decision** - Apply learned patterns to new data

> "The real revolution isn't in the intelligence of these machines, it's in our willingness to use them." - Anonymous

## Common AI Techniques

### Machine Learning
```python
# Simple example
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
```

### Deep Learning
- Uses neural networks with multiple layers
- Excellent for images, text, and complex patterns
- Requires large amounts of data

### Natural Language Processing (NLP)
- Enables machines to understand human language
- Used in chatbots, translation, sentiment analysis

## Benefits and Risks

| Aspect | Benefit | Risk |
|--------|---------|------|
| Healthcare | Early disease detection | Privacy concerns |
| Business | Increased efficiency | Job displacement |
| Education | Personalized learning | Bias in algorithms |

## Conclusion

AI is a powerful technology that's transforming multiple industries. As we continue to develop AI systems, it's crucial to:

- Ensure **fairness** and **transparency**
- Address **privacy** concerns
- Consider **ethical** implications

For more information, visit [AI Research Resources](https://example.com).

---

*Last updated: February 5, 2026*
"""

if __name__ == "__main__":
    print("Sample Markdown Response for AI:")
    print("=" * 80)
    print(sample_markdown_response)
    print("=" * 80)
    print("\nThis markdown will be rendered with:")
    print("✓ Proper headings (H1, H2, H3)")
    print("✓ Bold and italic text")
    print("✓ Numbered and bulleted lists")
    print("✓ Code blocks with syntax highlighting")
    print("✓ Blockquotes with styling")
    print("✓ Tables with alternating row colors")
    print("✓ Links that open in new tabs")
    print("✓ Horizontal dividers")
