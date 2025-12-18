# Novig Charts Optimization Plan

## Current State
- ✅ Streamlit dashboard with market selection
- ✅ Candidate picker (multi-select)
- ✅ Video settings (duration, FPS, gridlines)
- ✅ Output saves to Downloads folder
- ⚠️ Chart styling needs improvement (user feedback: "not good")

---

## Design Decisions - SELECT WHAT YOU WANT

### 📊 Chart Styling

#### Bar Design
- [ ] **Gradient bars** - Horizontal gradient from dark to bright cyan
- [ ] **Solid color bars** - Single vibrant cyan color
- [ ] **Rounded bars** - Rounded corners on bar ends
- [ ] **Sharp bars** - Square/rectangular bars
- [ ] **Thick bars** - More prominent, chunkier bars
- [ ] **Thin bars** - Sleeker, more minimal bars

#### Glow Effects
- [ ] **Strong glow** - Prominent neon glow around bars
- [ ] **Subtle glow** - Soft, understated glow
- [ ] **No glow** - Clean bars without glow effects

#### Background
- [ ] **Gradient background** - Navy gradient (current)
- [ ] **Solid dark background** - Pure dark navy
- [ ] **Textured background** - Subtle noise/pattern
- [ ] **Vignette effect** - Darker edges, lighter center

#### Typography
- [ ] **Dharma Gothic** - Current bold condensed font
- [ ] **Clean sans-serif** - More modern, readable font
- [ ] **Larger percentages** - Make odds more prominent
- [ ] **Smaller candidate names** - More compact layout

#### Layout
- [ ] **Current layout** - Ranks on left, bars in middle, % on right
- [ ] **No rank badges** - Remove the numbered badges
- [ ] **Percentage inside bars** - Show % inside the bar instead of right side
- [ ] **More vertical spacing** - Spread bars out more
- [ ] **Less vertical spacing** - Tighter, more compact

#### Grid
- [ ] **Dashed gridlines** - Current style
- [ ] **Solid gridlines** - Continuous lines
- [ ] **No gridlines** - Remove grid entirely
- [ ] **Only 50%/100% markers** - Fewer gridlines

---

### 🎬 Animation

#### Speed
- [ ] **Smooth transitions** - Current eased animations
- [ ] **Faster transitions** - Snappier position changes
- [ ] **Slower transitions** - More dramatic movement

#### Effects
- [ ] **Bar racing** - Bars physically move positions (current)
- [ ] **Static positions** - Bars stay in place, only length changes
- [ ] **Highlight leader** - Special effect on #1 position

---

### 🖼️ Branding

#### Logo
- [ ] **Bottom left** - Current position
- [ ] **Bottom right** - Move to right corner
- [ ] **Top corner** - Move to top
- [ ] **Smaller logo** - Less prominent
- [ ] **Larger logo** - More prominent
- [ ] **No logo** - Remove entirely

#### Colors
- [ ] **Cyan theme** - Current (#00d4ff)
- [ ] **Electric blue** - Brighter blue
- [ ] **Teal/mint** - Greener shade
- [ ] **Purple accent** - Different accent color
- [ ] **Multi-color bars** - Different color per candidate

---

### 📱 Dashboard UX

#### Candidate Selection
- [ ] **Current multiselect** - Dropdown with checkboxes
- [ ] **Card grid** - Visual cards to click/select
- [ ] **Drag and drop** - Reorder candidates manually
- [ ] **Search/filter** - Type to filter candidates

#### Preview
- [ ] **Add preview frame** - Show static preview before generating
- [ ] **Thumbnail of last chart** - Display recent output

#### Output
- [ ] **Auto-open video** - Automatically play after generation
- [ ] **Copy to clipboard** - Quick share button
- [ ] **Multiple formats** - Add GIF option

---

## Priority Fixes

### Must Have
- [ ] Fix chart styling based on selections above
- [ ] Ensure candidate names display correctly
- [ ] Smooth animation performance

### Nice to Have
- [ ] Preview before generating
- [ ] Multiple output formats
- [ ] Faster generation time

---

## Instructions

1. **Check the boxes** above for features you want
2. **Uncheck** anything you don't want
3. Save this file
4. I'll implement your selections

**What specifically looks "not good" about the current chart?**
- Bar colors?
- Background?
- Font/text?
- Layout/spacing?
- Animation?
- Something else?

