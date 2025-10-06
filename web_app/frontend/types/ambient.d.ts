// Ambient module declarations for packages without types in this project
// Keeps TypeScript happy without changing runtime behavior

declare module 'react-syntax-highlighter';
declare module 'react-syntax-highlighter/dist/cjs/styles/prism' {
  export const oneDark: any;
}

declare module 'marked' {
  export const marked: any;
  const _default: any;
  export default _default;
}
