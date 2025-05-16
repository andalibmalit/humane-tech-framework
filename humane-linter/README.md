# Humane Tech Linter

A CLI tool to scan codebases for dark patterns and other anti-patterns that undermine humane technology. This tool helps developers identify and remove manipulative or harmful UX practices from their products.

## Features
- Scans JavaScript, HTML, and other text files for 50+ dark patterns
- Reports file, line, and pattern detected
- Easy to extend with new rules
- Includes a web viewer for non-technical users

## How to Use

### 1. Prerequisites
- You need [Node.js](https://nodejs.org/) installed to run the CLI tool.

### 2. Run the Linter
- Open a terminal and navigate to the `humane-linter` directory.
- Run the linter on your codebase:
  ```sh
  node index.js <path-to-scan>
  ```
  - Example: `node index.js ../my-project`
- The linter will print results to the console and write a report to `humane-linter-report.json` in the current directory.

### 3. View Results in the Web Viewer
- Open `web-viewer/index.html` in your web browser (no server or build step needed).
- Click the file input and select your `humane-linter-report.json` file.
- The results will be displayed in a user-friendly format.

## Dark Patterns Detected
- Hidden costs
- Forced continuity
- Roach motel
- Privacy Zuckering
- Bait and switch
- Confirmshaming
- Disguised ads
- Misdirection
- Scarcity/urgency manipulation
- Trick questions
- Preselected options
- Friend spam
- Fake social proof
- Obscured unsubscribe
- ...and many more

## Contributing
Add new rules in `rules/dark-patterns.js` and submit a pull request!
