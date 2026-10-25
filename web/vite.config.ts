import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// base relativa funciona tanto no GitHub Pages (/corridas-futuras-luca/) quanto na Vercel (/).
export default defineConfig({
  base: "./",
  plugins: [react()],
});
