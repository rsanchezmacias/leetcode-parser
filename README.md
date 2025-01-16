# Leetcode Parser

**Leetcode Parser** is a Python-based tool designed to streamline your coding preparation process. It scrapes problem data from Leetcode, including the question title, description, and initial method stub, and automatically generates a starter file in your preferred programming language (`*.py` for Python or `*.swift` for Swift). This eliminates the manual effort of copying problem details and setting up the environment, allowing you to focus entirely on solving the problem.

## Frameworks and Tools Used

This project leverages the following frameworks and libraries:

- **Selenium**: Automates the web browser to navigate Leetcode, select the desired programming language, and extract problem details dynamically.
- **Jinja2**: Manages templates for generating starter files with placeholders for the question's title, description, and initial code stub.
- **PyYAML**: Parses configuration files that manage user preferences, such as directories for storing generated files and browser profiles.

## High-Level Overview of Steps

### 1. Setup and Configuration
- The app begins by loading configurations from a YAML file (`config.yaml`). Settings include:
  - Browser profiles
  - User data directory
  - Directory paths for storing generated files

### 2. Input Validation
- Command-line arguments are used to specify:
  - The Leetcode problem URL
  - The desired programming language
- Input validation ensures:
  - The URL is well-formed
  - The language is supported

### 3. Scraping the Problem
- Using Selenium, the app:
  - Navigates to the Leetcode problem URL.
  - Selects the desired programming language in the code editor.
  - Extracts the problem title, difficulty level, description, and initial code stub.

### 4. Formatting and File Generation
- The scraped data is passed to a formatter that structures the information.
- A new file is generated using Jinja2 templates.
- The file is stored in a directory structure based on the problem's difficulty and title.

### 5. Opening the File
- The generated file is automatically opened in:
  - **Xcode** (for Swift)
  - **Visual Studio Code** (for Python)

## How to Use

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/your-username/leetcode-parser.git
    cd leetcode-parser
    ```

2. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Set Up the Configuration File**:
    - Create a `config.yaml` file in the `resources` directory:
      ```yaml
      config:
        user_data_dir: "/path/to/your/chrome/user/data"
        profile_directory: "Default"
        questions_home_directory: "/path/to/store/questions"
      ```

4. **Run the Script**:
    - Use the command-line arguments to specify the problem URL and language preference:
      ```bash
      python main.py -p https://leetcode.com/problems/two-sum/
      ```

5. **Generated File**:
    - The script will generate a file for the problem and open it in your preferred editor.

