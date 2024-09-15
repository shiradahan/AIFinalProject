# 💡 **Final Project: AI Models for Camper Preferences**

![Project Cover Image](project_image.jpeg)


---

## Table of Contents
- [The Team](#the-team)
- [Project Description](#project-description)
- [Getting Started](#getting-started)
- [Prerequisites](#prerequisites)
- [Installing](#installing)
- [Testing](#testing)
- [Deployment](#deployment)
- [Built With](#built-with)
- [Acknowledgments](#acknowledgments)

---

## 👥 **The Team**

- **Team Members**  
  - Member 1: [Omer Sarig](omer.sarig@mail.huji.ac.il)
  - Member 2: [Shira Dahan](shira.dahan@mail.huji.ac.il)
  - Member 3: [Noa Benzikry](noa.benzikry@mail.huji.ac.il) 

---

## 📚 **Project Description**

This project was developed as part of the **Introduction to AI** course. It focuses on processing a dataset containing campers' preferences and running various AI models to simulate how those preferences might be optimized. The available models are:

- **Base-line model**  
- **Constraint Satisfaction Problem (CSP)**  
- **Genetic Algorithm**

### Main Features:
- Allows sampling of camper preferences data from the file.
- Runs selected AI models for a specified number of iterations.
- Supports flexible configuration of the number of samples and iterations.

### Main Components:
- Data processing and sampling from campers' preferences.
- Execution of AI models with varying configurations.

### Technologies:
- Python
- Constraint Satisfaction Problem algorithms
- Genetic Algorithms

---

## ⚡ **Getting Started**

To get a copy of the project up and running on your local machine, follow the instructions below.

---

## 🧱 **Prerequisites**

- Python 3.x
- Libraries: 
  - `numpy`
  - `pandas`
  - `argparse`

---

## 🏗️ **Installing**

1. Clone the repository:  
   ```bash
   git clone https://github.com/your-repo/camper-preferences.git
   ```
2. Navigate to the project directory:  
   ```bash
   cd camper-preferences
   ```
3. Install the required dependencies:  
   ```bash
   pip install -r requirements.txt
   ```

---

## 🧪 **Testing**

You can run tests by executing:

```bash
python test_script.py
```

This test will check whether the script correctly samples data, processes the file, and runs the specified AI models for the given number of iterations.

---

## 🚀 **Deployment**

To deploy the project, no special setup is required. Simply run the script on a local machine using the following command format:

```bash
python script.py <filename> [-m MODEL] [-s SAMPLES] [-i ITERATIONS]
```

Where:
- `MODEL` is one of 'base-line', 'csp', or 'genetic'.
- `SAMPLES` is a number between 100 and the total number of campers.
- `ITERATIONS` is a positive integer.

---

## ⚙️ **Built With**

- **Python** - The main language used in development.
- **Genetic Algorithm** - For solving optimization problems.
- **CSP Algorithm** - For solving constraint satisfaction problems.

---

## 🙏 **Acknowledgments**
- Special thanks to the **Introduction to AI** course staff at the Hebrew University.
- Libraries such as `numpy`, `pandas`, and `argparse` played a key role in this project.


