import nextCoreWebVitals from "eslint-config-next/core-web-vitals.js";
import nextTypescript from "eslint-config-next/typescript.js";
import { dirname } from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// eslint-config-next exports are CommonJS, so we need to access the config property
const coreWebVitalsConfig = nextCoreWebVitals.config || nextCoreWebVitals;
const typescriptConfig = nextTypescript.config || nextTypescript;

const eslintConfig = [...coreWebVitalsConfig, ...typescriptConfig, {
  rules: {
    // TypeScript rules - core enabled, permissive on edge cases
    "@typescript-eslint/no-explicit-any": "warn",
    "@typescript-eslint/no-unused-vars": ["warn", { "argsIgnorePattern": "^_", "varsIgnorePattern": "^_" }],
    "@typescript-eslint/no-non-null-assertion": "warn",
    "@typescript-eslint/ban-ts-comment": "warn",
    "@typescript-eslint/prefer-as-const": "off",
    "@typescript-eslint/no-unused-disable-directive": "off",

    // React rules
    "react-hooks/exhaustive-deps": "warn",
    "react-hooks/purity": "warn",
    "react/no-unescaped-entities": "off",
    "react/display-name": "off",
    "react/prop-types": "off",
    "react-compiler/react-compiler": "off",

    // Next.js rules
    "@next/next/no-img-element": "warn",
    "@next/next/no-html-link-for-pages": "off",

    // General JavaScript rules - core safety enabled
    "prefer-const": "warn",
    "no-unused-vars": "off", // Covered by @typescript-eslint/no-unused-vars
    "no-console": "off",
    "no-debugger": "warn",
    "no-empty": "warn",
    "no-irregular-whitespace": "error",
    "no-case-declarations": "off",
    "no-fallthrough": "warn",
    "no-mixed-spaces-and-tabs": "error",
    "no-redeclare": "error",
    "no-undef": "error",
    "no-unreachable": "error",
    "no-useless-escape": "warn",
  },
}, {
  ignores: ["node_modules/**", ".next/**", "out/**", "build/**", "next-env.d.ts", "examples/**", "skills"]
}];

export default eslintConfig;
