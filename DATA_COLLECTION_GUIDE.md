# Data Collection Guide — API vs. Manual Downloads

Quick reference for which data can be automated and which requires manual collection.

---

## 📊 Summary Table

| Data Source | API Available? | Coverage | Effort | Script Available |
|------------|----------------|----------|--------|------------------|
| **ESS Round 9** | ❌ No (requires account) | 28 countries | 15 min | N/A |
| **Gini, GDP, Unemployment** | Yes (World Bank) | All 28 countries | 5 min | `scripts/fetch_oecd_data.py` |
| **OECD Institutional (EPL, ALMP)** | ⚠️ Partial | 21 OECD members only | 30 min | ⚠️ Partial |
| **ICTWSS (Union, Bargaining)** | ❌ No (Excel download) | 27 countries | 20 min | N/A |
| **AI Exposure Indicators** | ❌ No (multiple sources) | Varies | 1-2 hours | N/A |

---

## Fully Automated (Use Provided Script)

### Basic Economic Indicators

**What:** Gini coefficient, GDP per capita, Unemployment rate

**Coverage:** All 28 ESS countries

**How to Collect:**
```bash
python scripts/fetch_oecd_data.py
```

**Output:**
- `data/external/gini_data_worldbank.csv`
- `data/external/gdp_data_worldbank.csv`
- `data/external/unemployment_data_worldbank.csv`

**Then:** Rename files (remove `_worldbank` suffix) to match expected format

**Time:** ~5 minutes

**Data Source:** World Bank API (broader coverage than OECD, includes all ESS countries)

---

## ⚠️ Partially Automated

### OECD Institutional Indicators (EPL, ALMP, Social Spending)

**What:** Employment protection, active labor market spending, social expenditure

**Coverage:** 21 OECD member countries only

**Missing:** BG, CY, HR, ME, RS, and partially IS (7 countries)

**How to Collect:**

**Option A: API (OECD members only)**
- Requires `pandasdmx` package or complex SDMX queries
- Script template in `scripts/fetch_oecd_data.py` (marked as TODO)

**Option B: Manual Download (Recommended for completeness)**
1. Visit: https://stats.oecd.org/
2. Navigate to: Employment → Employment Protection
3. Download: EPL indicators for all countries, year 2018
4. Repeat for: Social Expenditure Database (SOCX)
5. Compile into `data/external/institutional_data.csv`

**Time:** 30-45 minutes

**Recommendation:** Do manual download to get cleaner data and avoid API complexity

---

## ❌ Manual Download Required

### 1. European Social Survey (ESS) Round 9

**Why Manual:** Requires account creation and terms acceptance

**Steps:**
1. Go to: https://ess.sitehost.iu.edu/
2. Create free account (or log in)
3. Navigate to: Data > Round 9 (2018)
4. Download: Integrated file `ESS9e03_3.dta` (Stata format)
5. Save to: `data/raw/ESS9e03_3.dta`

**Time:** 10-15 minutes (one-time account setup)

**File Size:** ~150 MB

**Alternative for Testing:** Use mock data generator:
```bash
python scripts/create_mock_data.py
```

---

### 2. ICTWSS Database (Union Density, Collective Bargaining)

**Why Manual:** Excel file download only, no API

**Steps:**
1. Visit: https://www.ictwss.org/downloads
2. Download: ICTWSS Database Version 6.1 (or latest)
3. Open Excel file
4. Filter to: Year = 2018
5. Extract columns:
   - `Country` (3-letter code)
   - `UD` → Union density (% of employees)
   - `AdjCov` → Adjusted collective bargaining coverage (%)
6. Convert country codes (ISO3 → ISO2):
   - AUT → AT, BEL → BE, etc.
7. Add to `data/external/institutional_data.csv` (merge with EPL/ALMP data)

**Time:** 15-20 minutes

**Coverage:** 27 of 28 countries (Iceland may be missing some years)

---

### 3. AI/Automation Exposure Indicators

**Why Manual:** Multiple sources, complex aggregation required

**Components:**

**A. OECD AI Exposure Index**
1. Download: OECD Employment Outlook 2023
2. Find: Chapter 3 supplementary data (Excel file)
3. Extract: Country-level AI exposure scores
4. Add column: `ai_exposure_oecd`

**B. Frey & Osborne Automation Risk**
1. Download: Frey & Osborne (2017) appendix
   - Paper: https://www.oxfordmartin.ox.ac.uk/publications/the-future-of-employment/
   - Data: Occupation-level automation probabilities (702 occupations)
2. Download: Eurostat Labor Force Survey (employment by occupation)
   - Link: https://ec.europa.eu/eurostat/web/lfs/data/database
   - Variables: Employment shares by ISCO-08 occupation, 2018
3. Aggregate to country level:
   ```python
   country_automation_risk = weighted_average(
       occupation_probabilities,
       weights=country_employment_shares
   )
   ```
4. Add column: `automation_risk`

**C. Felten, Raj & Seamans Index (Optional)**
1. Download: From Harvard Dataverse or authors' websites
2. Aggregate to country level (same method as Frey & Osborne)
3. Add column: `ai_exposure_felten`

