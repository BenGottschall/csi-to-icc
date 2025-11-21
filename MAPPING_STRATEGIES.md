# CSI-to-ICC Mapping Strategies

This document outlines different approaches for creating mappings between CSI MasterFormat codes and ICC code sections.

> **Status Update (Nov 2025):** Option 1 (Keyword Matching) has been implemented and is live in production at [csimap.up.railway.app](https://csimap.up.railway.app/). User feedback indicates it works surprisingly well as a baseline!

## Current Data
- **CSI Codes**: 8,778 codes (MasterFormat 2016) ✅ Loaded
- **ICC Sections**: 1,087 IPC 2018 sections ✅ Loaded
- **Search Method**: Keyword matching (fallback when no manual mappings exist) ✅ Implemented
- **Next Goal**: Add IBC, IRC, IMC codes and create expert-validated mappings

---

## Strategy Options

### 🟢 FREE Options

#### Option 1: Pure Keyword Matching
**Cost**: $0
**Quality**: Medium (70-80% useful)
**Speed**: Very fast (<100ms per search)

**How it works:**
1. Extract keywords from CSI code title
2. Search ICC section titles and descriptions
3. Rank by keyword overlap (TF-IDF, cosine similarity)
4. Return top N matches

**Pros:**
- Zero cost
- Fast
- Runs entirely locally
- No external dependencies
- Works offline

**Cons:**
- Misses semantic relationships
- Can't understand context
- May return irrelevant matches with keyword overlap

**Implementation:**
- Python libraries: `scikit-learn`, `nltk`, or `spaCy`
- Store results in database
- Can be enhanced with synonym expansion

**Status**: ✅ Recommended as baseline (implement first)

---

#### Option 2: Local Open-Source LLM (Ollama)
**Cost**: $0
**Quality**: Good (85-90% useful)
**Speed**: Slow (5-30 seconds per mapping)

**How it works:**
1. Install Ollama locally
2. Download model (Llama 3.1, Mistral, etc.)
3. Prompt: "Which IPC sections relate to: [CSI code title]?"
4. Parse response and create mappings
5. Store results permanently

**Pros:**
- Zero ongoing cost
- Good quality with 7B+ models
- Complete privacy (all local)
- No rate limits

**Cons:**
- Slower processing
- Requires decent hardware (but works on laptops)
- Initial setup time
- Large disk space for models (~4-8GB)

**Setup:**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Download model
ollama pull llama3.1:8b

# Use in Python
pip install ollama
```

**Status**: ⏳ Good option for batch processing all codes overnight

---

### 💰 ULTRA-LOW COST Options ($1-10)

#### Option 3: Hybrid - Keywords + Claude Haiku Batch
**Cost**: $3-8 one-time
**Quality**: Excellent (90-95% useful)
**Speed**: Fast for users (pre-computed)

**How it works:**
1. **Phase 1**: Keyword matching for obvious cases (80% of codes)
   - High keyword overlap = confident match
   - Store these mappings
2. **Phase 2**: Claude Haiku API for ambiguous cases (20% of codes)
   - Low keyword overlap or unclear matches
   - LLM provides context-aware suggestions
3. Run ONCE, store all results in database

**Cost Breakdown:**
- Claude Haiku: $0.25/1M input tokens, $1.25/1M output tokens
- Estimate for 8,778 codes:
  - ~500 tokens input per code
  - ~200 tokens output per code
  - Only process ~20% with LLM (~1,756 codes)
  - **Total: ~$3-6 one-time**

**Pros:**
- High quality mappings
- One-time cost
- Best quality-to-cost ratio
- Results are instant for users

**Cons:**
- Requires Anthropic API key
- Small upfront cost

**Implementation:**
```python
# Pseudo-code
for csi_code in all_csi_codes:
    keyword_matches = keyword_search(csi_code)

    if keyword_matches.confidence > 0.8:
        # High confidence - use keyword results
        save_mappings(keyword_matches)
    else:
        # Low confidence - use LLM
        llm_result = claude_haiku_api(csi_code, icc_sections)
        save_mappings(llm_result)
```

**Status**: 🎯 Best bang-for-buck option

---

#### Option 4: On-Demand Haiku with Caching
**Cost**: $0 upfront, ~$0.50 per 100 searches, max $5 over first few months
**Quality**: Excellent (90-95% useful)
**Speed**: First search slow (2-5s), cached searches instant

**How it works:**
1. User searches for CSI code
2. Check if mapping exists in database
3. If not: Call Claude Haiku API
4. Cache result permanently
5. Future searches for same code = instant (cached)

**Cost Progression:**
- First 100 unique searches: ~$0.50
- First 1,000 unique searches: ~$3-5
- After that: Nearly free (most codes cached)
- Only pay for codes users actually search

**Pros:**
- Zero upfront cost
- Pay-as-you-grow model
- Only pay for codes users care about
- Can start testing immediately

**Cons:**
- First search on any code is slower
- Costs accumulate over time (but cap at ~$5-10)

**Implementation:**
```python
@api.post("/search")
def search_csi_code(csi_code: str):
    # Check cache
    cached_mapping = db.get_mapping(csi_code)
    if cached_mapping:
        return cached_mapping

    # Not cached - use LLM
    llm_result = claude_haiku_api(csi_code)
    db.save_mapping(llm_result)
    return llm_result
```

**Status**: 🎯 Excellent for MVP/testing phase

---

### 💰 MEDIUM COST Options ($10-20)

#### Option 5: Keyword + GPT-4o-mini Refinement
**Cost**: $8-12 one-time
**Quality**: Excellent (92-96% useful)
**Speed**: Fast (pre-computed)

**How it works:**
- Keyword matching finds candidate ICC sections
- GPT-4o-mini ranks and refines the candidates
- Adds reasoning for why each mapping is relevant
- Batch process all codes once

**Cost Breakdown:**
- GPT-4o-mini: $0.15/1M input tokens, $0.60/1M output tokens
- All 8,778 codes: ~$8-12 one-time

**Pros:**
- Slightly better quality than Haiku
- Still very affordable
- Good for detailed explanations

**Cons:**
- More expensive than Haiku for similar quality
- OpenAI API required

**Status**: ⏸️ Consider if you prefer OpenAI ecosystem

---

### 💸 HIGHER COST (Outside Budget)

#### Option 6: Full GPT-4 Batch Processing
**Cost**: $40-80 one-time
**Quality**: Best possible (95-98% useful)

Premium quality with GPT-4, but exceeds $20 budget. Consider for future if budget increases.

**Status**: ❌ Outside current budget

---

## Recommended Implementation Plan

### Phase 1: Baseline (FREE) ✅
**Implement Now:**
1. **Keyword Matching System**
   - Build text similarity search
   - Create ranking algorithm
   - Test with sample codes
   - Use this as fallback for all approaches

**Timeline**: 1-2 hours
**Cost**: $0

---

### Phase 2: Choose Enhancement (OPTIONAL)

**If budget = $0:**
- Add **Local LLM (Ollama)** for better results
- Run batch processing overnight
- Cost: $0, Time: Setup (1 hour) + Processing (overnight)

**If budget = $3-8:**
- Implement **Hybrid Keywords + Haiku Batch (Option 3)**
- Best quality-to-cost ratio
- One-time cost, permanent results
- Cost: ~$5, Time: 2-3 hours setup + 1-2 hours processing

**If budget = $0 but want flexibility:**
- Implement **On-Demand Haiku (Option 4)**
- Start free, pay-as-you-grow
- Perfect for MVP testing
- Cost: Starts at $0, Time: 1-2 hours setup

---

## Decision Matrix

| Option | Cost | Quality | Speed | Complexity | Best For |
|--------|------|---------|-------|------------|----------|
| 1. Keywords Only | $0 | 70% | Instant | Low | Baseline/MVP |
| 2. Local LLM | $0 | 85% | Slow | Medium | Budget constraint |
| 3. Hybrid Batch | $5 | 90% | Instant | Medium | **Best overall** |
| 4. On-Demand | $0-5 | 90% | Mixed | Low | MVP testing |
| 5. GPT-4o-mini | $10 | 92% | Instant | Medium | Quality focus |
| 6. Full GPT-4 | $50 | 95% | Instant | Medium | Outside budget |

---

## Current Status

- [ ] Phase 1: Keyword matching (in progress)
- [ ] Phase 2: Choose enhancement strategy
- [ ] Phase 3: Implement chosen strategy
- [ ] Phase 4: User testing and refinement

---

## Notes

- All costs are estimates and may vary based on actual usage
- Anthropic API key required for Options 3-4
- OpenAI API key required for Options 5-6
- Keyword matching will be useful regardless of which enhancement is chosen
- Can always upgrade strategy later (keyword → LLM → better LLM)

---

## Future Enhancements

Once basic mapping is working:
- User-submitted mappings
- Voting/rating system
- Expert verification workflow
- Community moderation
- Mapping confidence scores
- Multiple mapping types (primary, secondary, reference)
