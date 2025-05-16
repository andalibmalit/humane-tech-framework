# Getting Started with Humane Tech Linter

This guide will help you run the Humane Tech Linter on any public or private GitHub repository—even if you're not a developer!

---

## 1. Open a Terminal

### On Mac
- Click the **Spotlight** icon (🔍) in the top right, type `Terminal`, and press Enter.
- ![Open Terminal on Mac](docs/screenshots/open-terminal-mac.png)

### On Windows
- Press the **Windows key**, type `cmd` or `Command Prompt`, and press Enter.
- ![Open Command Prompt on Windows](docs/screenshots/open-terminal-windows.png)

---

## 2. Install Node.js and Git

- Go to [nodejs.org](https://nodejs.org/) and download the LTS version. Install it.
- Go to [git-scm.com](https://git-scm.com/) and download Git. Install it.
- ![Node.js Download](docs/screenshots/nodejs-download.png)
- ![Git Download](docs/screenshots/git-download.png)

---

## 3. Generate a GitHub Personal Access Token

1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Click **Generate new token** (classic)
3. Give it a name (e.g., "Humane Linter")
4. Select the **repo** scope
5. Click **Generate token** and copy it (you won't see it again!)
- ![GitHub Token Steps](docs/screenshots/github-token-steps.png)

---

## 4. Set Your Token as an Environment Variable

### On Mac/Linux
Open your terminal and run:
```sh
export GITHUB_TOKEN=your_token_here
```

### On Windows (Command Prompt)
```cmd
set GITHUB_TOKEN=your_token_here
```

- ![Set Token Mac](docs/screenshots/set-token-mac.png)
- ![Set Token Windows](docs/screenshots/set-token-windows.png)

---

## 5. Run the Linter on a GitHub Repo

In your terminal, run:
```sh
node index.js --github https://github.com/yourusername/your-private-repo
```
- ![Run Linter](docs/screenshots/run-linter.png)

The linter will:
- Download the code
- Scan for dark patterns
- Print results to the terminal
- Save a report as `humane-linter-report.json`
- Clean up after itself

---

## 6. View Results in the Web Viewer

- Open `web-viewer/index.html` in your browser
- Click the file input and select your `humane-linter-report.json`
- See your results in a friendly format!
- ![Web Viewer](docs/screenshots/web-viewer.png)

---

If you get stuck, ask for help or open an issue on GitHub! 