**Final Output:** `data/external/ai_exposure_data.csv`

**Time:** 1-2 hours (most labor-intensive!)

**Recommendation for PhD Application:**
- **Minimum:** OECD AI exposure only (~30 minutes)
- **Better:** OECD + Frey & Osborne aggregated (~2 hours)
- **Optional:** Add Felten et al. as robustness check

**Alternative:** Use placeholder values for proof-of-concept, note as limitation

---

## 🚀 Recommended Workflow

### Phase 1: Get Started Quickly (30 minutes)

1. **Run automated script:**
   ```bash
   python scripts/fetch_oecd_data.py
   ```

2. **Download ESS manually** (account creation + download)

3. **Create mock data for testing:**
   ```bash
   python scripts/create_mock_data.py
   ```
   This lets you test all code immediately!

4. **Test the pipeline:**
   ```python
   from src.data_prep import create_analysis_dataset
   df = create_analysis_dataset()
   print(df.shape)  # Should work!
   ```

**Result:** Functional analysis pipeline in 30 minutes

---

### Phase 2: Add Real Institutional Data (1 hour)

5. ⚠️ **ICTWSS manual download** (20 min)
6. ⚠️ **OECD EPL/ALMP manual download** (30 min)
7. **Merge into** `institutional_data.csv`

**Result:** Notebooks 04 (welfare regime extension) now functional

---

### Phase 3: Add AI Exposure (1-2 hours)

8. ❌ **OECD AI Exposure** from Employment Outlook 2023 (30 min)
9. ❌ **Frey & Osborne aggregation** (1-1.5 hours)
10. **Save to** `ai_exposure_data.csv`

**Result:** Notebook 05 (AI exposure extension) now functional

---

## 💡 Smart Shortcuts

### For Testing/Development
- Use `scripts/create_mock_data.py` to generate synthetic data
- Develop full analysis pipeline without waiting for downloads
- Replace with real data before final analysis

### For Quick PhD Application Portfolio
- **Minimum:** ESS + World Bank automated data (30 min)
  - Gets you notebooks 01-03 (core replication)
- **Better:** + ICTWSS manual download (50 min)
  - Gets you notebook 04 (welfare regime analysis)
- **Best:** + AI exposure indicators (2.5 hours total)
  - Gets you full portfolio with all extensions

### For Publication-Quality Analysis
- All real data, no mock data
- OECD data preferred over World Bank (more consistent methodology)
- Multiple AI exposure measures for robustness
- Total time: ~3-4 hours of data collection

---

## 📂 Expected File Structure

After data collection, you should have:

```
data/
├── raw/
│   └── ESS9e03_3.dta                    # ESS Round 9 (manual)
└── external/
    ├── gini_data.csv                    # World Bank API (automated)
    ├── gdp_data.csv                     # World Bank API (automated)
    ├── unemployment_data.csv            # World Bank API (automated)
    ├── institutional_data.csv           # OECD + ICTWSS (manual)
    └── ai_exposure_data.csv             # Multiple sources (manual)
```

---

## 🔧 Troubleshooting

**Issue: World Bank API returns empty data**
- Some countries may not have data for 2018
- Try year range: 2017-2019
- Check country codes (should be ISO2: 'AT', 'BE', etc.)

**Issue: OECD API is too complex**
- Recommendation: Use manual download from OECD.Stat Explorer
- It's faster and more reliable than fighting with SDMX queries

**Issue: Can't find Frey & Osborne data**
- Original paper: Available at Oxford Martin School website
- Replication data: Check author's personal websites
- Alternative: Use only OECD AI exposure index

---

## ❓ Questions?

**"Do I need ALL the data to test the code?"**
- No! Use `scripts/create_mock_data.py` for testing
- Replace with real data when ready for actual analysis

**"Can I skip AI exposure data?"**
- Yes, if focusing on notebooks 01-04 only
- AI exposure is only needed for notebook 05 (extension)

**"Which data source is most important?"**
- Priority 1: ESS Round 9 (core data, ~15 min)
- Priority 2: Basic economics via World Bank API (~5 min)
- Priority 3: ICTWSS union data (~20 min)
- Priority 4: OECD institutional data (~30 min)
- Priority 5: AI exposure (~2 hours)

**"How long for minimum viable analysis?"**
- ESS + World Bank data = ~20 minutes
- This gets you the core 7-model replication (notebooks 01-03)

---

## 📚 References

**APIs:**
- World Bank: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation
- OECD.Stat: https://stats.oecd.org/

**Manual Downloads:**
- ESS: https://ess.sitehost.iu.edu/
- OECD.Stat Explorer: https://stats.oecd.org/Index.aspx
- ICTWSS: https://www.ictwss.org/
- OECD Employment Outlook: https://www.oecd.org/employment/outlook/

**Papers:**
- Frey & Osborne (2017): https://doi.org/10.1016/j.techfore.2016.08.019
- Felten, Raj & Seamans (2021): https://doi.org/10.1002/smj.3286

---

**Last Updated:** February 2026
**Total Time Investment:** 20 minutes (minimum) to 4 hours (complete)
