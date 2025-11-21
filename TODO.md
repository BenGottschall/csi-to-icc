# Project TODO

## High Priority

### Data Expansion
- [ ] **Add IBC 2024/2021/2018** (International Building Code)
  - Most commonly used ICC code
  - ~10,000+ sections across all chapters
- [ ] **Add IRC 2024/2021** (International Residential Code)
  - Critical for residential construction
- [ ] **Add IMC 2024/2021** (International Mechanical Code)
- [ ] **Add IECC 2024/2021** (International Energy Conservation Code)

### Manual CSI-to-ICC Mappings
- [ ] **Create expert-verified mappings** for most-used divisions:
  - Division 03: Concrete
  - Division 05: Metals
  - Division 06: Wood, Plastics, and Composites
  - Division 22: Plumbing
  - Division 23: HVAC
  - Division 26: Electrical
  - Division 33: Utilities
- [ ] **Build mapping interface** for construction professionals to contribute
- [ ] **Add relevance scoring** (primary/secondary/reference)

### Search Improvements
- [ ] **Improve keyword matching algorithm**
  - Add synonyms and related terms
  - Weight title matches higher than description matches
- [ ] **Add search history** (per session)
- [ ] **Show "related searches"** based on common patterns
- [ ] **Add autocomplete** for CSI code input

## Medium Priority

### User Features
- [ ] **User accounts** (optional login)
  - Save favorite searches
  - Personal notes on code sections
  - Search history across sessions
- [ ] **Export functionality**
  - PDF reports with CSI code → ICC sections
  - CSV export for spreadsheets
  - Print-friendly format
- [ ] **Comparison view** - Compare code requirements across years (2018 vs 2021 vs 2024)
- [ ] **Mobile app** (React Native or PWA)

### State-Specific Codes
- [ ] **Add state amendments** for top 10 states by population
  - California, Texas, Florida, New York, etc.
- [ ] **State selector** with adopted code version info
- [ ] **Highlight differences** between base ICC and state amendments

### Content Enhancements
- [ ] **Add code context** - Show parent chapter/section hierarchy
- [ ] **Related sections** - "See also" links within ICC codes
- [ ] **Change tracking** - Highlight what changed between code years
- [ ] **Calculation tools** - Built-in calculators for common code requirements

## Low Priority / Future

### Community Features
- [ ] **User-submitted mappings** (with moderation/voting system)
- [ ] **Comments and discussions** on code sections
- [ ] **Expert Q&A forum** for code interpretation questions
- [ ] **Case studies** - Real-world examples of code applications

### Technical Improvements
- [ ] **Full-text search** with PostgreSQL tsvector
- [ ] **Redis caching** for popular queries
- [ ] **Rate limiting** for API endpoints
- [ ] **Analytics dashboard** - Track popular searches, useful data for prioritizing mappings
- [ ] **Elasticsearch** integration for advanced search
- [ ] **GraphQL API** option alongside REST

### Data Science / ML
- [ ] **LLM-assisted mapping suggestions** (GPT-4, Claude, etc.)
  - Generate initial mappings for human review
  - Explain relationships between codes
- [ ] **Semantic search** - Find related codes by meaning, not just keywords
- [ ] **Auto-categorization** - ML model to suggest relevance scores

### Integrations
- [ ] **Browser extension** - Look up codes while browsing specifications
- [ ] **API for CAD software** (AutoCAD, Revit plugins)
- [ ] **Bluebeam integration** - Direct lookup from PDF specs
- [ ] **Procore/PlanGrid integration** - Construction management platforms

## Completed ✅

- [x] Core application (FastAPI backend + Next.js frontend)
- [x] Database schema with 5 tables
- [x] 8,778 CSI MasterFormat 2016 codes loaded
- [x] IPC 2018 fully loaded (1,087 sections)
- [x] Keyword-based fallback search
- [x] Docker deployment setup
- [x] Railway production deployment
- [x] Basic search interface with filters
- [x] Direct links to codes.iccsafe.org

---

## Notes

- **Prioritize user feedback** - Let actual usage patterns guide development priorities
- **Expert validation is critical** - All CSI-to-ICC mappings should be reviewed by licensed professionals
- **Start small** - Better to have accurate mappings for a few divisions than questionable ones for all
- **Consider partnerships** - ICC, CSI, or construction firms might be interested in collaboration
