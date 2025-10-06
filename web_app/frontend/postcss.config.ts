// Avoid importing types from `postcss-load-config` to prevent
// a build-time dependency on that package's type declarations.
// Use a loosely-typed config so tsc won't error if the package is
// not installed in the environment where type checking runs.
const config: any = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}

export default config
