# 8086 Compiler

<!-- PROJECT LOGO -->
<br />
<p align="center">
  

  <h3 align="center">8086 Compiler</h3>
  
<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
        <li><a href="#features">Features</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
    </li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project
8086-Compiler
This is a graphical user interface (GUI) for the 8086 compiler. It allows users to write and compile Assembly code for the 8086 microprocessor using a user-friendly interface.

### Built With
Python - Libraries( Streamlit, numpy, pandas)

### Features
Code Editor : Any Code Editor can be used for seeing Code (I have used VS Code).

**_Instruction Implemented_ :**
  <p>
  <li>ADD, SUB, MUL, DIV (Arithmetic Instruction) <br/></li>
  <li>AND, OR, XOR, NOT, NEG (Logical Instruction)  <br/></li>
  <li>MOV  <br/></li>
 <li> CMC, STC, CLC, STD, CLD, etc (Flag Instruction) <br/></li>
  <li>SHL, SHR, SAR, SAL (Shift Instructions) <br/></li>
  <li>ROR, ROL, RCL, RCR (Rotate Instructions) <br/></li>

All the Instruction are implemented using concept of Modular Programming, also NONE of the external Libraries are used to perform operations. All the above mentioned instructions are implemented by using own functions. By using Libraries we can minimize the code size but the internal function complexity will be same, so I have implemented all the function at my own and also it has been implemented by keeping in mind the working of 8086 microprocessor Compiler Execution.
</p>

**_Modular Programming_** :
If I want to implement 16-bit Addition Operation the it can be done by using the 1-bit addition function and if I want to do 8-bit addition then also it can be done by 1-bit addition function.


### Getting Started
This is an example of how you may give instructions on setting up your project locally.
To use the 8086 Compiler GUI, follow these steps:

<ul>
  <li>Download the code from Github by clicking the "Download" button or by cloning the repository using Git.</li>
  <li>Install python compiler (any version after 3.7)</li>
  <li>Install Libraries such as streamlit, numpy, pandas, base64 and re.</li>
  <li>Open the Command Prompt and move to the folder where file is located.</li>
  <li>Write the command "streamlit run 8086_Compiler.py"</li>
  <li>Now type the program in Code Section (Text Editor)</li>
  <li>After writing program , Click on Compile Button to compile the program.</li>
  <li>Now you can check Register values and Machine Code of your assembly instructions.</li>
  <li>You will get machine code by a seperate machine_code.txt file in your folder. </li>
</ul>


### Contact
If you have some suggestions related to the code, you can contact me on
<p>Email : suayush.04@gmail.com <br/> LinkedIn : https://www.linkedin.com/in/ayush-sutariya04/</p>

