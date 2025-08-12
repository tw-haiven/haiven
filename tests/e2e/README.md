# End-to-End Tests Documentation

## Overview

This directory contains comprehensive end-to-end tests for the Haiven application, including tests that verify the nuanced behavior of different user workflow patterns.

## Key Test Files

### Context and Document Selection Patterns
**File**: `context-document-selection-patterns.spec.ts`

This test suite serves as **living documentation** for the intentional design decisions around context and document selection across different page types. It verifies four distinct user workflows:

#### 1. 📄 Information Retrieval (`/knowledge-chat`)
- **Pattern**: Document selection only
- **Use Case**: Finding information in documentation
- **Optimization**: Search accuracy over speed
- **Test**: Verifies "Select document" visible, "Select your context" hidden

#### 2. 🎯 Expert-Assisted Work (`/chat?prompt=<id>`)
- **Pattern**: Both context AND document selection
- **Use Case**: Professional work with AI guidance + supporting materials
- **Optimization**: Work output quality with comprehensive support
- **Test**: Verifies both "Select your context" AND "Select document" visible

#### 3. 💡 Creative Ideation (`/cards?prompt=<id>`)
- **Pattern**: Context selection only
- **Use Case**: Rapid brainstorming and idea generation
- **Optimization**: Creative flow speed over factual accuracy
- **Test**: Verifies "Select your context" visible, "Select document" hidden

#### 4. 🛠️ Specialized Tools (`/creative-matrix`, `/scenarios`)
- **Pattern**: Neither selection (custom interfaces)
- **Use Case**: Interactive tools with specialized parameters
- **Optimization**: Tool-specific workflows
- **Test**: Verifies neither selection type visible

## Business Value of These Tests

### 1. **Prevents Feature Regression**
- Ensures workflow-specific optimizations don't get accidentally "fixed"
- Protects against well-meaning but misguided "consistency" changes

### 2. **Documents Design Intent**
- Makes implicit design decisions explicit and testable
- Helps new team members understand the rationale

### 3. **Validates User Experience**
- Each workflow is optimized for different success metrics
- Tests ensure users get the right tools for their intended tasks

### 4. **Supports Product Decisions**
- Provides concrete evidence that different pages serve different purposes
- Helps justify why "missing" features are actually intentional omissions

## Environment Configuration

The tests are now configured to run against three different environments:

### 1. Local Development Environment
- **URL**: `http://localhost:8080`
- **Project**: `local`
- **Features**: Automatically starts the application

### 2. Demo Environment  
- **URL**: `https://team-ai-owd2wjctzq-uc.a.run.app`
- **Project**: `demo`
- **Requirements**: Authentication required (one-time setup)

### 3. Production Environment
- **URL**: `https://haiven.thoughtworks-labs.net`
- **Project**: `prod`
- **Requirements**: Authentication required (one-time setup)

## Running the Tests

```bash
# Environment-specific tests
npm test                     # Default: runs all tests
npm run test:local          # Local development environment
npm run test:demo           # Demo environment
npm run test:prod           # Production environment

# Development & debugging
npm run test:headed         # Run with visible browser
npm run test:debug          # Debug mode
npm run test:ui             # Interactive UI mode
npm run test:report         # View last test report

# Setup
npm run setup               # Install dependencies
```

### Authentication Setup (One-time)

**Status**: 
- ✅ **Demo environment**: Already authenticated and ready to use
- ⚠️  **Production environment**: Requires authentication setup

#### Authentication Setup Commands
```bash
# Set up production environment authentication
npm run auth:prod

# Set up demo environment authentication  
npm run auth:demo
```

**How it works:**
1. Opens Chrome browser to the target environment URL
2. Waits for you to complete Okta authentication
3. Saves the authentication state for future test runs

**Note**: 
- Authentication files are stored in `playwright/.auth/` and will be reused until they expire
- Both commands use the same underlying script (`setup-auth.js`) with different parameters
- You can also run directly: `node setup-auth.js demo` or `node setup-auth.js prod`

## Test Philosophy

These tests follow the principle that **different user intents require different UI patterns**:

- **Progressive Complexity**: Simple tasks get simple UIs
- **Workflow Optimization**: Each page type maximizes its primary use case success
- **Cognitive Load Management**: Don't overwhelm users with irrelevant options

## Expected Test Results

When these tests pass, they confirm:

✅ **Knowledge Chat**: Users focused on information retrieval get streamlined document search  
✅ **Guided Prompts**: Users doing complex work get both expert guidance and supporting materials  
✅ **Cards Generation**: Users in creative mode get inspiration without factual constraints  
✅ **Custom Tools**: Users get specialized interfaces without generic chat overhead  

## If Tests Fail

If these tests start failing, it likely means:

❌ Someone "unified" the UI patterns (breaking workflow optimization)  
❌ A component refactor accidentally changed the rendering logic  
❌ New features were added without considering workflow-specific needs  

**Before "fixing" these tests**, consider whether the change improves the specific workflow the page is designed for, rather than just making it consistent with other pages.

## Related Documentation

- `/ui/src/pages/knowledge-chat.js` - Document-only configuration
- `/ui/src/pages/chat.js` - Both-selections configuration  
- `/ui/src/pages/cards.js` - Context-only configuration
- `/ui/src/app/_prompt_chat.js` - Main component with conditional rendering
- `/ui/src/pages/_cards-chat.js` - Cards-specific component

## Future Considerations

As the application evolves, consider:

1. **New Workflow Types**: Should they follow existing patterns or need new ones?
2. **User Research**: Do the workflow optimizations match actual user behavior?
3. **Performance Metrics**: Are we measuring the right success criteria for each workflow?
4. **A/B Testing**: Could we test whether users prefer consistency vs. optimization?