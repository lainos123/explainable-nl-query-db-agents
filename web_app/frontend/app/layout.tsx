import "./globals.css"
// Root layout component for the application

// Main layout function
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen min-w-full box-border antialiased bg-gray-900 text-gray-100" suppressHydrationWarning={true}>
        {children}
      </body>
    </html>
  )
}
