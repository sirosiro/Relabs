# Relabs - 3D Modeling Tool

Relabs is a lightweight, face-based 3D modeling tool written in Python. It focuses on intuitive manipulation of cubic structures with real-time synchronization between a 3D viewport and precise numerical controls.

## ✨ Features

*   **Face-Based Modeling**: Intuitive manipulation of 3D surfaces.
*   **Real-time Synchronization**: Seamless update between the 3D viewport and the numerical control panel.
*   **Precise Control**: Edit vertex coordinates directly with absolute precision.
*   **Visual Aids**: Color-coded coordinate axes gizmo and face highlighting.
*   **Export Support**: Export models to XML with flexible settings (Coordinate systems, Scope).
*   **Architecture**: Built with a robust MVC pattern and strict separation of concerns for maintainability.

## 🛠 Requirements

*   Python 3.8+
*   PySide6
*   PyOpenGL
*   numpy

## 🚀 Installation & Usage

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/Relabs.git
    cd Relabs
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    python main.py
    ```

## 🏗 Architecture

Relabs adheres to a strict "Architecture First" philosophy. The project is structured using a fractal architecture manifest system.

*   **[Core](./Core/)**: Pure data models and geometry logic. Independent of any UI framework.
*   **[UI](./UI/)**: Presentation layer built with PySide6 and OpenGL. Handles user interaction and rendering.
*   **[Service](./Service/)**: Application logic, including selection management and data export.

For more details on the design philosophy and architectural decisions, please refer to the [ARCHITECTURE_MANIFEST.md](./ARCHITECTURE_MANIFEST.md).

## 🤝 Contributing

This project is developed with a unique "AI-Cooperated" workflow.
Please read [DESIGN_PHILOSOPHY.md](./DESIGN_PHILOSOPHY.md) before contributing to understand our core principles and the role of intent-based coding.

---
## Attribution

This project was created with the assistance of
[`CIP`](https://github.com/sirosiro/cip) (Core-Intent Prompting Framework),
a CC BY 4.0 licensed prompt framework for generative AI.
