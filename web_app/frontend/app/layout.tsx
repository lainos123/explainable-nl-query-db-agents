// Root layout component for the application

// Font settings (demo)
const css = {
  fontFamily: 'Arial, sans-serif',
  h: '100vh',
  w: '100vw',
  margin: 0,
  padding: 0,
  boxSizing: 'border-box',
};

// Main layout function
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body style={css}>
        {children}
      </body>
    </html>
  )
}
