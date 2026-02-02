# Development Guidelines

## Architecture and Async

- Implement full support for async/await by integrating the qasync library (essential for API calls or I/O without blocking the interface).
- Use the Worker Objects approach for heavy tasks, ensuring the Main Thread remains fluid at 60fps.
- Structure the code with clear separation: Main Window Class, Styles Class, and Logic/Worker Class.
- use @slot(), and QueuedConnection com asyncSlot

## Modern Visual Design (Flat UI)

- Create a Responsive Dark Mode and light Mode design inspired by the Visual Studio Code or Spotify look.
- Use Advanced QSS:
  - Define a color dictionary (Primary, Secondary, Background, Surface, Error)
  - Apply the color dictionary via Qt Style Sheets
  - Implement rounded borders (border-radius: 8px)
  - Create smooth :hover and :pressed effects
  - Use generous padding and typography (e.g., 'Segoe UI' or 'Inter')
- The interface should adapt dynamically to different window sizes (use QGridLayout and setStretch)

## Error Handling and Feedback

- Implement a Robust Exception Handling system:
  - Each asynchronous operation should have a try-except that captures the error and sends it to the UI via Signals
- Create a visual Notification (Toast) component or a dynamic status bar to show errors and successes to the user without interrupting the flow
- Include a QProgressBar or QProgressIndicator that activates automatically during asynchronous processes

## Features and Components

- Use modern slot syntax (e.g., @Slot())
- Create a Dashboard, Sidebar, Navbar, and footer with progressbar

## Code Delivery

- Generate modular, clean, and documented code following PEP 8
- Include a comments section at the top with the required dependencies (poetry install PySide6 qasync)

## UI/UX Advanced Guidelines

### Atomic Componentization (Design System)

- Create a library of reusable base widgets (e.g., `TecnButton`, `TecnLineEdit`, `TecnCard`) to ensure visual consistency across the entire application.
- Centralize style properties within these components to allow global UI updates from a single source.

### Navigation and Routing

- Implement a central `Navigator` class to manage `QStackedWidget` transitions.
- Decouple view logic from navigation logic to allow screen switching from any part of the application without direct class coupling.

### Visual Validation Feedback

- Integrate input fields directly with Pydantic `Schemas`.
- Implement real-time visual feedback (e.g., dynamic red borders, error tooltips) that triggers immediately when validation fails.
- Use a debounce mechanism for input validation to ensure the UI remains fluid during typing.

### High DPI Support and SVG Icons

- Enable automatic High DPI scaling to support 4K monitors and various OS scale factors.
- Use **SVG** format exclusively for all icons to ensure crisp, resolution-independent visuals.

### Accessibility and Productivity

- Define standard keyboard shortcuts for common actions (e.g., `Ctrl+N` for New, `Ctrl+F` for Search, `Esc` for Cancel).
- Enforce a logical `Tab Order` in all forms to facilitate efficient keyboard-only navigation.

### Asset Management (Qt Resource System)

- Utilize `.qrc` files to compile icons, custom fonts, and QSS into Python modules.
- Ensure all assets are embedded to prevent "file not found" errors during deployment.
