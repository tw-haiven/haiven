# Haiven E2E Tests

End-to-end Playwright tests for the Haiven application.

## Quick Start

```bash
# From repository root
cd tests

# Setup
./run-e2e-tests.sh setup

# Run all tests
./run-e2e-tests.sh run

# Run with UI
./run-e2e-tests.sh run ui
```
# Haiven E2E Test Coverage Documentation

## Test Status
The Playwright tests are currently running but experiencing some timeout issues during execution. The test suite contains 74 tests across 7 test files, running on both Chromium and Firefox browsers.

## Test Suite Overview

### 1. Core Application Navigation (`haiven.spec.ts`)
**Coverage:** Basic application functionality and user flows
- **Main Page Loading:** Verifies the home page loads with correct elements
- **Navigation:** Tests navigation to About, Knowledge Overview, and API Keys pages
- **Sidebar Navigation:** Tests expanding Research menu and Ideate submenu interactions
- **Chat Interactions:** Tests document tabs in Knowledge Overview and chat message functionality

### 2. Card System Tests (`haiven-card-tests.spec.ts`)
**Coverage:** Core card generation and enrichment functionality
- **Navigation:** Tests navigation to Requirements Breakdown page
- **Card Generation:** Tests initial card generation with valid user input
- **Individual Card Controls:** Tests card interaction buttons and dialogs
- **Copy Functionality:** Tests "COPY ALL" button functionality
- **Card Enrichment:** Tests multiple enrichment options:
  - BDD Scenario enrichment
  - "What might fail" scenario enrichment
  - Custom input enrichment
- **UI State Management:** Tests button state changes after enrichment
- **Warning Messages:** Verifies enrichment warning messages are displayed

### 3. Cards Exploration (`cards-exploration.spec.ts`)
**Coverage:** Card functionality across different application pages
- **STRIDE Page:** Tests threat modeling card generation and interactions
- **Requirements Breakdown:** Tests requirements analysis card generation
- **Fitness Functions:** Tests fitness function brainstorming cards
- **Sample Input Functionality:** Tests sample input dialogs and copy functionality
- **Card Interactions:** Tests card buttons and dialog interactions

### 4. Pinboard System (`pinboard.spec.ts`)
**Coverage:** Content management and persistence (US-001)
- **Dialog Management:** Tests pinboard modal open/close functionality
- **Content Addition:** Tests adding notes and context to pinboard
- **Content Viewing:** Tests viewing pinned content across different tabs
- **Data Validation:** Tests form validation for required fields
- **Persistence:** Tests localStorage persistence across browser sessions
- **Chat Integration:** Tests using pinboard content in chat contexts

### 5. Creative Matrix (`creative-matrix.spec.ts`)
**Coverage:** Matrix generation and customization (US-002)
- **Parameter Configuration:** Tests matrix parameter setup and validation
- **Row/Column Customization:** Tests custom matrix dimensions and labels
- **Content Generation:** Tests matrix generation with different inputs
- **Custom Prompts:** Tests additional prompting functionality
- **Output Validation:** Tests matrix structure and content validation
- **UI Interactions:** Tests all interactive elements and controls

### 6. Client Research Sources (`client-research-sources.spec.ts`)
**Coverage:** Source verification and citation functionality
- **Company Overview:** Tests mandatory source links in company research
- **AI Tools Configuration:** Tests source generation with AI tools config
- **Ideas to Pitch:** Tests source links in pitch generation
- **Source Validation:** Verifies proper URL formatting and link validity

### 7. Scenario Design (`scenario-design.spec.ts`)
**Coverage:** Basic scenario design functionality
- **Page Navigation:** Tests navigation to scenario design page
- **UI Elements:** Verifies presence of essential UI components
- **Form Elements:** Tests scenario parameter inputs and controls

## Key Testing Patterns

### Test Utilities (`test-utils.ts`)
The test suite includes sophisticated utility functions:
- **Modal Dismissal:** Automatic handling of disclaimer modals
- **Streaming Detection:** Smart waiting for AI content generation completion
- **Element Stability:** Ensures UI elements are stable before interaction
- **Fallback Mechanisms:** Robust timeout handling with fallback strategies

### Browser Coverage
- **Chromium:** 37 tests
- **Firefox:** 37 tests
- **Total:** 74 tests across both browsers

### Configuration
- **Timeouts:** 60-second test timeout with 30-second action/navigation timeouts
- **Retries:** 1 retry locally, 2 in CI
- **Workers:** Limited to 2 parallel workers to reduce system load
- **Screenshots/Videos:** Captured on failure for debugging

## Important Areas Covered

### Security & Authentication
- API key page navigation
- User authentication flows

### AI Content Generation
- Card generation across multiple domains (threat modeling, requirements, fitness functions)
- Content enrichment with various prompts
- Source citation and verification
- Creative matrix generation with custom parameters

### User Experience
- Modal and dialog interactions
- Form validation and error handling
- Content persistence and state management
- Cross-browser compatibility

### Data Management
- Local storage persistence
- Content copying and export functionality
- Pinboard content management

## Test Quality Features
- **Robust Selectors:** Uses multiple selector strategies for reliability
- **Content Validation:** Verifies substantial content generation rather than just presence
- **State Management:** Tests UI state changes and button enabling/disabling
- **Error Handling:** Includes timeout and fallback mechanisms
- **Cross-Page Testing:** Tests functionality across different application pages
