import { render } from "ink";
import App from "./App.js";

// Prevent MaxListenersExceededWarning
process.stdin.setMaxListeners(100);

render(<App />);
