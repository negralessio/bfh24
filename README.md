# 👨🏽‍💻 Setup Project

1. Clone the repository by running the following command:
   ```shell
   git clone https://github.com/negralessio/bfh24
   ```

2. Navigate to the project root directory by running the following command in your terminal:
   ```shell
   cd bfh24
   ```

3. Create a virtual environment and activate it.
   ```shell
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Install the required packages by running the following command in your terminal:
   ```shell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. (Optional) Install pre-commit to help adhering to code styles and mitigating minor issues
   ```shell
   pre-commit install
   pre-commit run --all-files
   ```